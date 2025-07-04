import traceback, sys, os

tokenIndex = 0

global tokens


def currentToken(part: str = None):
    if not part:
        return tokens[tokenIndex]
    else:
        return tokens[tokenIndex][part]


def eatToken():
    global tokenIndex
    if peekToken("type") in ["spaces", "newline"]:
        tokenIndex += 2
    else:
        tokenIndex += 1


def peekToken(part: str = None):
    if tokens[tokenIndex + 1]["type"] in ["spaces", "newline"]:
        if part:
            return tokens[tokenIndex + 2][part]
        else:
            return tokens[tokenIndex + 2]
    else:
        if part:
            return tokens[tokenIndex + 1][part]
        else:
            return tokens[tokenIndex + 1]


def parser(input_tokens):
    """
    tokens are in an array
    """

    global tokens
    tokens = input_tokens

    tree = []

    while currentToken("type") != "eof":
        tree.append(parse())
    return tree


def parse():
    if currentToken("type") == "type":
        currentType = currentToken("value")
        eatToken()  # int, char, etc.

        if currentToken("type") != "identifier":
            print_error("parse() > variable type", "identifier")

        identifier = currentToken("value")
        eatToken()  # variable/function name

        if currentToken("type") == "leftParen":
            return function_defenition(identifier, currentType)

        elif currentToken("type") == "assign":
            return variable_defenition(identifier, currentType)

        elif currentToken("type") == "semicolon":
            return variable_initialization(identifier, currentType)

        else:
            print_error(
                "not function def, var assign, or var init",
                ["assign", "leftParen", "semicolon"],
            )
    elif currentToken("type") == "keyword":
        match currentToken("value"):
            case "if":
                return parse_if()
            case "do":
                return parse_do()
            case "while":
                return parse_while()
    elif currentToken("type") == "identifier":
        identifier = currentToken("value")
        eatToken()  # variable/function name

        if currentToken("type") == "leftParen":
            return function_call(identifier)
        elif currentToken("type") == "assign":
            # variable reassignment
            eatToken()  # equals

            expression = []
            while currentToken("type") != "semicolon":
                expression.append(currentToken())
                eatToken()  # item on the right side of expression
            if currentToken("type") != "semicolon":
                print_error("variable reassignment", "semicolon")
            eatToken()  # semicolon
            expression = parseExpression(expression)

            return {
                "node": "variableReassignment",
                "target": identifier,
                "value": expression,
            }
        # implement increment and decrement before? someday? 7/2/25
        elif currentToken("type") == "increment":
            eatToken()  # increment
            if currentToken("type") != "semicolon":
                print_error("variable increment", "semicolon")
            eatToken()  # semicolon
            return {"node": "increment", "target": identifier}
        elif currentToken("type") == "decrement":
            eatToken()  # decrement
            if currentToken("type") != "semicolon":
                print_error("variable decrement", "semicolon")
            eatToken()  # semicolon
            return {"node": "decrement", "target": identifier}
        else:
            print_error("not function call or var reassign", ["assign", "leftParen"])

    else:
        print("unknown token:", currentToken())
        exit(1)


def function_defenition(identifier, currentType):
    if currentToken("type") != "leftParen":
        print_error("function_defenition()", "leftParen")
    eatToken()  # leftParen

    while currentToken("type") != "rightParen":
        eatToken()  # for now, no arguments allowed

    if currentToken("type") != "rightParen":
        print_error("function_defenition()", "rightParen")
    eatToken()  # rightParen

    if currentToken("type") != "leftBrace":
        print_error("function defenition", "leftBrace")
    eatToken()  # leftBrace

    body = []
    while currentToken("type") != "rightBrace":
        body.append(parse())
    if currentToken("type") != "rightBrace":
        print_error("function_defenition()", "rightBrace")
    eatToken()  # rightBrace

    return {
        "node": "functionDefinition",
        "name": identifier,
        "type": currentType,
        "body": body,
    }


