import traceback, sys, os

tokenIndex = 0

global tokens


def currentToken(part: str = None):
    return tokens[tokenIndex] if not part else tokens[tokenIndex][part]


def eatToken():
    global tokenIndex
    tokenIndex += 2 if peekToken("type") in ["spaces", "newline"] else 1


def peekToken(part: str = None):
    idx = (
        tokenIndex + 2
        if tokens[tokenIndex + 1]["type"] in ["spaces", "newline"]
        else tokenIndex + 1
    )
    return tokens[idx][part] if part else tokens[idx]


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
        currentType = []
        while currentToken("type") == "type":
            currentType.append(currentToken("value"))
            eatToken()  # int, char, etc.

        if currentToken("type") != "identifier":
            print_error("parse() > variable type", "identifier")

        identifier = currentToken("value")
        eatToken()  # variable/function name

        match currentToken("type"):
            case "leftParen":
                return function_defenition(identifier, currentType)
            case "assign" | "semicolon" | "comma":
                return parse_variable_declaration(identifier, currentType)
            case "leftBrace":
                return structure_defenition(identifier)
            case _:
                print_error(
                    "not function def, var assign, or var init",
                    ["assign", "leftParen", "semicolon", "comma", "leftBrace"],
                )
    elif currentToken("type") == "keyword":
        match currentToken("value"):
            case "if":
                return parse_if()
            case "do":
                return parse_do()
            case "while":
                return parse_while()
            case "return":
                return parse_return()
            # add for loop
            # add switch case
            case _:
                print_error("keyword", ["if", "do", "while", "return"])
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
        elif currentToken("type") == "plusAssign":
            eatToken()  # plus assign
            expression = []
            while currentToken("type") != "semicolon":
                expression.append(currentToken())
                eatToken()  # item on the right side of expression
            eatToken()  # semicolon
            value = parseExpression(expression)
            return {"node": "plusAssign", "target": identifier, "value": value}
        elif currentToken("type") == "minusAssign":
            eatToken()  # minus assign
            expression = []
            while currentToken("type") != "semicolon":
                expression.append(currentToken())
                eatToken()  # item on the right side of expression
            eatToken()  # semicolon
            value = parseExpression(expression)
            return {"node": "minusAssign", "target": identifier, "value": value}
        else:
            print_error("not function call or var reassign", ["assign", "leftParen"])

    else:
        # print("unknown token:", currentToken())
        print_error("unknown token", "idk")
        exit(1)


def function_defenition(identifier, currentType):
    eatToken()  # leftParen

    while currentToken("type") != "rightParen":
        eatToken()  # for now, no arguments allowed

    eatToken()  # rightParen

    if currentToken("type") != "leftBrace":
        print_error("function defenition", "leftBrace")
    eatToken()  # leftBrace

    body = []
    while currentToken("type") != "rightBrace":
        body.append(parse())
    eatToken()  # rightBrace

    return {
        "node": "functionDefinition",
        "name": identifier,
        "type": currentType,
        "body": body,
    }

# TODO: fix this to support function calls
def parse_variable_declaration(identifier, currentType):
    variables = []

    while True:
        value = None
        if currentToken("type") == "assign":
            eatToken()  # equals
            expression = []
            while currentToken("type") not in ["comma", "semicolon"]:
                expression.append(currentToken())
                eatToken()  # item on the right side of expression
            value = parseExpression(expression)

        variables.append(
            {
                "node": "variableDefinition",
                "name": identifier,
                "type": currentType,
                "value": value,
            }
        )

        if currentToken("type") == "comma":
            eatToken()  # comma
            if currentToken("type") != "identifier":
                print_error("variable declaration", "identifier")
            identifier = currentToken("value")
            eatToken()  # variable name
            continue
        elif currentToken("type") == "semicolon":
            eatToken()  # semicolon
            break
        else:
            print_error("variable declaration", ["comma", "semicolon"])

    return {"node": "variableDeclarationList", "declarations": variables}


