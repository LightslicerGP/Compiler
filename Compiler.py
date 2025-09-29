import json, sys
from Parts._1_Lexer import lexer
from Parts._2_Parser import parser
from Parts._3_Generator import generator

if len(sys.argv) < 2:
    print("Usage: python <compilerLocation>.py <filename>.c [--debug for debug mode]")
    exit(1)
else:
    file = sys.argv[1]

debug = "--debug" in sys.argv

print("Lexing...") if debug else None
tokens = lexer(file)
with open("_1_tokens.json", "w") as outfile:
    json.dump(tokens, outfile, indent=2)

print("Parsing...") if debug else None
tree = parser(tokens)
with open("_2_tree.json", "w") as outfile:
    json.dump(tree, outfile, indent=2)

print("Generating...") if debug else None
assembly = generator(tree)
with open("_3_assembly.json", "w") as outfile:
    json.dump(assembly, outfile, indent=2)

print("Done!") if debug else None
