import os
import json
import pickle
from collections import defaultdict

from altair.util.separate_code_and_comments import separate_code_and_comments
from altair.util.normalize_text import normalize_text
from altair.util.log import getLogger

logger = getLogger(__name__)

def build_bow_script_vocabulary(script_folder, max_script_count=10000, max_vocab_size=5000, min_word_count=2):
    '''
    Generates a dictionary of words to be used as the vocabulary in techniques that utilize bag of words.
    Args:
        script_folder (str): Folder location of corpus containing script files
        max_script_count (int): the maximum number of code scripts to process in the script_folder
        max_vocab_size (int): the maximum number of words to be used in the vocabulary (dimension of bag of words vector)
        min_word_count (int): a word will be included in vocabulary if it appears at least min_count times in the corpus
    Returns:
        words_ordered_by_count (list): a list of size equal or less than vocab_size that contains the most frequent
        normalized words in the corpus
    '''
    word_count = defaultdict(int)
    counter = 0

    # Read file contents, extract code, normalize contents and count resulting tokens
    # Altair's JSON format uses the 'content' label for the script code
    for py_file in sorted(os.listdir(script_folder)):
        if counter >= max_script_count: break
        fullpath = os.path.join(script_folder, py_file)
        with open(fullpath, "r") as py_file_contents:
            for line in py_file_contents:
                counter += 1
                parsed_json = json.loads(line)
                code, comments = separate_code_and_comments(parsed_json['content'],py_file)
                normalized_script = normalize_text(code, True, True, True, True)
                for token in normalized_script: word_count[token] += 1
                if counter >= max_script_count: break

    # Determine descending order for library based on count and restricted by min_count threshold
    words_ordered_by_count = [i[0] for i in sorted(word_count.items(), key=lambda x: (x[1], x[0]), reverse=True) if
                              i[1] > min_word_count]

    # Trim the vocabulary to the requested vocab_size
    if len(words_ordered_by_count) >= max_vocab_size:
        words_ordered_by_count = words_ordered_by_count[:max_vocab_size]
    else:
        logger.warning("Only %d words were observed using max_script_count=%d, max_vocab_size=%d and min_word_count=%d" % \
                       (len(words_ordered_by_count),max_script_count, max_vocab_size,min_word_count))

    return words_ordered_by_count

def main(script_folder,vocab_pickle_filename,max_script_count,max_vocab_size,min_word_count):

    bow_script_vocabulary = build_bow_script_vocabulary(script_folder, max_script_count, max_vocab_size, min_word_count)

    logger.info("Saving bag of words vocabulary pickle file at %s" % vocab_pickle_filename)
    pickle.dump(bow_script_vocabulary, open(vocab_pickle_filename, "wb"))
    logger.info("Bag of words vocabulary pickle file saved at %s" % vocab_pickle_filename)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build bag of words vocabulary from a folder that contains multiple files of JSON arrays.')

    # Required args
    parser.add_argument("script_folder",
                        type=str,
                        help="Folder location of Python scripts")
    parser.add_argument("vocab_pickle_filename",
                        type=str,
                        help="Output file name for pickle file containing vocabulary list")

    # Optional args
    parser.add_argument("--max_script_count",
                        type=int,
                        default=10000,
                        help="Specify maximum number of code scripts to process (default = 10000")
    parser.add_argument("--max_vocab_size",
                        type=int,
                        default=5000,
                        help="Specify maximum size of vocabulary, which will be Bag of Words dimension size (default = 5000)")
    parser.add_argument("--min_word_count",
                    type=int,
                    default=2,
                    help="Minimum times a word is observed in corpus for the word to be included in vocabulary (default = 2)")

    args = parser.parse_args()
    main(args.script_folder,args.vocab_pickle_filename,args.max_script_count,args.max_vocab_size,args.min_word_count)
