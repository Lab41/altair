## Representing Source Code Other Than Python

The scripts in this directory were designed to be trained on Python scripts. We did not explore representations of other programming languages but it could be attempted via the following steps and modifications. 

### 1 - Obtain a large corpus of scripts to use as training data

- We used BigQuery and GitHubArchive to download more than 1,000,000 Python scripts 

- Our best models were trained on at least 500,000 of the downloaded scripts 

### 2 - Normalize the training data

- Remove any training data script that is less than 1000 characters in length. We found that many scripts less than 1000 characters in length were essentially fragments (ex: library import statements with no supporting code) of limited training value

- Remove the comments from the training data scripts. We found that nearly half of our training data contained no comments. To maintain consistency of the content and vocabulary across the training set we modified a minification script for Python code (util/separate_code_and_comments.py). Removing comments from scripts in a different programming language would require a new technique. 

- Parse the training script content according to the needs of the model. For Doc2Vec we formatted the script content to return an ordered list of words and did not remove "Python stop words" (util/normalize_text.py)

- These normalizations steps were included in our Doc2Vec training script (build/build_doc2vec_trainingset.py)

### 3 - Train the model

- We built our Doc2Vec models by leveraging multi-core (ex: 16) CPU support on a server with 128GB of RAM. The large RAM was needed to load 500,000+ normalized Python scripts into memory as training data and iterate over them (build/build_doc2vec_model_from_training_set.py)

- Training a Doc2Vec model on 500,000 Python scripts via multi-core CPU support with large RAM spanned 2 days and 1,000,000 Python scripts spanned nearly a week


### 4 - Check the model

- If you don't have a labeled test set, one option is to spot check that the model has learned similarities between coding keywords. We used a Jupyter notebook to show the closest words to a query word as shown in the "Do the word vectors show useful similarities?" example [here](https://markroxor.github.io/gensim/static/notebooks/doc2vec-IMDB.html)

- The expectation is that the model will have learned groupings of similar words used in code. When you have multiple trained models their results can be compared side by side.
     
### 5 - Vectorize the scripts to be used for recommendations

- Feed a folder of the scripts to be used for recommendations through the trained model and retain a lookup table for vectors and scripts (Dockerfile.vectorize_folder)

- Ensure that the normalization and parsing of these scripts are consistent with the training data used to train the model

### 6 - Get nearest vector to a new script

- Doc2Vec will calculate a vector representation for a new script using infer_vector(). The random_seed() call is needed to ensure deterministic output


    import pickle  
    trained_model = pickle.load(open(model_pickle_filename,"rb"))   
    trained_model.random.seed(0)   
    new_script_vector = trained_model.infer_vector(new_script_normalized_code) 

- Calculate a distance score (ex: cosine similarity) between the new script vector and the previously vectorized scripts to be used for recommendations (app.py). The closest vectors should content similar semantic content to the new script vector


