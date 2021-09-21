from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA

def flatten_list(lst):
    return [j for i in lst for j in i]

def preprocessing(text: str) -> str:
    '''
    >>> preprocessing('Hi @steve, check out this website: https://goodboi.com.')
    'hi check out this website'
    '''
    # urls, html-tags, escape, mentions
    text = re.sub('http+[a-zA-Z0-9.:/?]+|(&+[a-z]+;)|(<+[a-z/]+>)|(\@+[a-zA-Z0-9_]+)|\\n|\\r|RT ', '', text)
    # single letter words
    text = re.sub(r'\b\w\b', '', text)
    # clean text
    text = re.sub('[^a-zA-Z ]+', '', text).strip().lower()
    # double spaces
    text = re.sub(' +', ' ', text).strip()
    return text

def tokenize(text: str) -> list:
    '''
    >>> tokenize("Are you ready?")
    ['Are', 'you', 'ready?']
    '''
    return text.split()

def lemmatization(tokens: list) -> list:
    '''
    >>> lemmatization(['I', 'was', 'running', 'last', 'night'])
    ['I', 'be', 'run', 'last', 'night']
    '''
    lemm = WordNetLemmatizer()
    return [lemm.lemmatize(word, pos='v') for word in tokens]

def remove_stopwords(text: list) -> list:
    '''
    >>> remove_stopwords(['Hello', "you're", 'a', 'good', 'boy'])
    ['Hello', 'good', 'boy']
    '''
    stop = [
        'want','youre','let','feel','way','best','event',
        'get','try','step','know','last','man','young','say',
        'easy','new','part','hi','start','end','january','february',
        'march','may','june','july','august','september','october',
        'november','december','catch','haha','congrats','also','will',
        'go','like','good','bad','see','theyre','worse','ok','pick',
        'stop','kid','detail','no','yes','new','me'
    ]
    stop = stopwords.words('english') + stop
    return [word for word in text if word.lower() not in stop]
