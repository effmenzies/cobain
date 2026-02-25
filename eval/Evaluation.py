from ChatBot import *
from Classifier import *
from Database import *
from Input import *
from Music import *
from Query import *
from Similarity import *
from Transaction import *
from Api import *

class Evaluator(Chatbot):
    def __init__(self):
        #initialise classifiers
        self.confirm = Classifier('confirm', analyzer='char_wb',ngram=(2,4))
        self.intent = Classifier('intent')

        #initialise similarity models
        self.smalltalk = Classifier('smalltalk')
        self.responses= Similarity('responses')
        self.qanda = Query('qanda')

        #other
        self.api = Api()
        self.transaction = Transaction()
        self.database = Database()

        #retrain models
        self.retrain()

    @staticmethod
    def test_set(file):
        return pd.read_csv(f'datasets/eval/{file}.csv')

    def classifier_test(self):
        #evaluate classifiers
        classifiers = {'Confirmations classifier':self.confirm,'Intent classifier':self.intent,'Smalltalk classifier':self.smalltalk}
        results={}
        for name, clf in classifiers.items():
            cv_scores, conf_matrix, precision, recall = clf.train()
            results[name]={'cv_scores':cv_scores,'conf_matrix':conf_matrix,'precision':precision,'recall':recall}
        return results

    def similarity_test(self):
        #evaluate similarity models
        classifiers = {'responses':self.responses,'qanda':self.qanda}
        results={}
        for name, model in classifiers.items():
            test_set = self.test_set(name)
            X = test_set['X'].values
            #consistent labels
            y_true = test_set['y'].values
            y_pred=[model.answer(x) for x in X]
            accuracy = self.qanda_accuracy(y_true,y_pred)
            results[name] = accuracy
        return results


    @staticmethod
    def qanda_accuracy(y_true,y_pred):
        correct_count = sum(1 for true, pred in zip(y_true,y_pred) if true==pred)
        print(correct_count)
        accuracy = correct_count / len(y_pred)
        return accuracy
