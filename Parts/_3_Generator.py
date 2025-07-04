# you can probably tell this is chatgpt generated
# but im gonna rewrite it all to the way i understand code
# have mercy, i'm still learning how to do this :sob:


class Register:
    def __init__(self, name):
        self.name = name
        self.in_use = False
        self.purpose = None
        self.low = None
        self.high = None

    def is_free(self):
        return not self.in_use and self.low is None and self.high is None


registers = {f"r{i}": Register(f"r{i}") for i in range(16)}


def get_low(name):
    return registers[name].low


def get_high(name):
    return registers[name].high


def alloc_full_register(purpose="in_use"):
    for reg in registers.values():
        if reg.is_free():
            reg.in_use = True
            reg.purpose = purpose
            return reg.name
    raise Exception("No free full register")


def alloc_half_register(purpose="in_use"):
    for i in range(8):
        reg = registers[f"r{i}"]
        if reg.in_use:
            continue
        if reg.low is None:
            reg.low = purpose
            return f"{reg.name}l"
        if reg.high is None:
            reg.high = purpose
            return f"{reg.name}h"
    raise Exception("No free 8-bit register")


def free_register(name):
    if name in registers:
        reg = registers[name]
        if not reg.in_use:
            raise Exception(f"{name} already free")
        reg.in_use = False
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
        if branch["node"] == "variableDefinition":
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
                emit(f"lod {expr['value']}, {variable_register}")
            else:
                result_reg = compile_expression(expr, target=variable_register)

                if result_reg != variable_register:
                    emit(f"cpy {result_reg}, {variable_register}")
                    free_register(result_reg)

    return output


# registers = {f"r{i}": None for i in range(16)}
# registers_hl = {f"r{i//2}{'h' if i % 2 == 0 else 'l'}": None for i in range(16)}
# register_stack = []


# def register_alloc(purpose="in_use", small=False):
#     if not small:
#         for name, value in registers.items():
#             if value is None:
#                 registers[name] = purpose
#                 if int(name[1]) < 8:
#                     registers_hl[name+"h"] = purpose + "_16Bit"
#                     registers_hl[name+"l"] = purpose + "_16Bit"
#                 return name
#         raise Exception("No register available")
#     else:
#         for name, value in registers_hl.items():
#             if value is None:
#                 registers_hl[name] = purpose
#                 if int(name.replace("h", "").replace("l", "")[1]) < 8:
#                     registers[name.replace("h", "").replace("l", "")] = purpose
#                 return name
#         raise Exception("No register available")

# def register_free(name):
#     if (name not in registers) and (name not in registers_hl):
#         raise Exception("Register not found")
#     if name in registers:
#         if registers[name] is None:
#             raise Exception("Register is not in use")
#         else:
#             registers[name] = None
#             registers_hl[name+"h"] = None
#             registers_hl[name+"l"] = None
#     elif name in registers_hl:
#         if registers_hl[name] is None:
#             raise Exception("Register is not in use")
#         else:
#             registers_hl[name] = None
#             registers[name.replace("h", "").replace("l", "")] = None
#     return True

# # print(registers, registers_hl)
# print(register_alloc("HELLOOOOOOOOO"))
# # print(registers, registers_hl)
# print(register_alloc(small=True))
# # print(registers, registers_hl)
# print(register_free("r0"))
# print(registers, registers_hl)


# registers = [
#     {"r0": None},
#     {"r1": None},
#     {"r2": None},
#     {"r3": None},
#     {"r4": None},
#     {"r5": None},
#     {"r6": None},
#     {"r7": None},
#     {"r8": None},
#     {"r9": None},
#     {"r10": None},
#     {"r11": None},
#     {"r12": None},
#     {"r13": None},
#     {"r14": None},
#     {"r15": None},
# ]
# registers_hl = [
#     {"r0h": None},
#     {"r0l": None},
#     {"r1h": None},
#     {"r1l": None},
#     {"r2h": None},
#     {"r2l": None},
#     {"r3h": None},
#     {"r3l": None},
#     {"r4h": None},
#     {"r4l": None},
#     {"r5h": None},
#     {"r5l": None},
#     {"r6h": None},
#     {"r6l": None},
#     {"r7h": None},
#     {"r7l": None},
# ]


# def register_alloc(name="in_use"):
#     for register in registers:
#         reg_name, reg_value = next(iter(register.items()))
#         if reg_value is None:
#             register[reg_name] = name  # mark as in use
#             # If register has high/low segment (r0-r7), set both high and low as in use
#             if reg_name.startswith("r") and reg_name[1].isdigit() and int(reg_name[1]) < 8:
#                 idx = int(reg_name[1])
#                 for reg_hl in registers_hl:
#                     for hl_name in reg_hl:
#                         if hl_name in (f"r{idx}h", f"r{idx}l"):
#                             reg_hl[hl_name] = name  # mark high/low as in use
#             return reg_name
#     raise Exception("No register available")


# def free_register(reg_name):
#     # Free the main register
#     found = False
#     for register in registers:
#         if reg_name in register:
#             register[reg_name] = None
#             found = True
#             break
#     if not found:
#         raise Exception(f"Register {reg_name} not found")
#     # If register has high/low segment (r0-r7), free both high and low as well
#     if reg_name.startswith("r") and reg_name[1].isdigit() and int(reg_name[1]) < 8 and len(reg_name) == 2:
#         idx = int(reg_name[1])
#         for reg_hl in registers_hl:
#             for hl_name in reg_hl:
#                 if hl_name in (f"r{idx}h", f"r{idx}l"):
#                     reg_hl[hl_name] = None
#     return True


# def generate(tree):
#     for element in tree:
#         print(element["node"])
#     return tree


# print(register_alloc())
# print(registers_hl)

# # GONNNA WORK ON THE ISA BEFORE DOING THIS
