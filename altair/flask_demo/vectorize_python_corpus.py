import pickle
import requests
import time
import os
from altair.util.separate_code_and_comments import separate_code_and_comments
from altair.util.normalize_text import normalize_text
import sys

def intermediate_save(code_vectors):
    temp_folder="temp"
    if not os.path.exists(temp_folder): os.mkdir(temp_folder)
    vector_file_basename = os.path.basename(vector_file) 
    temp_file_name = os.path.splitext(vector_file_basename)[0]+"_"+str(int(time.time()))+os.path.splitext(vector_file_basename)[1]
    pickle.dump(code_vectors, open(os.path.join(temp_folder,temp_file_name), "wb"))
    print("Update - Python file inventory written to temp pickle file", os.path.join(temp_folder,temp_file_name)) 
    print("Update - Total Python files vectorized:",len(code_vectors))

def vectorize_code(code_vectors,code_urls,model):
    # code_urls is a set, make it a list to allow skipping some entries
    code_urls_list = list(code_urls)
    # start at a point close to where the previous code_vectors file left off
    starting_point = len(code_vectors)
    for i in range(starting_point,len(code_urls_list)):
	    url = code_urls_list[i]
	    if i>starting_point and i % 5000 == 0: 
	        intermediate_save(code_vectors)
	    if requests.get(url).status_code==200:
	        try:
	            code = requests.get(url).text
	            parsed_code, _ = separate_code_and_comments(code,"code")
	            normalized_code = normalize_text(parsed_code, remove_stop_words=False, only_letters=False, return_list=True)
	            if len(normalized_code)>1:
	                model.random.seed(0)
	                vector = model.infer_vector(normalized_code)
	                code_vectors[url]=vector
	            else:
	                print("Parsing resulted in empty list for",url)
	                continue
	        except:
	            print("Unexpected error:", sys.exc_info()[0])
	            continue
	    else:
	       print("Error code {} for url: {}".format(requests.get(url).status_code, url))
    return code_vectors
	
def main(model_file,url_file,vector_file):
    # Load doc2vec pretrained model for vectorization
    model = pickle.load(open(model_file,"rb"))
    print("Loaded model from",model_file)
    # Load url list of python scripts
    code_urls = pickle.load(open(url_file,"rb"))
    print("Loaded python file listing from",url_file)
    try: 
        code_vectors = pickle.load(open(vector_file,"rb"))
        print("Loaded code vectors from",vector_file)
    except:
        code_vectors = dict()
        pass    
    print("Start - Total Python files inventoried:",len(code_urls))
    print("Start - Total Python files vectorized:",len(code_vectors))
    if len(code_urls)==len(code_vectors):
        print("All code has been vectorized; quitting")
        return 0
    code_vectors = vectorize_code(code_vectors,code_urls,model)
    print("Final - Total Python files inventoried:",len(code_urls))
    print("Final - Total Python files vectorized:",len(code_vectors))
    pickle.dump(code_vectors, open(vector_file, "wb"))    
        						
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Vectorize list of Github URLs that refer to Python scripts for Altair demo')
    # Required args
    parser.add_argument("model_pickle_filename",
                        type=str,
                        help="File name for pickle file containing pretrained Altair Doc2Vec model")
    parser.add_argument("url_pickle_filename",
                        type=str,
                        help="Pickle file with list of Github URLs that refer to Python scripts")
    parser.add_argument("vector_pickle_filename",
                        type=str,
                        help="Pickle file containing dictionary of URLs for Python scripts and associated Doc2Vec vectors")
    args = parser.parse_args()
    main(args.model_pickle_filename,args.url_pickle_filename,args.vector_pickle_filename)						
