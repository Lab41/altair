import pickle
from sklearn.feature_extraction.text import CountVectorizer
from altair.vectorize01.vectorizers.Vectorizer import Vectorizer

class LDAVectorizer(Vectorizer):
    def __init__(self, pkl_lda_model, pkl_vocab, vectorizer_kwargs=None):
        if not vectorizer_kwargs:
            vectorizer_kwargs = {}

        with open(pkl_lda_model, "rb") as f:
            self.model = pickle.load(f)
        with open(pkl_vocab, "rb") as f:
            vocab = pickle.load(f)
        vectorizer_kwargs["analyzer"] = "word"
        vectorizer_kwargs["vocabulary"] = vocab
        self.vectorizer = CountVectorizer(**vectorizer_kwargs)

    def vectorize(self, document):
        counts = self.vectorizer.transform([document])
        return self.model.transform(counts)[0]

    def vectorize_multi(self, documents):
        counts = self.vectorizer.transform([documents])
        return self.model.transform(counts)[0]
