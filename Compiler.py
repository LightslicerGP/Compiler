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
extract_tokens = "--extract-tokens" in sys.argv
extract_tree = "--extract-tree" in sys.argv
extract_assembly = "--extract-assembly" in sys.argv
assembly_clean = "--assembly-clean" in sys.argv
extract_all = "--extract-all" in sys.argv
# output_filename = "--o" in sys.argv

# if output_filename:
#     idx = sys.argv.index("--o")
#     if idx + 1 < len(sys.argv):
#         candidate = sys.argv[idx + 1]
#         system_args = [
#             "--debug", "--extract-tokens", "--extract-tree",
#             "--extract-assembly", "--assembly-clean", "--extract-all", "--o"
#         ]
#         if candidate not in system_args:
#             final_filename = candidate + "bin"

print("Lexing...") if debug else None
tokens = lexer(file)
if extract_tokens or extract_all:
    with open("_1_tokens.json", "w") as outfile:
        json.dump(tokens, outfile, indent=2)

print("Parsing...") if debug else None
tree = parser(tokens)
if extract_tree or extract_all:
    with open("_2_tree.json", "w") as outfile:
        json.dump(tree, outfile, indent=2)

print("Generating...") if debug else None
assembly = generator(tree)
if extract_assembly or extract_all:
    with open("_3_assembly.json", "w") as outfile:
        json.dump(assembly, outfile, indent=2)

print("Done!") if debug else None

# TODO: add --assembly-clean to convert the (if --extract-assembly
# or --extract-all is enabled) assembly extract to a clean file
# TODO: add --o to specify the output filename
