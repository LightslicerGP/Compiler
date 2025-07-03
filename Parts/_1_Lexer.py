charIndex = 0


def currentChar():
    return fileContents[charIndex]


def eatChar():
    global charIndex
    charIndex += 1


def peekChar():
    return fileContents[charIndex + 1]


tokens = []


def lexer(file):
    """
    file with .c extension
    """

    global fileContents

    if not file.endswith(".c"):
        raise ValueError("Input file must have a .c extension")

    with open(f"{file}", "r") as input:
        fileContents = []
        fileContents = input.read() + "\0"

    currentString = ""
    currentLineNum = 1
    currentCharNum = 1

    while currentChar() != "\0":

        if currentChar() == "\n":
            # tokens.append(
            #     {
            #         "type": "newline",
            #         "value": "\n",
            #         "fromLineNum": currentLineNum,
            #         "fromCharNum": currentCharNum,
            #         "toLineNum": currentLineNum + 1,
            #         "toCharNum": 0,
            #     }
            # )
            currentLineNum += 1
            currentCharNum = 1
            eatChar()

        elif currentChar() == "#":
            tokens.append(
                {
                    "type": "hashtag",
                    "value": "#",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == "(":
            tokens.append(
                {
                    "type": "leftParen",
                    "value": "(",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == ")":
            tokens.append(
                {
                    "type": "rightParen",
                    "value": ")",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == "{":
            tokens.append(
                {
                    "type": "leftBrace",
                    "value": "{",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == "}":
            tokens.append(
                {
                    "type": "rightBrace",
                    "value": "}",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == "[":
            tokens.append(
                {
                    "type": "leftBrack",
                    "value": "[",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == "]":
            tokens.append(
                {
                    "type": "rightBrack",
                    "value": "]",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == ",":
            tokens.append(
                {
                    "type": "comma",
                    "value": ",",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == ";":
            tokens.append(
                {
                    "type": "semicolon",
                    "value": ";",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == ".":
            tokens.append(
                {
                    "type": "period",
                    "value": ".",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum,
                }
            )
            currentCharNum += 1
            eatChar()

        elif currentChar() == "+":
            if peekChar() == "=":
                tokens.append(
                    {
                        "type": "plusAssign",
                        "value": "-=",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            elif peekChar() == "+":
                tokens.append(
                    {
                        "type": "increment",
                        "value": "++",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            else:
                tokens.append(
                    {
                        "type": "plus",
                        "value": "+",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()

        elif currentChar() == "-":
            if peekChar() == "=":
                tokens.append(
                    {
                        "type": "minusAssign",
                        "value": "-=",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            elif peekChar() == "-":
                tokens.append(
                    {
                        "type": "decrement",
                        "value": "--",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            else:
                tokens.append(
                    {
                        "type": "minus",
                        "value": "-",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()

        elif currentChar() == "*":
            if peekChar() == "=":
                tokens.append(
                    {
                        "type": "multAssign",
                        "value": "*=",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            else:
                tokens.append(
                    {
                        "type": "asterisk",
                        "value": "*",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()

        elif currentChar() == ">":
            if peekChar() == "=":
                tokens.append(
                    {
                        "type": "greatEqual",
                        "value": ">=",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            else:
                tokens.append(
                    {
                        "type": "greater",
                        "value": ">",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()

        elif currentChar() == "<":
            if peekChar() == "=":
                tokens.append(
                    {
                        "type": "lessEqual",
                        "value": "<=",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            else:
                tokens.append(
                    {
                        "type": "less",
                        "value": "<",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()

        elif currentChar() == "=":
            if peekChar() == "=":
                tokens.append(
                    {
                        "type": "equal",
                        "value": "==",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            else:
                tokens.append(
                    {
                        "type": "assign",
                        "value": "=",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()
        elif currentChar() == "!":
            if peekChar() == "=":
                tokens.append(
                    {
                        "type": "notEqual",
                        "value": "!=",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            else:
                tokens.append(
                    {
                        "type": "not",
                        "value": "!",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()
        elif currentChar() == "|":
            if peekChar() == "|":
                tokens.append(
                    {
                        "type": "logicalOr",
                        "value": "||",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            else:
                tokens.append(
                    {
                        "type": "or",
                        "value": "|",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()
        elif currentChar() == "&":
            if peekChar() == "&":
                tokens.append(
                    {
                        "type": "logicalAnd",
                        "value": "&&",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum + 1,
                    }
                )
                currentCharNum += 2
                eatChar()
                eatChar()
            else:
                tokens.append(
                    {
                        "type": "and",
                        "value": "&",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()
        elif currentChar() == "/":
            if peekChar() == "/":
                currentCharNum += 2
                eatChar()
                eatChar()
                while currentChar() != "\n":
                    currentString += currentChar()
                    eatChar()
                # tokens.append(
                #     {
                #         "type": "comment",
                #         "value": f"{currentString}",
                #         "fromLineNum": currentLineNum,
                #         "fromCharNum": currentCharNum,
                #         "toLineNum": currentLineNum,
                #         "toCharNum": currentCharNum + len(currentString) - 1,
                #     }
                # )
                currentCharNum += len(currentString)
                currentString = ""
            else:
                tokens.append(
                    {
                        "type": "slash",
                        "value": "/",
                        "fromLineNum": currentLineNum,
                        "fromCharNum": currentCharNum,
                        "toLineNum": currentLineNum,
                        "toCharNum": currentCharNum,
                    }
                )
                currentCharNum += 1
                eatChar()

        elif currentChar() == '"':
            currentCharNum += 1
            eatChar()
            while currentChar() != '"':
                currentString += currentChar()
                eatChar()
            # print("(string)", currentString)
            tokens.append(
                {
                    "type": "string",
                    "value": f"{currentString}",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum + len(currentString),
                }
            )
            currentCharNum += len(currentString) + 1
            eatChar()
            currentString = ""

        elif currentChar() == " ":
            while currentChar() == " ":
                currentString += " "
                eatChar()
            # tokens.append(
            #     {
            #         "type": "spaces",
            #         "value": len(currentString),
            #         "fromLineNum": currentLineNum,
            #         "fromCharNum": currentCharNum,
            #         "toLineNum": currentLineNum,
            #         "toCharNum": currentCharNum + len(currentString) - 1,
            #     }
            # )
            currentCharNum += len(currentString)
            currentString = ""

        elif currentChar().isnumeric():
            while currentChar().isnumeric() or currentChar() in ("x", "."):
                currentString += currentChar()
                eatChar()
            tokens.append(
                {
                    "type": "number",
                    "value": f"{currentString}",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum + len(currentString) - 1,
                }
            )
            currentCharNum += len(currentString)
            currentString = ""

        elif currentChar().isalpha() or currentChar == "_":
            while (
                currentChar().isalnum()
                or currentChar().isnumeric()
                or currentChar() == "_"
            ):
                currentString += currentChar()
                eatChar()
            currentType = ""
            if currentString in [
                "char",
                "const",
                "double",
                "enum",
                "float",
                "int",
                "long",
                "short",
                "signed",
                "struct",
                "union",
                "unsigned",
                "void",
                "volatile",
            ]:
                currentType = "type"
            elif currentString in [
                "break",
                "case",
                "continue",
                "default",
                "do",
                "else",
                "extern",
                "for",
                "goto",
                "if",
                "register",
                "return",
                "sizeof",
                "static",
                "switch",
                "typedef",
                "while",
            ]:
                currentType = "keyword"
            else:
                currentType = "identifier"

            tokens.append(
                {
                    "type": f"{currentType}",
                    "value": f"{currentString}",
                    "fromLineNum": currentLineNum,
                    "fromCharNum": currentCharNum,
                    "toLineNum": currentLineNum,
                    "toCharNum": currentCharNum + len(currentString) - 1,
                }
            )
            currentCharNum += len(currentString)
            currentString = ""

        else:
            print(f'unknown token: "{currentChar()}"')
            currentCharNum += 1
            eatChar()
    tokens.append(
        {
            "type": "eof",
            "value": "\0",
            "fromLineNum": currentLineNum,
            "fromCharNum": currentCharNum,
            "toLineNum": currentLineNum,
            "toCharNum": currentCharNum,
        }
    )
    return tokens
