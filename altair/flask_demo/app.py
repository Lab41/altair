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
import sys

app= Flask(__name__)

@app.route("/")
def main():
   return render_template('index.html')

@app.route('/',methods=['POST'])
def work_it():
    uri = request.form['uri']
    radio = request.form.get('group1', None)
    print("radio",radio)

    if uri:
        print ('looking for {0} ...'.format(uri))
        sys.stdout.flush()

        try:
            if radio == "script":
                closest = get_closest_docs(uri)
            else:
                closest = get_closest_words(uri)
            print(json.dumps({'ret':'True','userWord':uri,'closestWord':closest,'msg':'success', 'type':radio}))
            sys.stdout.flush()
            return json.dumps({'ret':'True','userWord':uri,'closestWord':closest,'msg':'success','type':radio})
        except:
            return json.dumps({'ret':'False','userWord':uri,'msg':'not found','type':radio})
    else:
        return json.dumps({'ret':'False','msg':'put in a Python script URL or a Python word'})

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
    #user_doc = requests.get(uri).text
    r = requests.get(uri)
    if r.status_code == 200:
        user_doc = r.text
        print("URI content length",len(user_doc))
        code, _ = separate_code_and_comments(user_doc,"user doc")
        normalized_code = normalize_text(code, remove_stop_words=False, only_letters=False, return_list=True)
        model.random.seed(0)
        user_vector = model.infer_vector(normalized_code)
        print("finding similar...")
        sys.stdout.flush()
        stored_urls = list()
        stored_vectors = list()
        for url in vectors:
            stored_urls.append(url)
            stored_vectors.append(vectors[url])
        pair_sims = cosine_similarity(user_vector.reshape(1, -1), stored_vectors)
        indices = (-pair_sims[0]).argsort()[:5]
        return [(stored_urls[index],round(float(pair_sims[0][index]),2)) for index in indices]
    else:
        print("URL returned status code", r.status_code)
        raise ValueError('URL error')

def get_closest_words(word):
    model.random.seed(0)
    nearby_words = model.most_similar(word)
    print("finding similar...")
    sys.stdout.flush()
    return [(word,round(float(distance),2)) for word,distance in nearby_words]


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

