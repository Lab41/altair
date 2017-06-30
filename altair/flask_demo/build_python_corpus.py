import pickle
import json
import requests
import time 
import os

# Quasi-random search terms to get 1) 200k+ files and 2) variety in results from Github API
search_terms = ['caffe', 'doc2vec', 'tfidf', 'cnn', 'neural', 'theano','defaultdict', 'torch', \
'xgboost', 'sigmoid', 'relu', 'flask', 'list', 'float', 'int', 'math', 'statistics', 'machine', \
'deep', 'stochastic', 'gradient', 'learning', 'train', 'logreg', 'tanh', 'gru', 'gan', 'svm', 'bs4', 'lda2vec', \
'spacy','nlp','sklearn','nltk', 'lda','word2vec','lstm','rnn','resnet','cv2','chainer','tensorflow', \
'numpy','scipy','lambda', 'token', 'accuracy', 'precision', 'support', 'labels', \
'json', 'pandas', 'hash', 'metrics', 'sparse', 'tqdm', 'multiprocessing', 'argparse', 'PIL', 'plotly', 'matplotlib', \
'matrix', 'vector', 'predicted',  'softmax', 'batchnorm', 'dropout', 'convolution', 'biases', 'corpus', \
'vocabulary', 'ngram', 'vectorizer', 'feature', 'keys', 'gamma', 'alpha', 'sgd', 'decay', 'backprop', 'gpu', \
'logits', 'argmax', 'fscore', 'confusion', 'precision', 'recall', 'ggplot', 'seaborn', 'bokeh', \
'scatter', 'pylab', 'crossentropy', 'model', 'neurons', 'cuda', \
'and','del','from','not','while', 'as','elif','global','or','with', \
'assert','else','if','pass','yield', 'break','except','import','print', 'coherence', 'magnitude', \
'class','exec','in','raise', 'continue','finally','is','return', 'def','for','lambda','try', \
'tar','gz','zip','itertools','frozenset','django','sorted','intersection','extend', 'vstack' \
'tuple','urllib','requests','pillow','beautifulsoup','pygame','scrapy','nose','sacred',\
'sympy', 'sqlite', 'sql', 'query', 'distinct', 'keras', 'gensim', 'statsmodels', 'arrow', 'lxml', \
'LogisticRegression', 'LatentDirichletAllocation', 'blocks', 'baron', 'cython', 'SQLAlchemy', \
'tornado', 'tqdm', 'pymongo', 'six', 'fuel', 'toolz','pyminifier', 'random', 'time', 'collections', \
'distance', 'namedtuple','ordereddict','median','verbose','glove','sys','os','counter', 'padding', \
'gaussian', 'arange', 'subplot', 'regex', 'soundfile', 'speech', 'signal', 'spectrogram', 'imshow', \
'os','django','sys','utils','core','logging','models','db','re','numpy','time', \
'unittest','datetime','conf','json','contrib','common','collections','tests','base','util','test',\
'six','exceptions','subprocess','random','urllib','api','mock','setuptools','auth','io','http', \
'math','urls','views','config','tools','functools','flask','translation','argparse','shutil', \
'lib','copy','tempfile','sqlalchemy','threading','matplotlib','itertools','pytest','urlresolvers', \
'requests','warnings','scipy','distutils','socket','plugins','openstack','ext','nose','template',\
'uuid','management','decorators','shortcuts','forms','hashlib','path','traceback','testing', \
'string','model','PyQt4','apps','client','base64','glob','i18n','parse','types','app','moves', \
'constants','nova','xml','openerp','inspect','__future__','helpers','settings','struct','operator',\
'pandas','pickle','contextlib','twisted','fields','rest_framework','generic','platform','errors',\
'v2','encoding','oslo_config','compat','optparse','QtCore','python','unit','google','pprint',\
'codecs','wsgi','csv','signal','oslo_log','south','oslo','internet','backends','cache','orm',\
'neutron','errno','decimal','configparser','lxml','yaml','ctypes','admin','osv','compute',\
'multiprocessing','web','modules','imp','appengine','objects','interfaces','storage','tornado',\
'builtins','zope','server','QtGui','oslo_utils','log','interface','sklearn','tensorflow','ui',\
'widgets','repository','textwrap','html','webob','misc','alembic','defaults','dateutil','utilities',\
'pkg_resources','command','resources','pytz','PIL','services','main','response','engine','gui',\
'extensions','gi','pygame','queue','tasks','simplejson','importlib','version','framework','signals',\
'request','data','loader','parser','abc','jinja2','commands','werkzeug','validators','translate',\
'sql','unittest2','text','functional','files','PyQt5','logger','contenttypes']

