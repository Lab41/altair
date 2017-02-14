from redbaron import RedBaron
import os
from collections import defaultdict
import pickle

from altair.util.log import getLogger

logger = getLogger(__name__)

def parse_fromimport_statements(fromimport_node_list, include_import_segment=False):
    '''
    Function to parse through import statements that begin with 'from' keyword (ex: from xml import parser)
    Note: Only the main library referenced after the from keyword is captured (ex: from xml.parser import tree = xml)
    Input: fromimport_node_list (RedBaron object containing list of FromImportNode objects)
            include_import_segment (Boolean flag to parse the segment after the 'import' keyword)
     Output: libraries (set of imported libraries identified from the fromimport_node_list)
    '''

    libraries = set()

    # Iterate over the FromImportNodes provided by Red Baron
    for fromimport_node in fromimport_node_list:
        # Iterate over the values associated with each FromImportNode
        for from_clause in fromimport_node.value:
            # Skip unique circumstance of local library import (ex: 'from .util import x')
            if fromimport_node.dumps().find('from .') != -1:
                continue
            else:
                libraries.add(from_clause.dumps())

        if include_import_segment:
            # This section identifies the import segment of the statement (ex: 'from xml import parser' = parser)
            for import_clause in fromimport_node.targets:
                # Remove reference to renaming a library (numpy as np becomes numpy)
                library_name = import_clause.dumps().split(' as')[0]
                # Address unique circumstance of 'from setup import (x,y,z)'
                if library_name not in ['(', ')']:
                    libraries.add(import_clause.dumps())

    return libraries

def parse_import_statements(import_node_list, include_dotted_segments=False):
    '''
    Function to parse through library import statements (ex: import xml.parser)
    Note: Only the main library referenced after the 'import' keyword is captured (ex: import xml.parser = xml)
    Input: import_node_list (RedBaron object containing list of ImportNode objects)
            include_dotted_segments (Boolean flag to also parse the dotted segments of a library)
    Output: libraries (set of imported libraries identified from the import_node_list)
    '''

    libraries = set()
    # Iterate over the ImportNodes provided by Red Baron
    for import_node in import_node_list:
        # Iterate over the values associated with each ImportNode (this will be all the libraries separated by commas)
        for comma_separated in import_node.value:
            library_name = comma_separated.dumps()
            # Only take the base of a library when dots are present (xml.parser becomes xml)
            # Note that this can create duplicate library mentions (xml.parser and xml.token = xml)
            library_name = library_name.split('.')[0]
            # Remove reference to author renaming a library (numpy as np becomes numpy)
            library_name = library_name.split(' as')[0]
            libraries.add(library_name)

            if include_dotted_segments:
                # This section extracts the dot separated components (ex: from xml.parser.expat = [xml,parser,expat])
                if len(import_node.value[0].value) > 1:
                    for dot_separated in import_node.value[0].value:
                        libraries.add(dot_separated.dumps())

    return libraries


def build_imported_libraries_vocabulary(script_folder, vocab_size=500, min_count=2):
    library_count = defaultdict(int)

    # Build list of python files and process with red baron to identify imported libraries
    for py_file in sorted(os.listdir(script_folder)):
        fullpath = os.path.join(script_folder, py_file)
        with open(fullpath, "r") as py_file_contents:
            try:
                red = RedBaron(py_file_contents.read())
                libraries = parse_import_statements(red.find_all("ImportNode"))
                libraries |= parse_fromimport_statements(red.find_all("FromImportNode"))
                for library in libraries: library_count[library] += 1

            except Exception as e:
                logger.info("%s error encountered in %s; skipping file" % (e.__class__.__name__, py_file))
                continue

    # Determine descending order for library based on count
    library_by_count = [i[0] for i in sorted(library_count.items(), key=lambda x: (x[1], x[0]), reverse=True) if
                        i[1] > min_count]

    # Trim the vocabulary to the requested vocab_size
    if len(library_by_count) >= vocab_size:
        library_by_count = library_by_count[:vocab_size]

    return library_by_count

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Build bag of words vocabulary for imported libraries from a folder of Python scripts.')

    # Required args
    parser.add_argument("script_folder",
                        type=str,
                        help="Folder location of Python scripts")
    parser.add_argument("pickle_filename",
                        type=str,
                        help="Output file name for pickle file containing vocabulary list")

    # Optional args
    parser.add_argument("--vocab_size",
                        type=int,
                        default=500,
                        help="Specify size of vocabulary, which will be Bag of Words dimension size (default = 5000)")
    parser.add_argument("--min_count",
                    type=int,
                    default=2,
                    help="Minimum times a library is observed in corpus for the library to be included in vocabulary (default = 2)")

    args = parser.parse_args()
    imported_libraries_vocabulary = build_imported_libraries_vocabulary(args.script_folder, args.vocab_size, args.min_count)
    if len(imported_libraries_vocabulary) < args.vocab_size:
        logger.warning("Only %d libraries were observed using vocab_size=%d and min_count=%d" % (len(imported_libraries_vocabulary), args.vocab_size, args.min_count))
    logger.info("Saving imported libraries vocabulary pickle file at %s" % args.pickle_filename)
    pickle.dump(imported_libraries_vocabulary, open(args.pickle_filename, "wb"))
    logger.info("Imported libraries vocabulary pickle file saved at %s" % args.pickle_filename)