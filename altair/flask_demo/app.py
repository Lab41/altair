# Remember to set PYTHONHASHSEED=0 as an environment variable
# or different vector results will occur each time this file is executed

from flask import Flask
from flask import render_template
from flask import request
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import json
import requests
from altair.util.separate_code_and_comments import separate_code_and_comments
from altair.util.normalize_text import normalize_text

app= Flask(__name__)

@app.route("/")
def main():
   return render_template('index.html')

@app.route('/',methods=['POST'])
def work_it():
    uri = request.form['uri']
    if uri:
        print ('looking for {0} ...'.format(uri))

        try:
        	closest = get_closest_docs(uri)
        	print(json.dumps({'ret':'True','userWord':uri,'closestWord':closest,'msg':'success'}))
        	return json.dumps({'ret':'True','userWord':uri,'closestWord':closest,'msg':'success'})
        except:
            return json.dumps({'ret':'False','userWord':uri,'msg':'script not found'})
    else:
        return json.dumps({'ret':'False','msg':'put in a script URL'})

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
    
def get_closest_docs(uri):
    user_doc = requests.get(uri).text
    code, _ = separate_code_and_comments(user_doc,"user doc")
    normalized_code = normalize_text(code, remove_stop_words=False, only_letters=False, return_list=True)
    model.random.seed(0)
    user_vector = model.infer_vector(normalized_code)
    print("finding similar...")
    stored_urls = list()
    stored_vectors = list()
    for url in vectors:
        stored_urls.append(url)
        stored_vectors.append(vectors[url])
    pair_sims = cosine_similarity(user_vector.reshape(1, -1), stored_vectors)
    indices = (-pair_sims[0]).argsort()[:5]
    return [(stored_urls[index],round(float(pair_sims[0][index]),2)) for index in indices]    
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run Altair demo with Doc2Vec pretrained model')
    # Required args
    parser.add_argument("model_pickle_filename",
                        type=str,
                        help="File name for pickle file containing pretrained Altair Doc2Vec model")

    parser.add_argument("vector_pickle_filename",
                        type=str,
                        help="Pickle file containing dictionary of URLs for Python scripts and associated Doc2Vec vectors")
    args = parser.parse_args()
    global model 
    model = pickle.load(open(args.model_pickle_filename,"rb"))
    global vectors 
    vectors = pickle.load(open(args.vector_pickle_filename,"rb"))
    
    app.run(host='0.0.0.0')

