from imports import *

from Classifier import *

class Query(Classifier):
    def __init__(self, file):
        self.file = file
        self.df = pd.read_csv(f'datasets/{self.file}.csv')
        self.stopwords=stopwords.words('english')
        #checks for existing dtm
        if not os.path.exists(f'models/{self.file}.joblib'):
            self.create_dt_matrix()
        self.vectorizer=joblib.load(f'models/vectorizers/{self.file}.joblib')
        self.clf = joblib.load(f'models/{self.file}.joblib')
        self.answers = joblib.load(f'models/responses/{self.file}.joblib')

        #loads the models
        self.vectorizer = joblib.load(f'models/vectorizers/{file}.joblib')
        self.dtm = joblib.load(f'models/{file}.joblib')

    def answer_lists(self):
        questions = set(self.df['Question'].values)
        answers_as_lists=[]
        for q in questions:
            answers_as_lists.append((q,self.df[self.df['Question']==q]['Answer'].values))
        return pd.DataFrame(answers_as_lists,columns=['Question','Answers'])


    def create_dt_matrix(self):
        vectorizer = TfidfVectorizer(sublinear_tf=True, use_idf=True, lowercase=True, stop_words=self.stopwords, ngram_range=(1,3))
        #convert the answers to lists of answers
        df = self.answer_lists()
        #preprocessing
        questions = df['Question'].values
        answers = df['Answers'].values
        docs = self.lemmatize(questions)
        #augment
        aug_df = self.augment(docs,answers)
        docs= aug_df['Utterance']
        matrix = vectorizer.fit_transform(docs)
        #save
        joblib.dump(matrix, f'models/{self.file}.joblib')
        joblib.dump(vectorizer, f'models/vectorizers/{self.file}.joblib')
        joblib.dump(aug_df['Intent'], f'models/responses/{self.file}.joblib')

    def answer(self, input):
        #preprocess
        doc = self.lemmatize([input])
        #transform to vector space
        doc_tf = self.vectorizer.transform(doc)
        #calcualte similarities
        similarities = cosine_similarity(doc_tf, self.dtm).flatten()
        confidence = max(similarities)

        #early exit
        if confidence==0:
            return None,None,None
        #no threshold - already a fallback mechanism
        answers = self.answers.iloc[similarities.argsort()[-1:]].values[0]
        #variability
        answer = rnd.choice(answers)
        #for testing
        ##answer = answers[0]
        doc = self.df[self.df['Answer']==answer]['Doc'].values[0]
        #returns answers, the doc and the confidence

        #for testing purposes, returns only the answer
        ##return answer
        return answer, doc, confidence