def structure_defenition(identifier):
    eatToken()  # leftBrace

    fields = []
    while currentToken("type") != "rightBrace":
        fields.append(parse())
    eatToken()  # rightBrace

    if currentToken("type") != "semicolon":
        print_error("structure_defenition()", "semicolon")
    eatToken()  # semicolon

    return {
        "node": "structDefinition",
        "name": identifier,
        "fields": fields,
    }


def function_call(identifier):
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

    eatToken()  # rightParen

    if currentToken("type") != "semicolon":
        print_error("function_call()", "semicolon")
    eatToken()  # semicolon

    return {"node": "functionCall", "name": identifier, "arguments": args}


def parse_if():
    eatToken()  # if keyword

    if currentToken("type") != "leftParen":
        print_error("parse_if()", "leftParen")
    eatToken()  # leftParen

    condition = []
    while currentToken("type") != "rightParen":
        condition.append(currentToken())
        eatToken()  # condition
    eatToken()  # rightParen
    condition = parseExpression(condition)

    if currentToken("type") != "leftBrace":
        print_error("parse_if()", "leftBrace")
    eatToken()  # leftBrace

    then = []
    while currentToken("type") != "rightBrace":
        then.append(parse())
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
            eatToken()  # rightBrace
    else:
        # no "else" statement
        or_else = None
    return {"node": "if", "condition": condition, "then": then, "else": or_else}


def parse_do():
    # if currentToken("type") != "keyword" or currentToken("value") != "do":
    #     print_error("parse_do() (do)", "'do' keyword")
    eatToken()  # do keyword

    if currentToken("type") != "leftBrace":
        print_error("parse_do() (do)", "leftBrace")
    eatToken()  # leftBrace

    body = []
    while currentToken("type") != "rightBrace":
        body.append(parse())
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
    eatToken()  # rightParen
    condition = parseExpression(condition)

    if currentToken("type") != "semicolon":
        print_error("parse_do() (while)", "semicolon")
    eatToken()  # semicolon

    return {"node": "do", "body": body, "condition": condition}


def parse_while():
    eatToken()  # while keyword

    if currentToken("type") != "leftParen":
        print_error("parse_while() (while)", "leftParen")
    eatToken()  # leftParen

    condition = []
    while currentToken("type") != "rightParen":
        condition.append(currentToken())
        eatToken()  # condition
    eatToken()  # rightParen
    condition = parseExpression(condition)

    if currentToken("type") != "leftBrace":
        print_error("parse_while() (do)", "leftBrace")
    eatToken()  # leftBrace

    body = []
    while currentToken("type") != "rightBrace":
        body.append(parse())
    eatToken()  # rightBrace

    return {"node": "while", "condition": condition, "body": body}


def parse_return():
    eatToken()  # return keyword

    expression = []
    while currentToken("type") != "semicolon":
        expression.append(currentToken())
        eatToken()  # item after return keyword
    eatToken()  # semicolon
    value = parseExpression(expression)

    return {
        "node": "return",
        "value": value,
    }


def parseExpression(tokens):
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
        token = tokens[i]
        if token["type"] == "identifier":
            left = {"node": "identifier", "value": token["value"]}
            i += 1
        elif token["type"] == "number":
            left = {"node": "literal", "value": token["value"]}
            i += 1
        elif token["type"] == "leftParen":
            left, i = parse_expr(i + 1)
            if i >= len(tokens) or tokens[i]["type"] != "rightParen":
                raise SyntaxError("Expected ')'")
            i += 1
        else:
            raise SyntaxError(f"Unexpected token: {token}")

        while i < len(tokens):
            op = tokens[i]
            if op["type"] not in precedence:
                break

            prec = precedence[op["type"]]
            if prec < min_prec:
                break

            op_type = op["value"]
            i += 1

            right, i = parse_expr(i, prec + 1)

            left = {
                "node": "binaryExpression",
                "type": op_type,
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
        "Parsing Error:",
        f"  File \"{os.path.abspath(file_path)}\", line {str(currentToken('fromLineNum'))}",
        f"{code_line}",
        " " * (currentToken("fromCharNum") - 1)
        + "^" * (currentToken("toCharNum") - currentToken("fromCharNum") + 1),
        f"error from {from_loc}, expected {expected}\n",
        traceback.format_stack()[-2],
    ]
    exit("\n".join(error))
