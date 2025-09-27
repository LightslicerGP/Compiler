output = []
symbol_table = {}
stack_offset = 0  # will ALWAYS be 0 at the start of every functon
# registers_full = {f"r{i}": None for i in range(16)}
# registers_half = {f"r{i}{hl}": None for i in range(8) for hl in ("h", "l")}
# registers = {**registers_full, **registers_half}


class Registers:
    def __init__(self, name) -> None:
        self.name = name
        # self.purpose = None
        self.high = None
        self.low = None
        self.full = None

    # def is__upper_half_free(self):
    #     return self.high is None and self.full is None

    # def is_lower_half_free(self):
    #     return self.low is None and self.full is None

    def is_half_free(self):
        if self.low is None and self.full is None:
            return "low"
        elif self.high is None and self.full is None:
            return "high"
        else:
            return False

    def is_full_free(self):
        return self.low is None and self.high is None and self.full is None

    def set_high(self, value):
        self.high = value

    def set_low(self, value):
        self.low = value

    def set_full(self, value):
        self.high = None
        self.low = None
        self.full = value


registers = {f"r{i}": Registers(f"r{i}") for i in range(16)}


def emit(line, indent=True):
    if indent:
        line = "  " + line
    output.append(line)


def alloc_full_reg(purpose="in_use"):
    # for register in registers:
    #     if not (register.endswith("h") or register.endswith("l")):
    #         if registers[register] is None:
    #             registers[register] = purpose
    #             return register
    for register in registers:
        if registers[register].is_full_free():
            registers[register].set_full(purpose)
            return register
    for variable in symbol_table:
        # print(variable, symbol_table[variable])
        if symbol_table[variable][0] == "r":
            return symbol_table[variable]
    print("No free full register")


def alloc_half_reg(purpose="in_use"):
    # for register in registers:
    #     if register.endswith("h") or register.endswith("l"):
    #         if registers[register] is None:
    #             registers[register] = purpose
    #             return register
    for register in registers:
        if registers[register].is_half_free() == "low":
            registers[register].set_low(purpose)
            return register + "l"
        elif registers[register].is_half_free() == "high":
            registers[register].set_high(purpose)
            return register + "h"

    print("No free half register")


def generator(tree):
    for branch in tree:
        # print(branch["node"])

        if branch["node"] == "functionDefinition":
            function_name = branch["name"]
            emit(f"{function_name}:", False)
            emit("psh rbp")
            emit("mov rbp, rsp")
            # add code here to support return typed, and parameters and stuff
            # body = branch.get("body", [])
            body = branch["body"]
            generator(body)

            emit("pop bp")
            emit("rtn")
        elif branch["node"] == "variableDefinition":
            variable_name = branch["name"]
            variable_type = branch["type"]
            variable_value = branch["value"]
            # print(variable_name, symbol_table)
            if variable_name in symbol_table:
                # variable is already allocated
                variable_register = symbol_table[variable_name]
                pass
            else:
                if variable_type in ("short", "char"):
                    variable_register = alloc_half_reg(variable_name)
                else:
                    variable_register = alloc_full_reg(variable_name)
                symbol_table[variable_name] = variable_register

            if variable_value is None:
                # variable initialization
                emit(f"lod 0, {variable_register}")
            else:
                if variable_value["node"] == "literal":
                    # var = some value
                    emit(f"lod {variable_value['value']}, {variable_register}")
                else:
                    # var = some expression
                    pass

    return output


