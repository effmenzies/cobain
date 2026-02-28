from imports import *

class Input:
    def __init__(self):
        self.vocab = []
        
    def process(self, text):
        self.doc = nlp(text)
        self.subjects = [token for token in self.doc if token.dep_ == "nsubj"]
        self.objects = [token for token in self.doc if token.dep_ in ["dobj", "pobj"]]
        self.verbs = [token for token in self.doc if token.pos_ == "VERB"]
        self.nouns = [token for token in self.doc if token.pos_ == "NOUN"]
        self.vocab.append(self.doc)

    def is_exit(self):
        pass

    def __call__(self):
        return self.input
