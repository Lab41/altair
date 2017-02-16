from bs4 import BeautifulSoup
import re
import warnings
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from altair.util.log import getLogger

logger = getLogger(__name__)

# Regular expressions to remove web links and only keep letter characters
link_re = re.compile(r'\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*')
letter_re = re.compile(r"[^a-zA-Z]")

# Use Python 3.0 keyword list (keyword.kwlist) in lower case as stop word candidates for code
python_stop_words = ['false', 'none', 'true', 'and', 'as', 'assert', 'break', 'class', 'continue', 'def', \
              'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', \
              'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', \
              'with', 'yield']

def normalize_text(raw_text, remove_stop_words=True, only_letters=True, return_list=False, remove_one_char_words=True, **kwargs):
    '''
    Algorithm to convert raw text to a return a clean text string
    Method modified from code available at:
    https://www.kaggle.com/c/word2vec-nlp-tutorial/details/part-1-for-beginners-bag-of-words
    Args:
        raw_text: Original text to clean and normalize
        remove_stop_words: Boolean value to trigger removal of stop words
        only_letters: Boolean value to trigger removal of characters that are not letters
        return_list: Boolean value to trigger return value as a list of words
        remove_one_char_words: Boolean value to trigger removal of words that are only a single character
    Returns:
        clean_text: Either a string or a list of words that has been filtered based on function parameters.

    '''
    # 1. Remove web links
    clean_text = link_re.sub('', raw_text)

    # 2. Remove HTML
    # Suppress UserWarnings from BeautifulSoup due to text with tech info (ex: code, directory structure)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning)
        clean_text = BeautifulSoup(clean_text, "lxml").get_text()

    # 3. Remove non-letters
    if only_letters: clean_text = letter_re.sub(" ", clean_text)

    # 4. Convert to lower case, split into individual words
    clean_text = clean_text.lower().split()

    # 5. Remove stop words
    if remove_stop_words:
        clean_text = [w for w in clean_text if not w in python_stop_words]
        clean_text = [w for w in clean_text if not w in ENGLISH_STOP_WORDS]

    # 6. Remove words that are only a single character in length
    if remove_one_char_words: clean_text = [w for w in clean_text if len(w)>1]

    # 7. Return as string or list based on parameters
    if return_list:
        return clean_text
    else:
        return " ".join(clean_text)