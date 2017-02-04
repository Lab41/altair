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
                        help="File that contains a single line representing the field names and order (\"FirstName\",\"LastName\",\"IDNumber\",\"Message\")")

    # Open input and output files 
    args = parser.parse_args()
    if args.input_file == args.output_file:
        print("Input file should not be the same as Output file")
        quit()         

    csv_file = open(args.input_file, 'r')
    json_file = open(args.output_file, 'w')

    # Check if user wants to customize csv field order 
    if not args.field_order_file:
        field_names = ["ScriptProjectId","ScriptVersionId","AuthorUserId","UserDisplayName","CompetitionId","CompetitionName","ScriptTitle","ScriptContent"]
    else:
        with open(args.field_order_file, 'r') as _order_file:
            field_order_reader = csv.reader(order_file)
            for row in field_order_reader: 
                field_names = [x for x in row]           

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
    for row in reader:
        # Remove meta kaggle scripts labeled as python that are actually R
        if row['ScriptContent'].find("<-")!=-1 and row['ScriptContent'].find("library(")!=-1:
            continue
        # Remove Kaggle competition name from the script content to allow model testing on competitions
        if 'CompetitionName' in row and 'ScriptContent' in row:
             row['ScriptContent'].replace(row['CompetitionName']," ")
        json.dump(row, json_file)
        json_file.write('\n')
