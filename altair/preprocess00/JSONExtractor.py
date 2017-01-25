import gzip
import json
import os

class JSONExtractor:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def extract(self, path_to_json_gz):
        basename = os.path.basename(path_to_json_gz).split(".")[0] # remove extension
        folder = os.path.join(self.output_dir, basename)
        if not os.path.exists(folder):
            os.makedirs(folder)

        with gzip.open(path_to_json_gz, "rb") as f1:
            for line in f1:
                j = json.loads(line)
                target = os.path.join(folder, "%s.py" % j["id"])
                with open(target, "w") as f2:
                    f2.write(j["content"].encode("utf-8"))

if __name__ == "__main__":
    input_dir = ""
    output_dir = ""

    extractor = JSONExtractor(output_dir)
    for json_gz_file in os.listdir(input_dir):
        extractor.extract(json_gz_file)