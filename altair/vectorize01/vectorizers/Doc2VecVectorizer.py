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
        # Doc2Vec expects a list of words that includes stop words
        normalized_doc = normalize_text(document, remove_stop_words=False, only_letters=False, return_list=True, **self.normalizer_kwargs)
        # Doc2Vec requires a defined seed for deterministic results when calling infer_vector
        self.model.random.seed(0)
        return self.model.infer_vector(normalized_doc, **self.infer_kwargs)

    def vectorize_multi(self, documents):
        vectorized = []
        for document in documents:
            # Doc2Vec expects a list of words that includes stop words
            normalized_doc = normalize_text(document, remove_stop_words=False, only_letters=False, return_list=True, **self.normalizer_kwargs)
            # Doc2Vec requires a defined seed for deterministic results when calling infer_vector
            self.model.random.seed(0)
            vectorized.append(self.model.infer_vector(normalized_doc, **self.infer_kwargs))
        return vectorized
