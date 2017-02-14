from altair.util.log import getLogger
logger = getLogger(__name__)

# Using langdetect to determine human language type (pip install langdetect)
from langdetect import detect, DetectorFactory

def determine_spoken_language(comments):
    # Detect spoken language for a string of comments extracted from source code
    # Input: comments (string)
    # Output: language (string) as a ISO 639-1 code (ex: 'en')

    # DetectorFactory Seed forces deterministic results on language assessment
    DetectorFactory.seed = 0
    language = "unknown" 

    try:
        # Attempt language detection
        language = detect(comments)
    except Exception as e:
        # Return "unknown" if there is not enough information to detect the language
        if e.__class__.__name__ in ['LangDetectException']:
            pass
        # Log unexpected error
        else:
            logger.info(e.__class__.__name__,"-",e)

    return language
