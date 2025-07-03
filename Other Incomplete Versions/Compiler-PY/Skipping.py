from tree_sitter import Language, Parser

Language.build_library("build/my-languages.so", ["tree-sitter-c"])

C_LANGUAGE = Language("build/my-languages.so", "c")
parser = Parser()
parser.set_language(C_LANGUAGE)

with open("temp.c", "rb") as f:
    code = f.read()

tree = parser.parse(code)
print(tree.root_node.sexp())  # prints the full syntax tree
