import pickle
import os
import json
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer

from altair.util.separate_code_and_comments import separate_code_and_comments
from altair.util.normalize_text import normalize_text
from altair.util.log import getLogger

logger = getLogger(__name__)

def build_lda_model(code_scripts_list,topics,vocab,use_binary=False,n_jobs=1):

    # Vectorize the python scripts with bag of words
    bow_model = CountVectorizer(analyzer="word", vocabulary=vocab, binary=use_binary)
    bow_vector_values = bow_model.transform(code_scripts_list).toarray()

    # Train/Fit LDA
    lda_model = LatentDirichletAllocation(n_topics=topics,learning_method="online",random_state=0,n_jobs=1)
    lda_model.fit(bow_vector_values)

    return lda_model

def main(script_folder,topics,vocab_pickle_filename,model_pickle_filename,max_script_count,use_binary,n_jobs):

    # Retrieve existing vocabulary
    if vocab_pickle_filename is not None:
        vocab = pickle.load(open(vocab_pickle_filename, "rb"))
    else:
        logger.warning("Pickle file containing bag of words vocabulary required")
        quit()

    code_scripts_list = list()
    counter = 0

    # Retrieve files containing Python scripts
    # Altair's JSON format uses the 'content' label for the script code
    for py_file in sorted(os.listdir(script_folder)):
        if counter >= max_script_count: break
        fullpath = os.path.join(script_folder, py_file)
        with open(fullpath, "r") as py_file_contents:
            for line in py_file_contents:
                counter += 1
                parsed_json = json.loads(line)
                code, comments = separate_code_and_comments(parsed_json['content'],py_file)
                if len(code) == 0:
                    continue
                else:
                    normalized_code = normalize_text(code, remove_stop_words=True, only_letters=False, return_list=False, remove_one_char_words=True)
                    code_scripts_list.append(normalized_code)

    lda_model = build_lda_model(code_scripts_list,topics,vocab,use_binary,n_jobs)

    #logger.info("Saving LDA model in a pickle file at %s" % model_pickle_filename)
    pickle.dump(lda_model, open(model_pickle_filename, "wb"))
    logger.info("LDA model pickle file saved at %s" % model_pickle_filename)

# Run this when called from CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build LDA model on set of python scripts')

    # Required args
    parser.add_argument("script_folder",
                        type=str,
                        help="Folder location of Python script files")

    parser.add_argument("vocab_pickle_filename",
                        type=str,
                        help="Input file location for pickle file containing previously built vocabulary list")

    parser.add_argument("model_pickle_filename",
                        type=str,
                        help="Output file name for pickle file containing fitted LDA model")

    # Optional args
    parser.add_argument("--topics",
                        type=int,
                        default=100,
                        help="Number of topics in the LDA model (default=100)")

    parser.add_argument("--max_script_count",
                        type=int,
                        default=10000,
                        help="Specify maximum number of code scripts to process (default = 10000")
    
    parser.add_argument("--use_binary",
                    action="store_true",
                    help="Specify whether LDA is provided binary Bag of Words representations (default=False)")

    parser.add_argument("--n_jobs",
                    type=int,
                    default=1,
                    help="Flag for multiprocessing where -1 uses all CPUs and 1 uses 1 CPU (default=1)")

    args = parser.parse_args()
    main(args.script_folder,args.topics,args.vocab_pickle_filename,args.model_pickle_filename,args.max_script_count,args.use_binary,args.n_jobs)
