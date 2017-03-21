import json
import tqdm
import numpy
from multiprocessing import Pool, Queue
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import issparse

from altair.vectorize01.vectorizers.BowAllVectorizer import BowAllVectorizer
from altair.vectorize01.vectorizers.BowImportVectorizer import BowImportVectorizer
from altair.vectorize01.vectorizers.Doc2VecVectorizer import Doc2VecVectorizer
from altair.vectorize01.vectorizers.LDAVectorizer import LDAVectorizer
from altair.vectorize01.vectorizers.TFIDFVectorizer import TFIDFVectorizer
from altair.util.separate_code_and_comments import separate_code_and_comments

features = None
raw = None
q = Queue()

def q_init(q):
    score_performance.q = q

def score_performance(t):
    current_idx, v = t
    # sklearn throws deprecation warnings for 1d arrays so need to reshape v
    pair_sims = cosine_similarity(v.reshape(1, -1), features)
    # TODO: Set a minimum cosine similarity score for candidates?
    top_candidates = pair_sims[0].argsort()[-top_n-1:][::-1]

    comp_id = raw[current_idx]["CompetitionId"]
    candidate_ids = [raw[candidate_idx]["CompetitionId"] for candidate_idx in top_candidates if candidate_idx!=current_idx][:top_n]
    scoring = [candidate_id == comp_id for candidate_id in candidate_ids]

    top_1_score = int(scoring[0])
    top_n_any_score = int(any(scoring))
    top_n_all_score = int(all(scoring))
    score_performance.q.put((top_1_score, top_n_any_score, top_n_all_score))

def main(data_path, num_cores, top_n_param, vectorizer):
    global raw
    global features
    global q
    global features_dense

    # Patch for error thrown by score_performance on declaration of top_n
    global top_n
    top_n = top_n_param

    raw = read_data(data_path)

    """
    # Remove items where competition IDs are in:
    # PyCon2015 Tutorial (#4353)
    # Word2Vec NLP Tutorial (#3971)
    filter_comp_ids = ["4353", "3971"]
    idxs_to_remove = set()
    for idx, r in enumerate(raw):
        if r["CompetitionId"] in filter_comp_ids:
            idxs_to_remove.add(idx)
    raw = [r for idx, r in enumerate(raw) if idx not in idxs_to_remove]
    """
    """
    # Take a random sample from raw.
    import random
    raw = random.sample(raw, 2000)
    """
    
    # Strip out comments and add to scripts if it has code; otherwise remove it from raw list  
    scripts = list()
    for index,script in list(enumerate(raw)):
        code, _ = separate_code_and_comments(script["ScriptContent"],script["ScriptTitle"])
        if len(code)>0: 
            scripts.append(code)
        else:
            raw.pop(index)
    #scripts = [script["ScriptContent"] for script in raw]

    # Choose vectorizer
    print("Vectorizing documents...")
    #vectorizer.vectorizer.fit(scripts)
    features = vectorizer.vectorize_multi(scripts)
    features_dense = features.todense() if issparse(features) else features
    p = Pool(num_cores, q_init, [q])
    print("Calculating pairwise similarities + scores...")
    for _ in tqdm.tqdm(p.imap_unordered(score_performance, list(enumerate(features_dense))), total=len(features_dense)):
        pass

    score_top_1 = 0
    score_top_n_any = 0
    score_top_n_all = 0

    while not q.empty():
        top_1, top_n_any, top_n_all = q.get()

        score_top_1 += top_1
        score_top_n_any += top_n_any
        score_top_n_all += top_n_all

    top_1_accuracy = score_top_1 / float(len(raw))
    top_n_any_accuracy = score_top_n_any / float(len(raw))
    top_n_all_accuracy = score_top_n_all / float(len(raw))

    print("Top 1: %s" % top_1_accuracy)
    print("Top N (Any): %s" % top_n_any_accuracy)
    print("Top N (All): %s" % top_n_all_accuracy)
    print("(N = %s)" % top_n)

    return {"top_1_accuracy":top_1_accuracy, "top_n_any_accuracy":top_n_any_accuracy, "top_n_all_accuracy":top_n_all_accuracy, "top_n":top_n}

def read_data(data_path):
    raw = []
    print("Reading data from: %s" % data_path)
    with open(data_path, "r") as f:
        for line in f:
            raw.append(json.loads(line))
    return raw

def parse_kwargs(kwargs_str):
    kv_pairs = kwargs_str.split(";")
    kwargs = {}
    for kv_pair in kv_pairs:
        k, v = kv_pair.split("=")
        kwargs[k] = v
    return kwargs

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Calculate evaluation metrics (Top 1, Top N Any, Top N All).')

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

    data_path = args.pop("data_path")
    num_cores = args.pop("num_cores")
    top_n = args.pop("top_n")

    for argname, val in args.items():
        if "kwargs" in argname and val is not None:
            args[argname] = parse_kwargs(val)

    vectorizer_cls = args.pop("vectorizer_cls")
    vectorizer = vectorizer_cls(**args)

    main(data_path, num_cores, top_n, vectorizer)