def variable_defenition(identifier, currentType):
    if currentToken("type") != "assign":
        print_error("variable_defenition()", "assign")
    eatToken()  # equals

    expression = []
    while currentToken("type") != "semicolon":
        expression.append(currentToken())
        eatToken()  # item on the right side of expression
    if currentToken("type") != "semicolon":
        print_error("variable reassignment", "semicolon")
    eatToken()  # semicolon
    value = parseExpression(expression)

    return {
        "node": "variableDefinition",
        "name": identifier,
        "type": currentType,
        "value": value,
    }


def variable_initialization(identifier, currentType):
    if currentToken("type") != "semicolon":
        print_error("variable_initialization()", "semicolon")
    eatToken()  # semicolon
    return {
        "node": "variableDefinition",  # rename? idk
        "name": identifier,
        "type": currentType,
        "value": None,
    }


def function_call(identifier):
    if currentToken("type") != "leftParen":
        print_error("function_call()", "leftParen")
    eatToken()  # leftParen

    args = []

    while currentToken("type") != "rightParen":
        token = currentToken()
        if token["type"] == "string":
            args.append({"node": "literal", "value": token["value"]})
            eatToken()

        elif token["type"] == "number":
            args.append({"node": "literal", "value": token["value"]})
            eatToken()

        elif token["type"] == "identifier":
            args.append({"node": "identifier", "value": token["value"]})
            eatToken()

        else:
            print_error("function_call() argument", ["string", "number", "identifier"])

        if currentToken("type") == "comma":
            eatToken()
        elif currentToken("type") == "rightParen":
            break
        else:
            print_error("function_call() after argument", ["comma", "rightParen"])

    if currentToken("type") != "rightParen":
        print_error("function_call()", "rightParen")
    eatToken()  # rightParen

    if currentToken("type") != "semicolon":
        print_error("function_call()", "semicolon")
    eatToken()  # semicolon

    return {"node": "functionCall", "name": identifier, "arguments": args}


def parse_if():
    if currentToken("type") != "keyword" or currentToken("value") != "if":
        print_error("parse_if()", "'if' keyword")
    eatToken()  # if keyword

    if currentToken("type") != "leftParen":
        print_error("parse_if()", "leftParen")
    eatToken()  # leftParen

    condition = []
    while currentToken("type") != "rightParen":
        condition.append(currentToken())
        eatToken()  # condition
    if currentToken("type") != "rightParen":
        print_error("parse_if()", "rightParen")
    eatToken()  # rightParen
    condition = parseExpression(condition)

    if currentToken("type") != "leftBrace":
        print_error("parse_if()", "leftBrace")
    eatToken()  # leftBrace

    then = []
    while currentToken("type") != "rightBrace":
        then.append(parse())
    if currentToken("type") != "rightBrace":
        print_error("parse_if()", "rightBrace")
    eatToken()  # rightBrace

    if currentToken("type") == "keyword" and currentToken("value") == "else":
        # "else" statement exists
        eatToken()  # else keyword
        if currentToken("type") == "keyword" and currentToken("value") == "if":
            # "else if" statement exists
            or_else = [parse_if()]
        else:
            # just the "else" statement
            or_else = []
            if currentToken("type") != "leftBrace":
                print_error("parse_if() (else)", "leftBrace")
            eatToken()  # leftBrace

            while currentToken("type") != "rightBrace":
                or_else.append(parse())
            if currentToken("type") != "rightBrace":
                print_error("parse_if() (else)", "rightBrace")
            eatToken()  # rightBrace
    else:
        # no "else" statement
        or_else = None
    return {"node": "if", "condition": condition, "then": then, "else": or_else}


