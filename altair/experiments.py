'''
Conducts an experiment on Altair's evaluation pipeline using Sacred
The output is recorded by Sacred if environment variable MONGO_DB_URI is set
'''

import argparse
import os
from evaluation import main as altair_evaluation
from altair.vectorize01.vectorizers.BowAllVectorizer import BowAllVectorizer
from altair.vectorize01.vectorizers.BowImportVectorizer import BowImportVectorizer
from altair.vectorize01.vectorizers.Doc2VecVectorizer import Doc2VecVectorizer
from altair.vectorize01.vectorizers.LDAVectorizer import LDAVectorizer
from altair.vectorize01.vectorizers.TFIDFVectorizer import TFIDFVectorizer

from sacred import Experiment
from sacred.observers import MongoObserver
from sacred.initialize import Scaffold

# Declare Sacred Experiment
ex = Experiment('Testing Altair Evaluation')

def run_model():
    return altair_evaluation(data_path=data_path,num_cores=num_cores,top_n_param=top_n,vectorizer=vectorizer)

def main():
    parser = argparse.ArgumentParser(description='Calculate Altair evaluation metrics (Top 1, Top N Any, Top N All) with Sacred.')

    # Required args
    parser.add_argument("data_path",
                        type=str,
                        help="Location of metakaggle JSON file.")

    # Optional args
    parser.add_argument("--num_cores",
                        type=int,
                        default=1,
                        help="Number cores (for parallelism).")
    parser.add_argument("--top_n",
                        type=int,
                        default=3,
                        help="N for calculating Top N (Any) and Top N (All).")

    subparsers = parser.add_subparsers(help="Subparsers per vectorizer type.")
    ###

    bow_all = subparsers.add_parser("bow_all",
                                    help="Bag of words vectorizer (entire script).")
    bow_all.add_argument("pkl_vocab",
                         type=str,
                         help="Path to vocabulary pickle file. Generated offline by build_bow_script_vocabulary.py.")
    bow_all.add_argument("--vectorizer_kwargs",
                         type=str,
                         help="Keyword arguments (see CountVectorizer docs for full list). Format: key1=val;key2=val2.")
    bow_all.set_defaults(vectorizer_cls = BowAllVectorizer)

    ###

    bow_import = subparsers.add_parser("bow_import",
                                       help="Bag of words vectorizer (libraries only).")
    bow_import.add_argument("pkl_libraries",
                            type=str,
                            help="Path to libraries pickle file. Generated offline by build_imported_libraries_vocabulary.py.")
    bow_import.add_argument("--vectorizer_kwargs",
                            type=str,
                            help="Keyword arguments (see CountVectorizer docs for full list). Format: key1=val;key2=val2.")
    bow_import.set_defaults(vectorizer_cls = BowImportVectorizer)

    ###

    doc2vec = subparsers.add_parser("doc2vec",
                                    help="Doc2Vec vectorizer (Le, Mikolov 2014) in gensim.")
    doc2vec.add_argument("pkl_d2v_model",
                         type=str,
                         help="Path to pickled Doc2Vec model. Generated offline.")
    doc2vec.add_argument("--normalizer_kwargs",
                         type=str,
                         help="Keyword arguments (see normalize_text() in utils/ for full list). Format: key1=val;key2=val2.")
    doc2vec.add_argument("--infer_kwargs",
                         type=str,
                         help="Keyword arguments (see Doc2Vec.infer_vector() docs for full list). Format: key1=val;key2=val2.")
    doc2vec.set_defaults(vectorizer_cls = Doc2VecVectorizer)

    ###

    lda = subparsers.add_parser("lda",
                                help="Latent Dirichlet Allocation vectorizer (Blei, Ng, Jordan 2003) in scikit-learn.")
    lda.add_argument("pkl_vocab",
                     type=str,
                     help="Path to vocabulary pickle file. Generated offline by build_bow_script_vocabulary.py.")
    lda.add_argument("pkl_lda_model",
                     type=str,
                     help="Path to pickled LDA model. Generated offline.")
    lda.add_argument("--vectorizer_kwargs",
                     type=str,
                     help="Keyword arguments (see CountVectorizer docs for full list). Format: key1=val;key2=val2.")
    lda.set_defaults(vectorizer_cls = LDAVectorizer)

    ###

    tfidf = subparsers.add_parser("tfidf",
                                  help="TF-IDF (Term Frequency, Inverse Document Frequency) vectorizer.")
    tfidf.add_argument("pkl_vocab",
                       type=str,
                       help="Path to vocabulary pickle file. Generated offline by build_bow_script_vocabulary.py.")
    tfidf.add_argument("--vectorizer_kwargs",
                       type=str,
                       help="Keyword arguments (see CountVectorizer docs for full list). Format: key1=val;key2=val2.")
    tfidf.add_argument("--transformer_kwargs",
                       type=str,
                       help="Keyword arguments (see TfidfTransformer docs for full list). Format: key1=val;key2=val2.")
    tfidf.set_defaults(vectorizer_cls = TFIDFVectorizer)

    args = parser.parse_args()
    args = args.__dict__

    # Make dictionary to pass as Sacred configuration variables (must be JSON serializable)
    import copy
    configs = copy.copy(args)
    configs.pop("vectorizer_cls")

    global data_path
    data_path = args.pop("data_path")
    global num_cores
    num_cores = args.pop("num_cores")
    global top_n
    top_n = args.pop("top_n")

    for argname, val in args.items():
        if "kwargs" in argname and val is not None:
            args[argname] = parse_kwargs(val)

    vectorizer_cls = args.pop("vectorizer_cls")
    global vectorizer
    vectorizer = vectorizer_cls(**args)

    # Add string descriptor of vectorizer to configs dict given Sacred's JSON serializable requirement
    if vectorizer_cls == BowAllVectorizer:
        configs["vectorizer_string"] = 'bow_all'
    elif vectorizer_cls == BowImportVectorizer:
        configs["vectorizer_string"] = 'bow_import'
    elif vectorizer_cls == TFIDFVectorizer:
        configs["vectorizer_string"] = 'tfidf'
    elif vectorizer_cls == LDAVectorizer:
        configs["vectorizer_string"] = 'lda'
    elif vectorizer_cls == Doc2VecVectorizer:
        configs["vectorizer_string"] = 'doc2vec'
    else:
        print("Unknown vectorizer; quitting")
        quit()

    # Monkey patch to avoid having to declare all our variables
    def noop(item):
        pass

    Scaffold._warn_about_suspicious_changes = noop

    # Add mongo observer for Sacred
    ex.observers.append(MongoObserver.create(url=os.environ['MONGO_DB_URI'], db_name='testing_altair_experiment'))

    # Define the entrypoint
    ex.main(lambda: run_model())

    # Tell sacred about config items so they are logged
    ex.run(config_updates=configs)

if __name__ == "__main__": main()


