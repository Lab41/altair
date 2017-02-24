import pickle
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from altair.vectorize01.vectorizers.Vectorizer import Vectorizer

class TFIDFVectorizer(Vectorizer):
    def __init__(self, pkl_vocab, vectorizer_kwargs=None, transformer_kwargs=None):
        if not vectorizer_kwargs:
            vectorizer_kwargs = {}
        if not transformer_kwargs:
            transformer_kwargs = {}

        with open(pkl_vocab, "rb") as f:
            vocab = pickle.load(f)
        vectorizer_kwargs["vocabulary"] = vocab
        self.vectorizer = CountVectorizer(**vectorizer_kwargs)
        self.transformer = TfidfTransformer(**transformer_kwargs)

    def vectorize(self, document):
        counts = self.vectorizer.transform([document])
        return self.transformer.fit_transform(counts)

    def vectorize_multi(self, documents):
        counts = self.vectorizer.transform(documents)
        return self.transformer.fit_transform(counts)
