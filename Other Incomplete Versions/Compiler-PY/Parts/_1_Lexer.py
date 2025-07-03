import re


regex_patterns = {
    r"( {4})+(?!\s*$)": "indentation",
    r"#.*$": "comment",
    r"\bcontinue\b": "keyword",
    r"\bnonlocal\b": "keyword",
    r"\bfinally\b": "keyword",
    r"\bassert\b": "keyword",
    r"\bexcept\b": "keyword",
    r"\bglobal\b": "keyword",
    r"\bimport\b": "keyword",
    r"\blambda\b": "keyword",
    r"\breturn\b": "keyword",
    # r"\bprint\b": "keyword",  # mabye, mabye not, its still a function name therefore a keyword so....
    r"\basync\b": "keyword",
    r"\bawait\b": "keyword",
    r"\bbreak\b": "keyword",
    r"\bclass\b": "keyword",
    r"\bFalse\b": "keyword",
    r"\braise\b": "keyword",
    r"\bwhile\b": "keyword",
    r"\byield\b": "keyword",
    r"\belif\b": "keyword",
    r"\belse\b": "keyword",
    r"\bfrom\b": "keyword",
    r"\bpass\b": "keyword",
    r"\bNone\b": "keyword",
    r"\bTrue\b": "keyword",
    r"\bwith\b": "keyword",
    r"\band\b": "keyword",
    r"\bdef\b": "keyword",
    r"\bdel\b": "keyword",
    r"\bfor\b": "keyword",
    r"\bnot\b": "keyword",
    r"\btry\b": "keyword",
    r"\bint\b": "keyword",
    r"\bstr\b": "keyword",
    r"\bbool\b": "keyword",
    r"\bbin\b": "keyword",
    r"\bfloat\b": "keyword",
    r"\bcomplex\b": "keyword",
    r"\blist\b": "keyword",
    r"\btuple\b": "keyword",
    r"\bset\b": "keyword",
    r"\bdict\b": "keyword",
    r"\bobject\b": "keyword",
    r"\btype\b": "keyword",
    r"\bas\b": "keyword",
    r"\bif\b": "keyword",
    r"\bin\b": "keyword",
    r"\bis\b": "keyword",
    r"\bor\b": "keyword",
    r"\+\+": "increment",
    r"--": "increment",
    r"\+=": "addition",
    r"-=": "subtraction",
    r"\*=": "multiplication",
    r"/=": "division",
    r"%=": "modulation",
    r"\+=": "and_assign",
    r"-=": "or_assign",
    r"\*=": "xor_assign",
    r"==": "equal",
    r"<=": "less_equal",
    r">=": "more_equal",
    r"!=": "not_equal",
    r"\(": "left_paren",
    r"\)": "right_paren",
    r"\{": "left_brace",
    r"\}": "right_brace",
    r"\[": "left_bracket",
    r"\]": "right_bracket",
    r"<": "less_than",
    r">": "more_than",
    r":": "colon",
    r";": "semicolon",
    r"\+": "addition",
    r"-": "subtraction",
    r"\*": "multiplication",
    r"/": "division",
    r"%": "modulo",
    r"=": "assign",
    r"!": "not",
    r"~": "invert",
    r"^-?\d*\.\d+": "float",
    r"^-?\d+": "integer",
    r"\.": "period",
    r",": "comma",
    r"(?:\'(?:[^\'\\]|\\.)*\'|\"(?:[^\"\\]|\\.)*\")": "string",
}


def lexer(file):

    file_content = file.read()

    tokens = []
    lines = file_content.split("\n")

    for line_number, line in enumerate(lines, 1):
        offset = 0
        while offset < len(line):
            match_found = False
            for regex, token_type in regex_patterns.items():
                match = re.match(regex, line[offset:])
                if match:
                    match_found = True
                    if token_type == "indentation":
                        tokens.append(
                            {
                                "type": token_type,
                                "value": f"{len(match.group()) // 4}",
                                "line": f"{line_number}",
                            }
                        )
                    else:
                        tokens.append(
                            {
                                "type": token_type,
                                "value": match.group(),
                                "line": f"{line_number}",
                            }
                        )
                    offset += len(match.group())
                    break

            if not match_found:  # not a standard regex, probably an identifier
                match = re.match(r"\b[A-Za-z_][A-Za-z0-9_]*\b", line[offset:])
                if match:
                    tokens.append(
                        {
                            "type": "identifier",
                            "value": match.group(),
                            "line": f"{line_number}",
                        }
                    )
                    offset += len(match.group())
                else:
                    if line[offset : offset + 1] != " ":
                        print(
                            f"WHAT IS THIS line {line_number}: ({line[offset:offset+1]}) in {line}"
                        )
                    offset += 1
        tokens.append(
            {
                "type": "newline",
                "value": "\n",
                "line": f"{line_number}",
            }
        )
    return tokens
