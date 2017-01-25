# Converts an indidivual Python file or a directory of Python files to Python3
# Note - These functions will overwrite the files after conversion. Originals are not retained.

from lib2to3.refactor import RefactoringTool, get_fixers_from_package

avail_fixes = set(get_fixers_from_package('lib2to3.fixes'))
rt = RefactoringTool(avail_fixes)

# Converts and overwrites a Python file to Python3
def convert_file(filename):
    rt.refactor_file(filename, write=True)

# Converts and overwrites all files ending in .py in the directory to Python3
def convert_directory(directoryname):
    rt.refactor_dir(directoryname,write=True)

