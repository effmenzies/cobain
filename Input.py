from imports import *

class Input:
    def __init__(self, input):
        self.input = input

    def __call__(self):
        return self.input

    def standardise(self):
        inputs = []
        clauses = self.divide_input()
        for clause in clauses:
            inputs.append(" ".join([word.lower() for word in word_tokenize(clause) if word not in string.punctuation]))
        return inputs
    
    def tokenize(self):
        return word_tokenize(self())

    def divide_input(self):
        clauses = re.split(r'[,.!?]|(?:,\s)?(?:but|however|although|because)',self())
        return [clause.strip() for clause in clauses if clause.strip()]

    def subject(self):
        #distinguishes subject between use and system
        subject = [word for word,tag in pos_tag(self.tokenize()) if ((tag in ['PRP$']) or (word in ['you','i']))]
        if subject[-1] in ['my','i','mine','myself','me']:
            return 'user'
        else: return 'bot'

    def proper_noun(self):
        #for finding a city when asking for the weather
        noun = [word for word,tag in pos_tag(self.tokenize()) if tag == 'NN']
        pattern= r"(?<=in\s)(?:[A-Za-z]+\s*)+\s*(?=right\s*now|at\s*the\s*moment|today|this\s*week|later|$)"
        match = re.findall(pattern,self(), re.IGNORECASE | re.VERBOSE)
        if match:
            return match[0]
        elif noun:
            return noun[-1]
        return None