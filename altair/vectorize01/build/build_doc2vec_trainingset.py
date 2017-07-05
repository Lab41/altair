from gensim.models import doc2vec
import pickle
import os
import json
import time
from altair.util.separate_code_and_comments import separate_code_and_comments
from altair.util.normalize_text import normalize_text
from altair.util.log import getLogger

logger = getLogger(__name__)

def main(script_folder,output_folder,min_script_len,max_total_files,max_per_pkl):

    doc2vec_tagged_documents = list()
    counter = 0
    logger.info("retrieving files")
    just_started = True

    # Retrieve files containing Python scripts
    # Altair's JSON format uses the 'content' label for the script code
    for py_file in sorted(os.listdir(script_folder)):
        if counter>= max_total_files: break
        fullpath = os.path.join(script_folder, py_file)
        with open(fullpath, "r") as py_file_contents:
            for line in py_file_contents:
                if counter >= max_total_files: break
                if counter!=0 and counter % 50000 == 0: logger.info("processed %d files" % counter)
                if not just_started and counter % max_per_pkl == 0:
                    logger.info("Saving pickle file of tagged documents for size %d",max_per_pkl)
                    pickle.dump(doc2vec_tagged_documents, open(os.path.join(output_folder,"training"+str(int(time.time()))+".pkl"), "wb"))
                    doc2vec_tagged_documents = list()
                    just_started = True
                parsed_json = json.loads(line)
                code, _ = separate_code_and_comments(parsed_json['content'],py_file)
                if len(code) < min_script_len:
                    continue
                else:
                    tokenized_code = normalize_text(code, remove_stop_words=False, only_letters=False, return_list=True, remove_one_char_words=True)
                    if len(tokenized_code) > 1:
                    	doc2vec_tagged_documents.append(doc2vec.TaggedDocument(tokenized_code, [counter]))
                    	counter += 1
                    	just_started = False
        
    logger.info("Saving final pickle file of tagged documents for size %d",max_per_pkl)            
    pickle.dump(doc2vec_tagged_documents, open(os.path.join(output_folder,"training"+str(int(time.time()))+".pkl"), "wb"))

# Run this when called from CLI
if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Build large set of Python scripts for Doc2Vec model training')
    # Required args
    parser.add_argument("script_folder",
                        type=str,
                        help="Folder name containing Python scripts as lines in files")
    parser.add_argument("output_folder",
                        type=str,
                        help="Folder name to save training set files")
    parser.add_argument("min_script_len",
                        type=int,
                        help="Minimum length of acceptable Python scripts",
                        default=2000)
    parser.add_argument("max_total_files",
                        type=int,
                        help="Maximum number of Python scripts for training",
                        default=1200000)
    parser.add_argument("max_per_pkl",
                        type=int,
                        help="Maximum number of Python scripts per saved pickle file",
                        default=300000)

    args = parser.parse_args()
    main(args.script_folder,args.output_folder,args.min_script_len,args.max_total_files,args.max_per_pkl)						
