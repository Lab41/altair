# This script was created to take the csv output from sqlite and convert it to JSON
# The csv output was generated from the Meta Kaggle dataset (https://www.kaggle.com/kaggle/meta-kaggle)
#
# The database fields represented in the csv file were:
# ScriptProjectId = Unique id of overall script project
# ScriptVersionId = Unique id of the version number of the script
# AuthorUserId = Unique id of the author of the script
# UserDisplayName = Text display name of the user/author
# CompetitionId = Unique id of the kaggle competition for the script
# CompetitionName = Text name of the competition for the script
# ScriptTitle = Text title for the script
# ScriptContent = Text of the actual code in the script

import csv
import json
import argparse
import sys
from pyminifier import token_utils, minification, obfuscate
from collections import namedtuple

from altair.util.log import getLogger

logger = getLogger(__name__)

def main(args):

    # Open input and output files
    csv_file = open(args.input_file, 'r')
    json_file = open(args.output_file, 'w')

    # Check if user wants to customize csv field order
    if not args.field_order_file:
        field_names = ["ScriptProjectId","ScriptVersionId","AuthorUserId","UserDisplayName","CompetitionId","CompetitionName","ScriptTitle","ScriptContent"]
    else:
        with open(args.field_order_file, 'r') as _order_file:
            field_order_reader = csv.reader(order_file)
            for row in field_order_reader:
                field_names = row
                continue

    # Address csv error regarding fields that exceed default size limit
    # Adapted from Stack Overflow post by user1251007
    maxInt = sys.maxsize
    decrement = True

    while decrement:
        # decrease the maxInt value by factor 10
        # as long as the OverflowError occurs.

        decrement = False
        try:
            csv.field_size_limit(maxInt)
        except OverflowError:
            maxInt = int(maxInt/10)
            decrement = True

    # Read CSV and Write the JSON to output_file after doing some preprocessing
    reader = csv.DictReader(csv_file, field_names)

    files = 0
    errors = 0
    written = 0
    options_tuple = namedtuple("options_tuple", ["tabs", "minimize", "obfuscate", "replacement_length"])
    options = options_tuple(False, args.minimize, args.obfuscate, 1)
    logger.info("Processing csv file...")

    for row in reader:
        files+=1
        # Remove very short or long scripts based on command line arguments
        script_len = len(row['ScriptContent'])
        if script_len<args.min_script_len or script_len>args.max_script_len:
            continue
        # Remove meta kaggle scripts labeled as python that are probably R
        if row['ScriptContent'].find("<-")!=-1 and row['ScriptContent'].find("library(")!=-1:
            continue

        # Remove Kaggle competition name from the script content to allow model testing on competitions
        if 'CompetitionName' in row and 'ScriptContent' in row:
            row['ScriptContent'].replace(row['CompetitionName']," ")
            row['ScriptContent'].replace(row['CompetitionName'].lower(), " ")

        # Minimize size of python script if set in args
        if args.minimize or args.obfuscate:
            try:
                tokens = token_utils.listified_tokenizer(row['ScriptContent'])
                source = minification.minify(tokens,options)
                tokens = token_utils.listified_tokenizer(source)

                # Obsfuscate python script
                if args.obfuscate:
                    table = [{}]
                    module = row['ScriptTitle']
                    name_generator = obfuscate.obfuscation_machine(identifier_length=int(options.replacement_length))
                    obfuscate.obfuscate(module, tokens, options, name_generator=name_generator, table=table)

                # Convert back to text
                result = ''
                result += token_utils.untokenize(tokens)
                row['ScriptContent'] = result

            except Exception as e:
                # logger.info("%s in %s; continuing" % (e.__class__.__name__,row['ScriptTitle']))
                errors+=1
                continue

        written+=1
        json.dump(row, json_file)
        json_file.write('\n')

    logger.info("Total files reviewed: %d" % files)
    if args.minimize or args.obfuscate:
        logger.info("File that failed pyminifier minimization/obfuscation parsing: %d" % errors)
    logger.info("Files successfully parsed to json: %d" % written)
    csv_file.close()
    json_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Meta Kaggle csv file to json format')

    # Required args
    parser.add_argument("input_file",
                        type=str,
                        help="Input file (csv)")
    parser.add_argument("output_file",
                        type=str,
                        help="Output file (json)")

    # Optional args
    parser.add_argument("--field_order_file",
                        type=str,
                        help="Comma Delimited File that contains a single line representing the field names and order \
                        (ex: ScriptContent,CompetitionName,CompetitionId)")
    parser.add_argument("--min_script_len",
                        type=int,
                        default=100,
                        help="Set a minimum character length for each script (default=100)")
    parser.add_argument("--max_script_len",
                        type=int,
                        default=1000000000,
                        help="Set a minimum character length for each script (default=1000000000)")
    parser.add_argument("--minimize",
                        action="store_true",
                        help="Specify whether to minimize script contents (default = false)")
    parser.add_argument("--obfuscate",
                        action="store_true",
                        help="Specify whether to obsfuscate script contents (default = false)")

    main(parser.parse_args())