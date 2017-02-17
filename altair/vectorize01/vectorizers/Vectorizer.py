from abc import ABCMeta, abstractmethod

class Vectorizer:
    __metaclass__ = ABCMeta

    @abstractmethod
    def vectorize(self, document):
        raise NotImplementedError("Child class must implement vectorize().")

    @abstractmethod
    def vectorize_multi(self, documents):
        raise NotImplementedError("Child class must implement vectorize_multi().")