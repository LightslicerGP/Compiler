import json, sys
from Parts._1_Lexer import lexer
from Parts._2_Parser import parser

if len(sys.argv) < 2:
    print("Usage: python <compilerLocation>.py <filename>.c [--debug for debug mode]")
    exit(1)
else:
    file = sys.argv[1]

if len(sys.argv) > 2 and sys.argv[2] == "--debug":
    debug = True
else:
    debug = False

print("Lexing...") if debug else None
tokens = lexer(file)
with open("tokens.json", "w") as outfile:
    json.dump(tokens, outfile, indent=2)

print("Parsing...") if debug else None
tree = parser(tokens)
with open("tree.json", "w") as outfile:
    json.dump(tree, outfile, indent=2)
    
print("Done!") if debug else None