def check_api_limit(message, code_urls):
    over_limit = False
    if 'message' in message and message['message'][:23]=='API rate limit exceeded':
        print("WARNING: Over API limit. Saving temp pickle, sleeping for 30 minutes...")
        over_limit = True
        save_temp_pickle(code_urls)
        time.sleep(1800)
    return over_limit

def save_temp_pickle(code_urls):
    temp_folder="temp"
    if not os.path.exists(temp_folder): os.mkdir(temp_folder)
    pickle_file_basename = os.path.basename(pickle_file_name) 
    temp_file_name = os.path.splitext(pickle_file_basename)[0]+"_"+str(int(time.time()))+os.path.splitext(pickle_file_basename)[1]    
    pickle.dump(code_urls, open(os.path.join(temp_folder,temp_file_name), "wb"))
    print("Python file inventory written to temp pickle file", os.path.join(temp_folder,temp_file_name)) 
    print("Total Python files inventoried:",len(code_urls))

def find_python_repos(oath_creds):
    code_urls = set()
    # Search code by multiple terms to generate different results
    for search_term in search_terms:
        print("Total Python files inventoried:",len(code_urls))
        # Github API caps number of results at 1000 (10 pages x 100 results per page)
        for page_num in range(1,11):
            print("Search term:'{}', Results page:{}".format(search_term,page_num))            
            URL = "https://api.github.com/search/code?q="+search_term+"+size:>1000+extension:py+language:python&per_page=100&page="+str(page_num)
            results = json.loads(requests.get(URL,auth=oath_creds).text)
            # If there are items in returned dict, look up the raw source code download page            
            if 'items' in results:
                for result in results['items']:  
                    try:                    
                        contents = json.loads(requests.get(result['url'],auth=oath_creds).text) 
                        # 'Size' can be missing due to API limit or Github error (ex: missing commit message) 
                        if 'size' not in contents:
                            over_limit, oath_token_slot = check_api_limit(contents, code_urls)
                            # If 'size' was missing because of API throttling error then try again, otherwise skip the url
                            if over_limit:
                               contents = json.loads(requests.get(result['url'],auth=oath_creds).text)
                            else:
                               continue  
                        code_urls.add(contents['download_url'])
                    except ValueError as v:
                        print("ValueError on",result['url'])
                        continue
                    except Exception as e:
                        print("Error on",result['url'])
                        continue

            # For generic search terms there should always be 'items' in results; Switch user account if over API limit                
            else:
                over_limit, oath_token_slot = check_api_limit(results, code_urls)
                
            # Reached the last page of search results (possible but unlikely)
            if 'items' in results and len(results['items'])<100:
                break
                
    return code_urls
    
def main(oath_userid,oath_token,pickle_file_name):
    # Github Oath authentication tokens are capped at 5000 API calls per hour
    oath_creds = (oath_userid,oath_token)
    code_urls = find_python_repos(oath_creds)
    print("Total Python files inventoried:",len(code_urls))
    pickle.dump(code_urls, open(pickle_file_name, "wb"))    
        						
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Build list of Github URLs that refer to Python scripts for Altair demo')
    # Required args
    parser.add_argument("oath_userid",
                        type=str,
                        help="Github oath userid")
    parser.add_argument("oath_token",
                        type=str,
                        help="Github oath token string")
    parser.add_argument("url_pickle_filename",
                        type=str,
                        help="Pickle file to store list of Github URLs that refer to Python scripts")
    args = parser.parse_args()
    main(args.oath_userid,args.oath_token,args.url_pickle_file_name)						
