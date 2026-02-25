from imports import *

from Classifier import *

class Similarity(Classifier):
    def __init__(self, file):
        self.file = file
        self.df = pd.read_csv(f'datasets/{self.file}.csv')
        self.stopwords =[]

        #check for file before re-training
        if not os.path.exists(f'models/{self.file}.joblib'):
            self.create_dt_matrix()
        #load the dtm and vectorizer once
        self.vectorizer = joblib.load(f'models/vectorizers/{self.file}.joblib')
        self.dtm = joblib.load(f'models/{self.file}.joblib')
        self.responses = joblib.load(f'models/responses/{self.file}.joblib')

    def create_dt_matrix(self):
        #creates and save the dtm
        #define the vectoriser
        vectorizer = TfidfVectorizer(use_idf=True, lowercase=True, ngram_range=(1,2))

        #preprocessing
        X = self.df['Utterance']
        y = self.df.drop('Utterance',axis=1).values.tolist()

        X_processed = self.lemmatize(X)
        #augmenting
        X_aug = self.augment(X_processed,y)
        #fitting
        matrix = vectorizer.fit_transform(X_aug['Utterance'])

        #save/overwrite
        joblib.dump(matrix, f'models/{self.file}.joblib')
        joblib.dump(vectorizer, f'models/vectorizers/{self.file}.joblib')
        joblib.dump(X_aug['Intent'], f'models/responses/{self.file}.joblib')

    def answer(self, input):
        #preprocess
        doc = self.lemmatize([input])
        #transform to vector
        doc_tf = self.vectorizer.transform(doc)
        #calculate cosine similarity
        similarities = cosine_similarity(doc_tf, self.dtm).flatten()
        confidence = max(similarities)
        #early exit
        if confidence==0:
            return None
        #find the answers
        answers = self.responses.iloc[similarities.argsort()[-1:]].values[0]

        #return the first answer for testing purpses
        ##return row[0]

        #select one answer at random
        answer = rnd.choice(answers).capitalize()
        if answer[-1] in string.punctuation:
            return answer
        return f'{answer}.'
