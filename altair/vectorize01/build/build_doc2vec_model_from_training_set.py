'''
Doc2Vec parameters
dm_mean - 0 uses sum, 1 uses mean. Only applies when dm is non-concatenative mode
dm - defines the training algorithm. By default (dm=1), ‘distributed memory’ (PV-DM) is used. Otherwise, distributed bag of words (PV-DBOW) is employed.
dbow_words - if set to 1 trains word-vectors (in skip-gram fashion) simultaneous with DBOW doc-vector training; default is 0 (faster training of doc-vectors only).
dm_concat - if 1, use concatenation of context vectors rather than sum/average; default is 0 (off). Note concatenation results in a much-larger model, as the input is no longer the size of one (sampled or arithmatically combined) word vector, but the size of the tag(s) and all words in the context strung together.
dm_tag_count = expected constant number of document tags per document, when using dm_concat mode; default is 1.
trim_rule = vocabulary trimming rule, specifies whether certain words should remain
size is the dimensionality of the feature vectors
window is the maximum distance between the predicted word and context words used for prediction within a document.
alpha is the initial learning rate (will linearly drop to zero as training progresses).
min_count = ignore all words with total frequency lower than this.
max_vocab_size = limit RAM during vocabulary building
sample = threshold for configuring which higher-frequency words are randomly downsampled; default is 0 (off), useful value is 1e-5.
iter = number of iterations (epochs) over the corpus. The default inherited from Word2Vec is 5, but values of 10 or 20 are common in published ‘Paragraph Vector’ experiments.
hs = if 1 (default), hierarchical sampling will be used for model training (else set to 0).
negative = if > 0, negative sampling will be used, the int for negative specifies how many “noise words” should be drawn (usually between 5-20).
'''

from gensim.models import doc2vec
from random import shuffle
import pickle
import os
import time

from log import getLogger
logger = getLogger(__name__)

def main(trainingset_folder, model_pickle_filename, training_algorithm, num_cores, epochs, vector_size, window, min_count, alpha, negative):

    doc2vec_model = doc2vec.Doc2Vec(dm=training_algorithm, size=vector_size, sample=1e-5, window=window, min_count=min_count, iter=20, dbow_words=1, workers=num_cores, alpha=0.05, min_alpha=0.001, negative=negative)
    doc2vec_tagged_documents = list()

    for trainingset in os.listdir(trainingset_folder):
        logger.info("starting training set %s" % trainingset)
        doc2vec_tagged_documents += pickle.load(open(os.path.join(trainingset_folder,trainingset),"rb"))

    #doc2vec_model = train_doc2vec_model(doc2vec_model, doc2vec_tagged_documents,epochs)
    # build Doc2Vec's vocab
    logger.info("building vocabulary")
    doc2vec_model.build_vocab(doc2vec_tagged_documents)

    # run training epochs while shuffling data and lowering learning rate (alpha)
    for i in range(epochs):
        logger.info("starting code epoch %d" % int(i+1))
        doc2vec_model.train(doc2vec_tagged_documents)
        doc2vec_model.alpha -= 0.002
        shuffle(doc2vec_tagged_documents)
    #logger.info("saving model pickle for %s" % trainingset)
    #pickle.dump(doc2vec_model, open(model_pickle_filename[:-4]+"_"+str(int(time.time()))+os.path.splitext(model_pickle_filename)[1], "wb"))
    #doc2vec_model.alpha = 0.05
    #in_loop = True

    # Per http://radimrehurek.com/gensim/models/doc2vec.html, delete_temporary_training_data reduces model size
    # If keep_doctags_vectors is set to false, most_similar, similarity, sims is no longer available
    # If keep_inference is set to false, infer_vector on a new document is no longer possible
    doc2vec_model.delete_temporary_training_data(keep_doctags_vectors=False, keep_inference=True)

    # Per http://radimrehurek.com/gensim/models/doc2vec.html, doc2vec has its own  method for saving/loading models
    # doc2vec_model.save(model_pickle_filename)
    # doc2vec_model = doc2vec.Doc2Vec.load(model_pickle_filename)

    #logger.info("saving doc2vec model in a pickle file at %s" % model_pickle_filename)
    pickle.dump(doc2vec_model, open(model_pickle_filename, "wb"))
    logger.info("doc2vec model pickle file saved at %s" % model_pickle_filename)

# Run this when called from CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build Doc2Vec model on set of python scripts')

    # Required args
    parser.add_argument("trainingset_folder",
                        type=str,
                        help="Folder location of Python script file list pickled in TaggedDocument format")

    parser.add_argument("model_pickle_filename",
                        type=str,
                        help="Output file name for pickle file containing trained Doc2Vec model")

    # Optional args
    parser.add_argument("--training_algorithm",
                        type=int,
                        default=2,
                        help="Training algorithm is 'distributed memory' (PV-DM)=1 or distributed bag of words (PV-DBOW)=2 (default=2)")

    parser.add_argument("--num_cores",
                        type=int,
                        default=1,
                        help="Number of cores for parallelism (default=1)")

    parser.add_argument("--epochs",
                        type=int,
                        default=5,
                        help="Number of training epochs for Doc2Vec model (default=5)")

    parser.add_argument("--vector_size",
                        type=int,
                        default=300,
                        help="Size of Doc2Vec vectors (default=300)")

    parser.add_argument("--window",
                        type=int,
                        default=5,
                        help="Maximum distance between the predicted word and context words used for prediction within a document (default=5)")

    parser.add_argument("--min_count",
                        type=int,
                        default=10,
                        help="Minimum number of document appearances for an associated word to be included in vocabulary (default=10)")

    parser.add_argument("--alpha",
                        type=float,
                        default=0.05,
                        help="Initial learning rate for model (default=0.05)")

    parser.add_argument("--negative",
                       type=int,
                       default=0,
                       help="Specify number of noise words used for negative sampling (default = 0)")

    args = parser.parse_args()
    main(args.trainingset_folder, args.model_pickle_filename, args.training_algorithm, args.num_cores, args.epochs, args.vector_size, args.window, args.min_count, args.alpha, args.negative)

