import abc
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from altair.vectorize01.vectorizers.Vectorizer import Vectorizer

class BowAllVectorizer(Vectorizer):
    def __init__(self, pkl_vocab, vectorizer_kwargs=None):
        if not vectorizer_kwargs:
            vectorizer_kwargs = {}

        with open(pkl_vocab, "rb") as f:
            vocab = pickle.load(f)
        vectorizer_kwargs["vocabulary"] = vocab
        self.vectorizer = CountVectorizer(**vectorizer_kwargs)

    def vectorize(self, document):
        return self.vectorizer.transform([document])

    def vectorize_multi(self, documents):
        return self.vectorizer.transform(documents)