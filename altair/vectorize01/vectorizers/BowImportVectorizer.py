import pickle
from redbaron import RedBaron
from sklearn.feature_extraction.text import CountVectorizer
from altair.vectorize01.vectorizers.Vectorizer import Vectorizer
from altair.vectorize01.build.build_imported_libraries_vocabulary import parse_fromimport_statements, parse_import_statements

class BowImportVectorizer(Vectorizer):
    def __init__(self, pkl_libraries, vectorizer_kwargs=None):
        if not vectorizer_kwargs:
            vectorizer_kwargs = {}

        with open(pkl_libraries, "rb") as f:
            vocab = pickle.load(f)
        vectorizer_kwargs["vocabulary"] = vocab
        self.vectorizer = CountVectorizer(**vectorizer_kwargs)

    def _extract_libraries(self, document):
        red = RedBaron(document)
        libraries = parse_import_statements(red.find_all("ImportNode"))
        libraries |= parse_fromimport_statements(red.find_all("FromImportNode"))
        return " ".join(libraries)

    def vectorize(self, document):
        libraries_str = [self._extract_libraries(document)]
        return self.vectorizer.transform(libraries_str)

    def vectorize_multi(self, documents):
        lib_documents = []
        for document in documents:
            lib_documents.append(self._extract_libraries(document))
        return self.vectorizer.transform(lib_documents)