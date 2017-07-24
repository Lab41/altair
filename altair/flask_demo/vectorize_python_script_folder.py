import pickle
import hashlib
import os
from altair.util.separate_code_and_comments import separate_code_and_comments
from altair.util.normalize_text import normalize_text

# Compute MD5 hash of file contents
def file_digest(current_script_fullpath):
    # Get MD5 hash of file
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(current_script_fullpath, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

# Calculate Doc2Vec vector for a single script via pretrained model
def vectorize_code(current_script_fullpath, model, remove_comments):
    with open(current_script_fullpath, "r") as input:
        code = input.read()
    if remove_comments:
        parsed_code, _ = separate_code_and_comments(code, "code")
    else:
        parsed_code = code
    normalized_code = normalize_text(parsed_code, remove_stop_words=False, only_letters=False, return_list=True)
    if len(normalized_code) > 1:
        model.random.seed(0)
        return model.infer_vector(normalized_code)
    else:
        print("Warning - Parsing resulted in empty list for", current_script_fullpath)
        return None

def main(model_file, script_folder, vector_output_file,remove_comments):

    # Build list of Python scripts (*.py) to vectorize from script_folder
    filtered_script_folder_contents = [file for file in os.listdir(script_folder) if os.path.splitext(file)[1] in ['.py']]
    print("Identified {0} Python scripts from {1}".format(len(filtered_script_folder_contents),script_folder))

    # Load doc2vec trained model for vectorization
    model = pickle.load(open(model_file, "rb"))
    print("Loaded Doc2Vec pretrained model from", model_file)

    vectorized_scripts = dict()
    errors = 0
    processed = 0
    # Iterate over Python scripts and obtain vector for code found inside the file
    for current_script in filtered_script_folder_contents:
        current_script_fullpath = os.path.join(script_folder, current_script)
        script_hash = file_digest(current_script_fullpath)
        # Make dictionary key the script name and script hash to avoid key conflict of two files that have the same name
        script_dict_key = current_script + "__" + script_hash
        script_vector = vectorize_code(current_script_fullpath, model,remove_comments)
        if script_vector is not None:
            vectorized_scripts[script_dict_key] = script_vector
            processed+=1
        else:
            errors+=1

    print("{0} Python scripts vectorized with {1} parsing errors encountered".format(processed,errors))
    pickle.dump(vectorized_scripts, open(vector_output_file, "wb"))
    print("Script vector dictionary pickled in {0}".format(vector_output_file))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Use Doc2Vec pretrained model to vectorize folder of Python scripts')
    # Required args
    parser.add_argument("model_pickle_filename",
                        type=str,
                        help="Input file name for pickle file containing pretrained Altair Doc2Vec model")
    parser.add_argument("script_foldername",
                        type=str,
                        help="Input file name for folder containing Python scripts")
    parser.add_argument("vector_pickle_filename",
                        type=str,
                        help="Output pickle file containing dictionary of Python script names and associated Doc2Vec vectors")
    parser.add_argument("--remove_comments",
                        type=bool,
                        default=True,
                        help="Remove comments when vectorizing code in script")
    args = parser.parse_args()
    main(args.model_pickle_filename, args.script_foldername, args.vector_pickle_filename, args.remove_comments)