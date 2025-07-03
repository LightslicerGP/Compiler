tokens = []
token_index = 0


def current_token():
    if token_index < len(tokens):
        return tokens[token_index]
    return None


def next_token():
    global token_index
    if token_index < len(tokens):
        token_index += 1


def peek_token():
    if token_index + 1 < len(tokens):
        return tokens[token_index + 1]
    return None


def parser(input_tokens):
    global tokens
    tokens = input_tokens
    parse_tree = []

    while current_token() is not None:
        parse_tree.append(parse_statement())
    if parse_tree and parse_tree[-1] == []: # removes the [] when theres a final \n
        parse_tree.pop()
    return parse_tree


def parse_statement(current_level: int = 0):
    tree = []

    if current_token()["type"] == "keyword":
        if current_token()["value"] == "if":
            tree = parse_if(current_level)
        elif current_token()["value"] == "def":
            tree = parse_function_declaration(current_level)
        elif current_token()["value"] == "return":
            tree = parse_return()
    elif current_token()["type"] == "identifier":
        if peek_token()["type"] == "left_paren":
            tree = parse_function_call()
        elif peek_token()["type"] == "assign":
            tree = parse_var_assign()
    elif current_token()["type"] == "indentation" and peek_token()["type"] in (
        "comment",
        "newline",
    ):
        next_token()
        next_token()
    elif current_token()["type"] == "comment":
        next_token()
        tree = parse_statement(current_level)
    elif current_token()["type"] == "newline":
        if peek_token() == None: # this is the final \n
            next_token()
            return tree
        else:
            next_token()
            tree = parse_statement(current_level)
    else:
        print("not a accounted token", current_token())
        print("peeking:", peek_token())
        next_token()

    if tree == []:
        print("tree is empty", current_token(), peek_token())
    return tree


def parse_if(current_level: int):
    if_tree = {"if": {"condition": {}, "then": []}}
    next_token()  # pop "if"

    if current_token()["type"] not in ("integer", "identifier"):
        raise ValueError("Expected an integer or identifier", current_token())
    if peek_token()["type"] not in (
        "equal",
        "less_than",
        "more_than",
        "less_equal",
        "more_equal",
        "not_equal",
    ):
        raise ValueError("Expected a comparison operator", current_token())

    left_value = (
        int(current_token()["value"])
        if current_token()["value"].isdigit()
        else current_token()["value"]
    )
    left = {f"{current_token()['type']}": left_value}
    next_token()

    operator_type = f"{current_token()['type']}"
    next_token()

    right_value = (
        int(current_token()["value"])
        if current_token()["value"].isdigit()
        else current_token()["value"]
    )
    right = {f"{current_token()['type']}": right_value}
    next_token()

    if_tree["if"]["condition"] = {
        "type": operator_type,
        "left": left,
        "right": right,
    }

    if current_token()["type"] != "colon":
        raise ValueError("Expected a colon", current_token())

    next_token()  # the colon

    if current_token()["type"] != "newline":
        raise ValueError("Expected a newline", current_token())

    next_token()  # the newline

    if current_token()["type"] != "indentation":
        raise ValueError("Expected an indentation", current_token())

    indentation_level = int(current_token()["value"])
    if indentation_level <= current_level:
        raise ValueError(
            "Indentation level must be greater for the 'then' block", current_token()
        )

    next_token()  # the indentation

    # Parse the 'then' block until indentation decreases or ends
    while current_token() is not None:
        if current_token()["type"] == "indentation":
            new_indentation_level = int(current_token()["value"])
            next_token()
            if new_indentation_level <= current_level:
                break  # End of 'then' block
        if_tree["if"]["then"].append(parse_statement(indentation_level))
    return if_tree


def parse_expression():  # cant do x = a + y * z correctly
    token = current_token()
    expression_tree = {}
    if token["type"] == "integer":
        value = int(token["value"])
        next_token()  # Move past the integer
        expression_tree = {"integer": value}
    elif token["type"] == "string":
        value = token["value"]
        next_token()  # Move past the string
        expression_tree = {"string": value}
    elif token["type"] == "identifier":
        value = token["value"]
        next_token()  # Move past the identifier
        expression_tree = {"variable": value}
    else:
        raise ValueError(
            f"Unexpected token type in expression: {token['type']}", current_token()
        )

    if current_token() is not None and current_token()["type"] in (
        "addition",
        "subtraction",
        "multiplication",
        "division",
    ):
        operator = current_token()["type"]
        next_token()  # Move past the operator

        right_expr = parse_expression()  # Parse the right-hand side expression
        left_expr = expression_tree
        expression_tree = {
            "binary_operation": {
                "operator": operator,
                "left": left_expr,
                "right": right_expr,
            }
        }

    return expression_tree


