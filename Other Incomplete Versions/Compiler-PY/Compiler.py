# import re
import json
from Parts._1_Lexer import lexer
from Parts._2_Parser import parser

# file = "Compiler.py"
file = "examplecode.py"


with open(file, "r") as file:
    tokens = lexer(file)
    with open("tokens.json", "w") as outfile:
        json.dump(tokens, outfile, indent=4)

    syntax_tree = parser(tokens)
    with open("tree.json", "w") as outfile:
        json.dump(syntax_tree, outfile, indent=4)