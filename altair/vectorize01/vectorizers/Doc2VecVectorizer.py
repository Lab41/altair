import pickle
from altair.util.normalize_text import normalize_text
from altair.vectorize01.vectorizers.Vectorizer import Vectorizer

class Doc2VecVectorizer(Vectorizer):
    def __init__(self, pkl_d2v_model, normalizer_kwargs=None, infer_kwargs=None):
        if not normalizer_kwargs:
            normalizer_kwargs = {}
        if not infer_kwargs:
            infer_kwargs = {}

        with open(pkl_d2v_model, "rb") as f:
            self.model = pickle.load(f)
        self.normalizer_kwargs = normalizer_kwargs
        self.infer_kwargs = infer_kwargs

    def vectorize(self, document):
        normalized_doc = normalize_text(document, **self.normalizer_kwargs)
        return self.model.infer_vector(normalized_doc, **self.infer_kwargs)

    def vectorize_multi(self, documents):
        vectorized = []
        for document in documents:
            normalized_doc = normalize_text(document, **self.normalizer_kwargs)
            vectorized.append(self.model.infer_vector(normalized_doc, **self.infer_kwargs))
        return vectorized