def parse_function_call():
    if current_token()["type"] != "identifier":
        raise ValueError("Expected a function name as an identifier", current_token())

    function_name = current_token()["value"]
    function_call_tree = {"function_call": {"name": function_name, "parameters": []}}

    next_token()  # Move past the function name

    if current_token()["type"] != "left_paren":
        raise ValueError("Expected '(' for function call", current_token())

    next_token()  # Move past '('

    # Parse parameters inside parentheses
    while current_token() is not None and current_token()["type"] != "right_paren":
        param = parse_expression()
        if param:
            function_call_tree["function_call"]["parameters"].append(param)

        if current_token()["type"] == "comma":
            next_token()  # Skip comma between parameters

    if current_token()["type"] != "right_paren":
        raise ValueError("Expected ')' to close function call", current_token())

    next_token()  # Move past ')'

    next_token() if current_token()["type"] == "newline" else None

    return function_call_tree


def parse_function_declaration(current_level: int):
    if not (current_token()["value"] == "def" and current_token()["type"] == "keyword"):
        raise ValueError(
            "Expected 'def' keyword for function declaration", current_token()
        )

    next_token()  # Skip the 'def' keyword

    if current_token()["type"] != "identifier":
        raise ValueError("Expected a function name after 'def'", current_token())

    function_name = current_token()["value"]
    function_tree = {
        "function_declaration": {"name": function_name, "parameters": [], "body": []}
    }

    next_token()  # Move past the function name

    if current_token()["type"] != "left_paren":
        raise ValueError("Expected '(' after function name", current_token())

    next_token()  # Move past '('

    # Parse parameters inside parentheses
    while current_token() is not None and current_token()["type"] != "right_paren":
        if current_token()["type"] != "identifier":
            raise ValueError(
                "Expected a parameter name in function declaration", current_token()
            )

        function_tree["function_declaration"]["parameters"].append(
            current_token()["value"]
        )
        next_token()  # Move past the parameter name

        if current_token()["type"] == "comma":
            next_token()  # Skip commas between parameters

    if current_token()["type"] != "right_paren":
        raise ValueError("Expected ')' to close parameter list", current_token())

    next_token()  # Move past ')'

    if current_token()["type"] != "colon":
        raise ValueError("Expected ':' after parameter list", current_token())

    next_token()  # Skip the colon

    if current_token()["type"] != "newline":
        raise ValueError(
            "Expected a newline after function declaration header", current_token()
        )

    next_token()  # Skip the newline

    if current_token()["type"] != "indentation":
        raise ValueError(
            "Expected an indentation block for function body", current_token()
        )

    indentation_level = int(current_token()["value"])
    if indentation_level <= current_level:
        raise ValueError(
            "Indentation level must be greater for the function body", current_token()
        )

    next_token()  # Move past the indentation

    # Parse the function body until indentation decreases or ends
    while current_token() is not None:
        if current_token()["type"] == "newline":
            break
        if current_token()["type"] == "indentation":
            new_indentation_level = int(current_token()["value"])
            next_token()  # Move past indentation
            if new_indentation_level <= current_level:
                break  # End of function body
        function_tree["function_declaration"]["body"].append(
            parse_statement(indentation_level)
        )

    return function_tree


def parse_return():
    if not (
        current_token()["type"] == "keyword" or current_token()["value"] == "return"
    ):
        raise ValueError("Expected 'return' keyword", current_token())

    next_token()  # Skip 'return'

    # Parse the return expression
    expression = parse_expression()
    if current_token()["type"] == "newline":
        next_token()
    return {"return": expression}


def parse_var_assign():
    # Ensure the current token is an identifier
    if current_token()["type"] != "identifier":
        raise ValueError("Expected a variable name for assignment", current_token())

    variable_name = current_token()["value"]
    next_token()  # Move past the variable name

    # Ensure the next token is an assignment operator
    if current_token()["type"] != "assign":
        raise ValueError("Expected '=' for assignment", current_token())

    next_token()  # Move past the assignment operator

    # Parse the right-hand side expression or function call
    if current_token()["type"] == "identifier" and peek_token()["type"] == "left_paren":
        value = parse_function_call()
    else:
        value = parse_expression()

    if current_token()["type"] == "newline":
        next_token()

    return {"variable_assign": {"name": variable_name, "value": value}}
