import json
import tqdm
from multiprocessing import Pool, Queue
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

data = "/path/to/metakaggle.json"
num_cores = 4
top_n = 5

raw = []
print("Reading data from: %s" % data)
with open(data, "r") as f:
    for line in f:
        raw.append(json.loads(line))

# Get script contents for any scripts that are not in
# PyCon2015 Tutorial (#4353)
# Word2Vec NLP Tutorial (#3971)
scripts = [script["ScriptContent"] for script in raw if script["CompetitionId"] not in ["4353", "3971"]]

# Choose vectorizer
print("Vectorizing documents...")
vectorizer = CountVectorizer()
features = vectorizer.fit_transform(scripts)
features_dense = features.todense()

def q_init(q):
    score_performance.q = q

def score_performance(t):
    current_idx, v = t
    pair_sims = cosine_similarity(v, features)
    top_candidates = pair_sims[0].argsort()[-top_n+1:][::-1][1:]

    comp_id = raw[current_idx]["CompetitionId"]
    candidate_ids = [raw[candidate_idx]["CompetitionId"] for candidate_idx in top_candidates]
    scoring = [candidate_id == comp_id for candidate_id in candidate_ids]

    top_1_score = int(scoring[0])
    top_n_any_score = int(any(scoring))
    top_n_all_score = int(all(scoring))
    score_performance.q.put((top_1_score, top_n_any_score, top_n_all_score))

q = Queue()
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

print("Top 1: %s" % (score_top_1 / float(len(raw))))
print("Top N (Any): %s" % (score_top_n_any / float(len(raw))))
print("Top N (All): %s" % (score_top_n_all / float(len(raw))))
print("(N = %s)" % top_n)