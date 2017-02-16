import pickle
import os
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer

from altair.vectorize01.code.build_bow_script_vocabulary import build_bow_script_vocabulary
from altair.util.separate_code_and_comments import separate_code_and_comments
from altair.util.normalize_text import normalize_text
from altair.util.log import getLogger

logger = getLogger(__name__)

def build_lda_model(script_folder,topics,vocab_pickle_filename,vocab_size,min_count):

    code_scripts_list = list()

    # Retrieve existing vocabulary or build a new bag of words vocabulary
    if vocab_pickle_filename is not None:
        vocab = pickle.load(open(vocab_pickle_filename, "rb"))
    else:
        if vocab_size is not None and min_count is not None:
            vocab = build_bow_script_vocabulary(script_folder,vocab_size,min_count)
        elif vocab_size is not None:
            vocab = build_bow_script_vocabulary(script_folder, vocab_size=vocab_size)
        elif min_count is not None:
            vocab = build_bow_script_vocabulary(script_folder, min_count=min_count)
        else:
            vocab = build_bow_script_vocabulary(script_folder)

    total = 0

    # Retrieve python script files
    for py_file in sorted(os.listdir(script_folder)):
        total += 1
        if total % 500 == 0: print(total, " files processed")
        fullpath = os.path.join(script_folder, py_file)
        with open(fullpath, "r") as py_file_contents:
            code, comments = separate_code_and_comments(py_file_contents.read(),py_file)
            if len(code) == 0: continue
            normalized_code = normalize_text(code, True, True, False, True)
            code_scripts_list.append(normalized_code)

    # Vectorize the python scripts with bag of words
    bow_model = CountVectorizer(analyzer="word", vocabulary=vocab)  # , binary=True)
    bow_vector_values = bow_model.transform(code_scripts_list).toarray()

    # Train/Fit LDA
    lda_model = LatentDirichletAllocation(n_topics=topics,learning_method="online")
    lda_model.fit(bow_vector_values)

    return lda_model

# Run this when called from CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build LDA model on set of python scripts')

    # Required args
    parser.add_argument("script_folder",
                        type=str,
                        help="Folder location of Python script files")

    parser.add_argument("topics",
                        type=int,
                        default=50,
                        help="Number of topics in the LDA model (default=50)")

    parser.add_argument("model_pickle_filename",
                        type=str,
                        help="Output file name for pickle file containing fitted LDA model")

    # Optional args
    parser.add_argument("--vocab_pickle_filename",
                        type=str,
                        help="File location for pickle file containing vocabulary list")

    parser.add_argument("--vocab_size",
                        type=int,
                        default=10000,
                        help="Specify size of vocabulary, which will be Bag of Words dimension size (default = 5000)")
    parser.add_argument("--min_count",
                    type=int,
                    default=5,
                    help="Minimum times a word is observed in corpus for the word to be included in vocabulary (default = 2)")

    args = parser.parse_args()
    lda_model = build_LDA_model(args.script_folder,args.topics,args.vocab_pickle_filename,args.vocab_size,args.min_count)
    logger.info("Saving LDA model in a pickle file at %s" % args.model_pickle_filename)
    pickle.dump(lda_model, open(args.model_pickle_filename, "wb"))
    logger.info("LDA model pickle file saved at %s" % args.model_pickle_filename)