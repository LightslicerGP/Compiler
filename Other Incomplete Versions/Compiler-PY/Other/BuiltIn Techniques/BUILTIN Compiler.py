import tokenize
import ast
import json
from io import BytesIO

# Step 1: Read the script
script_path = "examplecode.gp"
with open(script_path, "r") as file:
    script_code = file.read()

# --- Tokenization ---
tokens = []
token_stream = tokenize.tokenize(BytesIO(script_code.encode("utf-8")).readline)

for token in token_stream:
    # Ignore encoding and end-of-file tokens
    if token.type != tokenize.ENCODING and token.type != tokenize.ENDMARKER:
        tokens.append(
            {
                "type": tokenize.tok_name[token.type],  # Human-readable token type
                "value": token.string,  # Token's actual value
                "start": token.start,  # Start position (line, column)
                "end": token.end,  # End position (line, column)
            }
        )

# Save tokens to BUILTIN tokens.json
tokens_output_path = "BUILTIN tokens.json"
with open(tokens_output_path, "w") as tokens_file:
    json.dump(tokens, tokens_file, indent=4)
print(f"Tokens saved to '{tokens_output_path}'!")

# --- Parsing ---
parsed_ast = ast.parse(script_code)  # Parse the code into an AST


# Convert AST to a dictionary for JSON serialization
def ast_to_dict(node):
    """Recursively convert an AST node to a dictionary."""
    if isinstance(node, ast.AST):
        return {
            "type": type(node).__name__,
            **{
                str(field): ast_to_dict(value)  # Ensure field names are strings
                for field, value in ast.iter_fields(node)
            },
        }
    elif isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    elif isinstance(node, tuple):
        return [
            ast_to_dict(item) for item in node
        ]  # Convert tuples to lists for JSON compatibility
    else:
        return node  # Base case for other types like strings, ints, etc.


parsed_tree = ast_to_dict(parsed_ast)

# Save parsed AST to BUILTIN tree.json
tree_output_path = "BUILTIN tree.json"
with open(tree_output_path, "w") as tree_file:
    json.dump(parsed_tree, tree_file, indent=4)
print(f"AST saved to '{tree_output_path}'!")
