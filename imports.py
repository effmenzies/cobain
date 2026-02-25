import json, ijson, sqlite3, joblib, string, os, re, nltk
import pandas as pd, random as rnd, numpy as np
from datetime import datetime, timedelta
from dateutil import parser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from nltk import pos_tag, WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from collections import deque, namedtuple