"""
# you can probably tell this is chatgpt generated
# but im gonna rewrite it all to the way i understand code
# have mercy, i'm still learning how to do this :sob:


class Register:
    def __init__(self, name):
        self.name = name
        self.purpose = None
        self.high = None
        self.low = None
        self.full = None

    def is_free(self):
        return self.low is None and self.high is None and self.full is None

    def set_high(self, int: value):
        self.high = value

    def set_low(self, int: value):
        self.low = value

    def set_full(self, int: value):
        self.high = None
        self.low = None
        self.full = value

    def get_high(self):
        return self.high

    def get_low(self):
        return self.low

    def get_full(self):
        return self.full

registers = {f"r{i}": Register(f"r{i}") for i in range(16)}


def alloc_full_register(purpose="in_use"):
    for reg in registers.values():
        if reg.is_free():
            # reg.in_use = True
            reg.purpose = purpose
            return reg.name
    raise Exception("No free full register")
# MAKE THIS SAVE A VARIABLE ELSEWHERE THEN ALLOCATE A NEW VARIABLE


def alloc_half_register(purpose="in_use"):
    for i in range(8):
        reg = registers[f"r{i}"]
        if reg.purpose is not None:
            continue
        if reg.low is None:
            reg.low = purpose
            return f"{reg.name}l"
        if reg.high is None:
            reg.high = purpose
            return f"{reg.name}h"
    raise Exception("No free 8-bit register")
# THIS SHOULD BE MODIFIED TO BE LIKE THE FULL REG VERSION


def free_register(name):
    if name in registers:
        reg = registers[name]
        if not reg.purpose is not none:
            raise Exception(f"{name} already free")
        reg.purpose = None
        reg.low = None
        reg.high = None
    elif name.endswith("l") or name.endswith("h"):
        reg_name = name[:-1]
        suffix = name[-1]
        if reg_name not in registers or int(reg_name[1:]) > 7:
            raise Exception(f"{name} is not a valid 8-bit register")
        reg = registers[reg_name]
        if suffix == "l":
            if reg.low is None:
                raise Exception(f"{name} already free")
            reg.low = None
        else:
            if reg.high is None:
                raise Exception(f"{name} already free")
            reg.high = None
        if reg.low is None and reg.high is None and not reg.in_use:
            reg.purpose = None
    else:
        raise Exception(f"Unknown register name: {name}")


symbol_table = {}

output = []


def emit(line):
    output.append(line)


def binary_op(op):
    return {"+": "add", "-": "sub", "*": "MUL", "/": "DIV"}.get(op, "UNKNOWN")


def compile_expression(expr, target=None):
    if expr["node"] == "literal":
        reg = target if target else alloc_full_register("literal")
        emit(f"lod {expr['value']}, {reg}")
        return reg

    elif expr["node"] == "binaryExpression":
        op = expr["type"]
        left = expr["left"]
        right = expr["right"]

        dest = target if target else alloc_full_register("bin_expr")

        left_reg = compile_expression(left, target=dest)

        if right["node"] == "literal":
            emit(f"{binary_op(op)} {left_reg}, {right['value']}, {left_reg}")
            return left_reg

        else:
            right_reg = compile_expression(right)
            if left_reg != dest:
                emit(f"cpy {left_reg}, {dest}")
                free_register(left_reg)
            emit(f"{binary_op(op)} {dest}, {right_reg}, {dest}")
            free_register(right_reg)
            return dest

    else:
        raise NotImplementedError(f"Unsupported expression: {expr['node']}")


def generator(tree):
    for branch in tree:
        if branch["node"] == "functionDefinition":
            function_name = branch["name"]
            emit(f"{function_name}:")

            emit("psh rbp")
            emit("mov rsp, rbp")
            # add code here to support return typed, and parameters and stuff
            # body = branch.get("body", [])
            body = branch["body"]
            generator(body)

            emit("pop bp")
            emit("rtn")

        elif branch["node"] == "variableDefinition":
            variable_name = branch["name"]

            if variable_name in symbol_table:
                variable_register = symbol_table[variable_name]
            else:
                if branch["type"] in ("short", "char"):
                    variable_register = alloc_half_register(variable_name)
                else:
                    variable_register = alloc_full_register(variable_name)
                symbol_table[variable_name] = variable_register

            expr = branch["value"]

            if expr is None:
                emit(f"lod 0, {variable_register}")
            elif expr["node"] == "literal":
                emit(f"lod {expr["value"]}, {variable_register}")
            else:
                result_reg = compile_expression(expr, target=variable_register)
                if result_reg != variable_register:
                    emit(f"cpy {result_reg}, {variable_register}")
                    free_register(result_reg)

        elif branch["node"] == "functionCall":
            # to do: arguments when calling a function
            emit(f"call {branch['name']}")

        elif branch["node"] == "return":
            value = branch["value"]
            result_reg = compile_expression(value)
            emit(f"mov {result_reg}, r0")
            free_register(result_reg)
            emit("pop bp")
            emit("ret")

        elif branch["node"] == "if":
            condition = branch["condition"]
            then_body = branch["then"]
            else_body = branch.get("else")

            label_id = len(output)
            else_label = f"else_{label_id}"
            end_label = f"endif_{label_id}"

            if condition["node"] == "binaryExpression":
                left = condition["left"]
                right = condition["right"]

                if left["node"] == "literal" and right["node"] == "literal":
                    emit(f"cmp {left['value']}, {right['value']}")
                else:
                    left_reg = compile_expression(left)
                    right_reg = compile_expression(right)
                    emit(f"cmp {left_reg}, {right_reg}")
                    free_register(left_reg)
                    free_register(right_reg)

                jump_map = {
                    "==": "jne",
                    "!=": "je",
                    "<": "jge",
                    ">": "jle",
                    "<=": "jg",
                    ">=": "jl",
                }

                jump_instr = jump_map.get(condition["type"])
                if not jump_instr:
                    raise Exception(
                        f"Unsupported if condition type: {condition['type']}"
                    )
                emit(f"{jump_instr} {else_label}")
            else:
                raise Exception("Unsupported if condition node type")

            generator(then_body)

            if else_body:
                emit(f"jmp {end_label}")
                emit(f"{else_label}:")
                generator(else_body)
                emit(f"{end_label}:")
            else:
                emit(f"{else_label}:")

    return output
"""
