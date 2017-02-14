import io, tokenize
from altair.util.log import getLogger

logger = getLogger(__name__)

def separate_code_and_comments(script, script_id):
    """
    Tokenizes a Python script and returns 'code' and 'comments'
    Algorithm from pyminifier modified for Python 3 based on Dan McDougall's post on Stack Overflow
    Input: String representation of a Python script
    Output: code (string), comments (string)
    """
    io_obj = io.StringIO(script)
    code = ""
    comments = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0

    # Tokenize will throw syntax errors (ex: IndentationError)
    try:
        token_list = [x for x in tokenize.generate_tokens(io_obj.readline)]
    except:
        logger.info("Error tokenizing %s; skipping file" % script_id)
        return "",""

    for tok in token_list:
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        ltext = tok[4]
        inside_operator = False
        # The following two conditionals preserve indentation.
        # This is necessary because we're not using tokenize.untokenize()
        # (because it spits out code with copious amounts of oddly-placed
        # whitespace).
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            code += (" " * (start_col - last_col))
        # Add to comments
        if token_type == tokenize.COMMENT:
            comments += token_string
        # This series of conditionals identifies docstrings:
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
                # This is likely a docstring; double-check we're not inside an operator:
                if prev_toktype != tokenize.NEWLINE:
                    # Note regarding NEWLINE vs NL: The tokenize module
                    # differentiates between newlines that start a new statement
                    # and newlines inside of operators such as parens, brackes,
                    # and curly braces.  Newlines inside of operators are
                    # NEWLINE and newlines that start new code are NL.
                    # Catch whole-module docstrings:
                    if start_col > 0:
                        # Unlabelled indentation means we're inside an operator
                        code += token_string
                        inside_operator = True
                    # Note regarding the INDENT token: The tokenize module does
                    # not label indentation inside of an operator (parens,
                    # brackets, and curly braces) as actual indentation.
                    # For example:
                    # def foo():
                    #     "The spaces before this docstring are tokenize.INDENT"
                    #     test = [
                    #         "The spaces before this string do not get a token"
                    #     ]

            # If this isn't inside an operator then it's a docstring comment
            if not inside_operator:
                comments += token_string

        else:
            code += token_string

        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line

    return code,comments

