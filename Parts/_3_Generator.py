import re

output = []
symbol_table = {}
stack_offset = 0  # will ALWAYS be 0 at the start of every functon
label_counters = {}
optimize_assembly = True


class Registers:
    fixed_registers = ["r13", "r14", "r15"]
    # registers rsp, rbp, rip

    def __init__(self, name) -> None:
        self.name = name
        self.high = None
        self.low = None
        self.full = None

    def is_half_free(self):
        if self.name not in Registers.fixed_registers:
            if self.low is None and self.full is None:
                return "low"
            elif self.high is None and self.full is None:
                return "high"
        return False

    def is_full_free(self):
        if self.name in Registers.fixed_registers:
            return False
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


def emit(line: str, indent: bool = True):
    output.append("  " + line) if indent else output.append(line)


def new_label(label_name: str):
    if label_name not in label_counters:
        label_counters[label_name] = 0
    else:
        label_counters[label_name] += 1
    return f"{label_name}{label_counters[label_name]}"


def spill_register(register: str):
    global stack_offset
    for var, entry in symbol_table.items():
        if entry["location"] == register:
            stack_offset += 2  # assuming int = 2 bytes
            entry["location"] = f"[rbp-{stack_offset}]"
            entry["stack_offset"] = stack_offset
            emit(f"str {register}, [rbp-{stack_offset}]")
            registers[register].set_full(None)
            break


def get_reg_for_var(var: int):
    entry = symbol_table[var]
    if entry["location"].startswith("r"):
        return entry["location"]
    else:
        reg = alloc_full_reg(var)
        emit(f"lod {entry['location']}, {reg}")
        entry["location"] = reg
        return reg


def alloc_full_reg(purpose="in_use"):
    for register in registers:
        if registers[register].is_full_free():
            registers[register].set_full(purpose)
            return register
    # No free reg, spill one
    reg_to_spill = next(iter(registers))
    spill_register(reg_to_spill)
    registers[reg_to_spill].set_full(purpose)
    return reg_to_spill


def alloc_half_reg(purpose="in_use"):
    for register in registers:
        if registers[register].is_half_free() == "low":
            registers[register].set_low(purpose)
            return register + "l"
        elif registers[register].is_half_free() == "high":
            registers[register].set_high(purpose)
            return register + "h"
    print("No free half register")


def free_reg(reg):
    if reg.endswith("l") or reg.endswith("h"):
        base = reg[:-1]
        if reg.endswith("l"):
            registers[base].low = None
        else:
            registers[base].high = None
        return
    registers[reg].set_full(None)


def gen_expr(node):
    if node["node"] == "literal":
        reg = alloc_full_reg("literal")
        emit(f"lod {node['value']}, {reg}")
        return reg
    if node["node"] == "identifier":
        return get_reg_for_var(node["value"])
    if node["node"] == "binaryExpression":
        op = node["type"]
        left_node = node["left"]
        right_node = node["right"]
        left_reg = gen_expr(left_node)
        right_reg = gen_expr(right_node)
        if op == "+":
            emit(f"add {left_reg}, {right_reg}")
            free_reg(right_reg)
            return left_reg
        if op == "-":
            emit(f"sub {left_reg}, {right_reg}")
            free_reg(right_reg)
            return left_reg
        if op == "*":
            emit(f"mul {left_reg}, {right_reg}")
            free_reg(right_reg)
            return left_reg
        if op == "/":
            emit(f"div {left_reg}, {right_reg}")
            free_reg(right_reg)
            return left_reg
        if op in (">", "<", ">=", "<=", "==", "!="):
            emit(f"cmp {left_reg}, {right_reg}")

            result = alloc_full_reg("cmp_result")

            true_label = new_label("EXPR_TRUE_")
            end_label = new_label("EXPR_END_")

            # default: result = 0
            emit(f"lod 0, {result}")

            # pick jump type
            if op == ">":
                emit(f"jg {true_label}")
            elif op == "<":
                emit(f"jl {true_label}")
            elif op == ">=":
                emit(f"jge {true_label}")
            elif op == "<=":
                emit(f"jle {true_label}")
            elif op == "==":
                emit(f"je {true_label}")
            elif op == "!=":
                emit(f"jne {true_label}")

            emit(f"jmp {end_label}")

            emit(f"{true_label}:", False)
            emit(f"lod 1, {result}")

            emit(f"{end_label}:", False)

            print(symbol_table)
            # free_reg(left_reg)
            # free_reg(right_reg)
            # print(symbol_table)
            return result

        raise Exception("Unknown operator: " + op)
    raise Exception("Unknown expression node type: " + node["node"])


def generator(tree):
    preoptimized_assembly = generate(tree)
    if optimize_assembly:
        return optimize(preoptimized_assembly)
    else:
        return preoptimized_assembly