def parse_do():
    if currentToken("type") != "keyword" or currentToken("value") != "do":
        print_error("parse_do() (do)", "'do' keyword")
    eatToken()  # do keyword

    if currentToken("type") != "leftBrace":
        print_error("parse_do() (do)", "leftBrace")
    eatToken()  # leftBrace

    body = []
    while currentToken("type") != "rightBrace":
        body.append(parse())
    if currentToken("type") != "rightBrace":
        print_error("parse_do() (do)", "rightBrace")
    eatToken()  # rightBrace

    if currentToken("type") != "keyword" or currentToken("value") != "while":
        print_error("parse_do() (while)", "'while' keyword")
    eatToken()  # while keyword

    if currentToken("type") != "leftParen":
        print_error("parse_do() (while)", "leftParen")
    eatToken()  # leftParen

    condition = []
    while currentToken("type") != "rightParen":
        condition.append(currentToken())
        eatToken()  # condition
    if currentToken("type") != "rightParen":
        print_error("parse_do() (while)", "rightParen")
    eatToken()  # rightParen
    condition = parseExpression(condition)

    if currentToken("type") != "semicolon":
        print_error("parse_do() (while)", "semicolon")
    eatToken()  # semicolon

    return {"node": "do", "body": body, "condition": condition}


def parse_while():

    if currentToken("type") != "keyword" or currentToken("value") != "while":
        print_error("parse_while() (while)", "'while' keyword")
    eatToken()  # while keyword

    if currentToken("type") != "leftParen":
        print_error("parse_while() (while)", "leftParen")
    eatToken()  # leftParen

    condition = []
    while currentToken("type") != "rightParen":
        condition.append(currentToken())
        eatToken()  # condition
    if currentToken("type") != "rightParen":
        print_error("parse_while() (while)", "rightParen")
    eatToken()  # rightParen
    condition = parseExpression(condition)

    if currentToken("type") != "leftBrace":
        print_error("parse_while() (do)", "leftBrace")
    eatToken()  # leftBrace

    body = []
    while currentToken("type") != "rightBrace":
        body.append(parse())
    if currentToken("type") != "rightBrace":
        print_error("parse_while() (do)", "rightBrace")
    eatToken()  # rightBrace

    return {"node": "while", "condition": condition, "body": body}


def parseExpression(tokens):
    # Operator precedence (higher = binds tighter)
    precedence = {
        "logicalOr": 1,  # ||
        "logicalAnd": 2,  # &&
        "equal": 3,  # ==
        "notEqual": 3,  # !=
        "greater": 4,  # >
        "greatEqual": 4,  # >=
        "less": 4,  # <
        "lessEqual": 4,  # <=
        "plus": 5,  # +
        "minus": 5,  # -
        "asterisk": 6,  # *
        "slash": 6,  # /
    }

    def parse_expr(i, min_prec=0):
        # Get the left operand
        token = tokens[i]
        if token["type"] == "identifier":
            left = {"node": "identifier", "value": token["value"]}
        elif token["type"] == "number":
            left = {"node": "literal", "value": token["value"]}
        elif token["type"] == "leftParen":
            left, i = parse_expr(i + 1)
            if tokens[i]["type"] != "rightParen":
                raise SyntaxError("Expected ')'")
            i += 1
        else:
            raise SyntaxError(f"Unexpected token: {token}")
        i += 1

        # Process binary operators
        while i < len(tokens):
            op = tokens[i]
            if op["type"] not in precedence:
                break

            prec = precedence[op["type"]]
            if prec < min_prec:
                break

            i += 1  # Consume operator
            right, i = parse_expr(i, prec + 1)

            left = {
                "node": "binaryExpression",
                "type": op["value"],  # e.g., "+", "==", "&&"
                "left": left,
                "right": right,
            }

        return left, i

    ast, _ = parse_expr(0)
    return ast


def print_error(
    from_loc: str,
    expected=None,
):
    if isinstance(expected, list):
        expected = " or ".join(expected)
    elif expected == None:
        expected = "not type " + currentToken("type")

    file_path = sys.argv[1]
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    code_line = lines[currentToken("fromLineNum") - 1].rstrip("\n")

    error = [
        "Compiling Error:",
        f"  File \"{os.path.abspath(file_path)}\", line {str(currentToken('fromLineNum'))}",
        f"{code_line}",
        " " * (currentToken("fromCharNum") - 1)
        + "^" * (currentToken("toCharNum") - currentToken("fromCharNum") + 1),
        f"error from {from_loc}, expected {expected}",
        "".join(traceback.format_stack()),
    ]
    exit("\n".join(error))
