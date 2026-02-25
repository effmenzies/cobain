from imports import *

from Input import *

class Classifier:
    def __init__(self, file,analyzer='word',ngram=(1,2)):
        self.file=file
        self.analyzer=analyzer
        self.ngram=ngram

        self.df = pd.read_csv(f'datasets/{file}.csv')
        #check for valid dataset
        if self.df.shape[1]!=2:
            raise Exception('Dataset must contan two columns')
        #normalise dataset
        self.df.columns=['Utterance','Intent']

        self.stopwords = ['a','an','one','the','it','its','this','that','there',"'s","'d",'is','am','are','be','to','some','few','go','for']
        #check if exists to preent retraining
        if not os.path.exists(f'models/{self.file}.joblib'):
            self.train()
        #load models
        self.vectorizer = joblib.load(f'models/vectorizers/{self.file}.joblib')
        self.clf = joblib.load(f'models/{self.file}.joblib')

    def pos_to_wordnet(self, pos_tag):
        #Map POS tag to WordNet tag
        if pos_tag.startswith('NN'):
            return wordnet.NOUN
        elif pos_tag.startswith('VB'):
            return wordnet.VERB
        elif pos_tag.startswith('JJ'):
            return wordnet.ADJ
        elif pos_tag.startswith('RB'):
            return wordnet.ADV
        else:
            return None

    def lemmatize(self,docs):
        #preprocessing
        lem = WordNetLemmatizer()
        lemmatized =[]
        for doc in docs:
            tagged_tokens = pos_tag([word for word in word_tokenize(doc) if word not in string.punctuation and word not in self.stopwords])
            lemmed = [lem.lemmatize(word,self.pos_to_wordnet(tag) or wordnet.NOUN)
                          for word, tag in tagged_tokens]
            lemmatized.append(" ".join(lemmed))
        return lemmatized

    def train(self):
        #split data
        X = self.df['Utterance'].values
        y = self.df['Intent'].values
        X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3,random_state=42,stratify=y)
        
        #define vectorizer
        vectorizer = TfidfVectorizer(use_idf=True,lowercase=True, ngram_range=self.ngram, analyzer=self.analyzer)
        
        #preprocess training data
        X_train = self.lemmatize(X_train)

        #augment data
        df_aug = self.augment(X_train,y_train)

        #transform to vector space
        X_aug = df_aug['Utterance'].values
        y_aug=df_aug['Intent'].values
        X_tf = vectorizer.fit_transform(X_aug)

        #train model
        clf = LogisticRegression(class_weight='balanced').fit(X_tf,y_aug)

        #serialise
        os.makedirs("models/vectorizers", exist_ok=True)
        joblib.dump(clf,f'models/{self.file}.joblib')
        joblib.dump(vectorizer,f'models/vectorizers/{self.file}.joblib')

        #for evaluation
        ##return self.test(X_test,y_test, X_tf, y_aug)
        return

    def test(self,X_test,y_test,X_tf, y_aug):
        #transform preprocessed test set
        X_test_tf = self.vectorizer.transform(self.lemmatize(X_test))
        #make predictions
        pred = self.clf.predict(X_test_tf)
        #cv scores
        kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=3)
        cv_scores = cross_val_score(self.clf,X_tf,y_aug,scoring='accuracy',cv=kfold)
        #conf_matrix
        conf_matrix = confusion_matrix(y_test, pred)
        precision, recall, _, _ = precision_recall_fscore_support(y_test, pred, average='weighted')
        return cv_scores, conf_matrix, precision, recall

    def synonym_set(self, text):
        tagged_tokens = pos_tag(word_tokenize(text))
        augments = [text]
        rnd.seed(42)
        #replace each word 3 times
        for _ in range(3):
            for word, tag in tagged_tokens:
                synonyms = {" ".join(lemma.name().split('_')) 
                            for syn in wordnet.synsets(word, pos=self.pos_to_wordnet(tag)) 
                            for lemma in syn.lemmas() if lemma.name() != word}
                #replace the word
                if synonyms:
                    augments.append(text.replace(word,rnd.choice(list(synonyms))))
        return augments
    
    def augment(self,X,y):
        rnd.seed(42)
        data=[]
        alphabet = string.ascii_letters.lower()
        for idx,sample in enumerate(X):
            #append synonyms
            for doc in self.synonym_set(sample):
                data.append((doc,y[idx]))

            #three character changes per sample
            for _ in range(3):
                for word in sample.split():

                    #random character deletion
                    chars = list(word)
                    aug_chars=chars
                    aug_chars.remove(rnd.choice(chars))
                    aug_word = "".join(aug_chars)
                    data.append((sample.replace(word,aug_word),y[idx]))

                    #random character insertion
                    aug_chars=chars
                    aug_chars.insert(rnd.randint(0,len(word)),rnd.choice(alphabet))
                    aug_word = "".join(aug_chars)
                    data.append((sample.replace(word,aug_word),y[idx]))

                    #random character swap
                    if len(chars)>1:
                        aug_chars=chars
                        pos = rnd.randint(0,len(aug_chars)-2)
                        temp = aug_chars[pos]
                        aug_chars[pos] = aug_chars[pos+1]
                        aug_chars[pos+1] = temp
                        aug_word = "".join(aug_chars)
                        data.append((sample.replace(word,aug_word),y[idx]))

                    #random exchange
                    word.replace(rnd.choice(chars),rnd.choice(alphabet))
                    aug_word = "".join(word)
                    data.append((sample.replace(word,aug_word),y[idx]))
        return pd.DataFrame(data, columns=['Utterance','Intent'])
    
    def intent(self,input):
        if not input:
            raise Exception('empty input')
        
        #transform the processed input
        input_tf = self.vectorizer.transform(self.lemmatize([input]))
        #calculate certainty
        proba = self.clf.predict_proba(input_tf)[0]

        #certainty
        confidence = max(proba)

        #80% certainty threshold
        if confidence>0.8:
            return self.clf.classes_[np.argmax(proba)]
        return None