def generate(tree):
    global stack_offset
    for branch in tree:
        # print(branch["node"])
        if branch["node"] == "functionDefinition":
            function_name = branch["name"]
            # label for the function
            emit(f"{function_name}:", False)
            # set up stack frame
            emit("psh rbp")
            emit("mov rsp, rbp")

            # allocate space for return value (return link)
            return_type = branch["type"]
            if "int" in return_type or "uint" in return_type:
                emit("sub rsp, 2, rsp")  #  2 bytes, 16 bits
                stack_offset += 2
            elif "short" in return_type:
                emit("sub rsp, 1, rsp")  #  1 byte, 8 bits
                stack_offset += 1

            # TODO: add code here to support parameters and stuff

            body = branch["body"]
            generate(body)

            if stack_offset > 0:
                emit(f"add rsp, {stack_offset}, rsp")
                stack_offset = 0

            # clean up stack frame
            emit("pop rbp")
            emit("rtn")
            # empty line, helps with optimization
            # later if the function is never used
            emit("", False)

        elif branch["node"] == "return":
            value = branch["value"]
            reg = gen_expr(value)
            emit(f"lod {reg}, r0")
            free_reg(reg)

        elif branch["node"] == "variableDeclarationList":
            for variable in branch["declarations"]:
                variable_name = variable["name"]
                variable_type = variable["type"]
                variable_value = variable["value"]
                # already allocated
                if variable_name in symbol_table:
                    # get register from symbol_table
                    variable_entry = symbol_table[variable_name]
                    # spill a register if it is not in a register
                    if variable_entry["stack_offset"] is not None:
                        spill_register(variable_entry["location"])
                    # set the variable register
                    variable_register = variable_entry["location"]
                # not allocated
                else:
                    # allocate a register
                    if variable_type in ("short", "char"):
                        variable_register = alloc_half_reg(variable_name)
                    else:
                        variable_register = alloc_full_reg(variable_name)

                    # put into symbol_table
                    symbol_table[variable_name] = {
                        "location": variable_register,
                        "stack_offset": None,  # not spilled yet
                    }

                # if no value, load 0
                if variable_value is None:
                    emit(f"lod 0, {variable_register}")
                else:
                    reg = gen_expr(variable_value)
                    emit(f"lod {reg}, {variable_register}")
                    free_reg(reg)

        elif branch["node"] == "variableReassignment":
            target = branch["target"]
            value = branch["value"]
            target_register = get_reg_for_var(target)
            # always use expression evaluator now
            reg = gen_expr(value)
            emit(f"lod {reg}, {target_register}")
            free_reg(reg)

        elif branch["node"] == "while":
            """
            general strucutre of a while loop:
            WHILE_START_X:
                condition (like cmp r0, 0)
                jump to WHILE_END_X if !condition (like jne)
                (while body)
                jump to WHILE_START_X
            WHILE_END_X:
            """

            # make labels
            start_label = new_label("WHILE_START_")
            end_label = new_label("WHILE_END_")

            emit(f"{start_label}:", False)

            cond = branch["condition"]

            reg = gen_expr(cond)
            # If it's a literal 0 or the value will always be 0, jump to end, skip body.
            # Otherwise compare to zero.
            emit(f"cmp {reg}, 0")
            emit(f"je {end_label}")
            free_reg(reg)

            # recursive body
            generate(branch.get("body", []))

            emit(f"jmp {start_label}")
            emit(f"{end_label}:", False)

        elif branch["node"] == "minusAssign":
            target = branch["target"]
            value = branch["value"]
            target_register = get_reg_for_var(target)
            reg = gen_expr(value)
            emit(f"sub {target_register}, {reg}")
            free_reg(reg)

        elif branch["node"] == "plusAssign":
            target = branch["target"]
            value = branch["value"]
            target_register = get_reg_for_var(target)
            reg = gen_expr(value)
            emit(f"add {target_register}, {reg}")
            free_reg(reg)
    return output


def optimize(assembly):
    # rule of thumb: if you delete a line, dont increment i
    i = 0
    while i < len(assembly):
        f"""
        optimize:
            lod [int], [regA]
            lod [regA], [regDest]
        to:
            lod [int] [regDest]
        """
        match = re.match(r"\s*lod\s+(\d+),\s*(r\d+)", assembly[i])
        if match:
            int = match.group(1)
            regA_1 = match.group(2)

            match2 = re.match(r"\s*lod\s+(r\d+),\s*(r\d+)", assembly[i + 1])
            if match2:
                regA_2 = match2.group(1)
                regDest = match2.group(2)

            if regA_1 == regA_2:
                assembly[i] = f"  lod {int}, {regDest}"
                del assembly[i + 1]

        i += 1
    return assembly
