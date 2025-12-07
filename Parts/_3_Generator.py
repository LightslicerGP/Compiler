import re

output = []
symbol_table = {}
stack_offset = 0  # will ALWAYS be 0 at the start of every function
label_counters = {}
optimize_assembly = True

# Track registers that are temporaries created by gen_expr (so we can free them).
# A register is "temporary" when gen_expr allocated it (literal, intermediate, cmp result).
temp_regs = set()


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


def is_reg_for_variable(reg: str):
    """
    Return True if `reg` is currently listed as the location for some
    variable in symbol_table. This prevents us from accidentally freeing
    or clobbering variable-owned registers.
    """
    for entry in symbol_table.values():
        if entry["location"] == reg:
            return True
    return False


def spill_register(register: str):
    global stack_offset
    # This still follows your original behavior: find the symbol whose
    # location equals the register, write it to the stack, update symbol_table
    for var, entry in symbol_table.items():
        if entry["location"] == register:
            stack_offset += 2  # assuming int = 2 bytes
            entry["location"] = f"[rbp-{stack_offset}]"
            entry["stack_offset"] = stack_offset
            emit(f"str {register}, [rbp-{stack_offset}]")
            # remove register from registers bookkeeping
            registers[register].set_full(None)
            # If it was a temp, also drop it from temp_regs
            temp_regs.discard(register)
            break


def get_reg_for_var(var: str):
    """
    Return a register containing var's value. If the variable currently lives
    in memory, load it into a newly allocated register *and* update symbol_table
    to reflect the new location (so the variable becomes register-resident).
    """
    entry = symbol_table[var]
    if isinstance(entry["location"], str) and entry["location"].startswith("r"):
        return entry["location"]
    else:
        reg = alloc_full_reg(var)
        emit(f"lod {entry['location']}, {reg}")
        entry["location"] = reg
        entry["stack_offset"] = None
        # Note: this is now variable-owned (we don't add to temp_regs),
        # because symbol_table points at it.
        return reg


def alloc_full_reg(purpose="in_use"):
    for register in registers:
        if registers[register].is_full_free():
            registers[register].set_full(purpose)
            return register
    # No free reg, pick one to spill (simple policy: first one)
    # Better policies possible, but this follows your prior design.
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


def free_reg(reg: str):
    """
    Free a register *only if* it is a temporary (created by gen_expr).
    Do NOT free if the register currently belongs to a variable.
    """
    # half-registers (like r1l / r1h)
    if reg.endswith("l") or reg.endswith("h"):
        base = reg[:-1]
        # If this half reg is the location of a variable don't free it.
        if is_reg_for_variable(reg):
            return
        # If it's a temporary, allow freeing
        if reg in temp_regs:
            if reg.endswith("l"):
                registers[base].low = None
            else:
                registers[base].high = None
            temp_regs.discard(reg)
        return

    # full register
    if is_reg_for_variable(reg):
        # Do not free registers that hold variables
        return

    if reg in temp_regs:
        registers[reg].set_full(None)
        temp_regs.discard(reg)
        return
    # If the register wasn't a temp, don't clobber it.


def gen_expr(node):
    """
    Generate code for an expression node and return the register
    containing the result of the expression (as a string, e.g. "r3").
    Temporaries created here are tracked in temp_regs so callers can free them safely.
    """

    # -------------------------
    # LITERAL
    # -------------------------
    if node["node"] == "literal":
        reg = alloc_full_reg("literal")
        emit(f"lod {node['value']}, {reg}")
        temp_regs.add(reg)  # this reg is a temporary
        return reg

    # -------------------------
    # IDENTIFIER
    # -------------------------
    if node["node"] == "identifier":
        # get_reg_for_var returns the register where the variable lives.
        # That register is *not* a temporary (it's in symbol_table),
        # so we don't add it to temp_regs.
        return get_reg_for_var(node["value"])

    # -------------------------
    # BINARY EXPRESSION
    # -------------------------
    if node["node"] == "binaryExpression":
        op = node["type"]
        left_node = node["left"]
        right_node = node["right"]

        left_reg = gen_expr(left_node)
        right_reg = gen_expr(right_node)

        # Arithmetic Ops --------------------------------------------
        if op == "+":
            emit(f"add {left_reg}, {right_reg}, {left_reg}")
            free_reg(right_reg)
            return left_reg

        if op == "-":
            emit(f"sub {left_reg}, {right_reg}, {left_reg}")
            free_reg(right_reg)
            return left_reg

        if op == "*":
            emit(f"mul {left_reg}, {right_reg}, {left_reg}")
            free_reg(right_reg)
            return left_reg

        if op == "/":
            emit(f"div {left_reg}, {right_reg}, {left_reg}")
            free_reg(right_reg)
            return left_reg

        # Comparison Ops ---------------------------------------------
        # Produce 0/1 boolean result in a NEW temporary register.
        # This is used when the comparison appears inside a larger expression.
        if op in (">", "<", ">=", "<=", "==", "!="):
            emit(f"cmp {left_reg}, {right_reg}")

            result = alloc_full_reg("cmp_result")
            temp_regs.add(result)  # result is a temporary

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

            # only free operand regs if they were temporaries
            free_reg(left_reg)
            free_reg(right_reg)
            return result

        raise Exception("Unknown operator: " + op)

    raise Exception("Unknown expression node type: " + node["node"])


def generator(tree):
    preoptimized_assembly = generate(tree)
    if optimize_assembly:
        # repeatedly run optimize until no changes occur
        optimized = preoptimized_assembly
        # i = 0
        while True:
            before = list(optimized)
            optimized = optimize(optimized)
            if optimized == before:
                break
            # i += 1
            # print(f"optimization pass {i}")
        return optimized
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
            if "int" in return_type:
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
                        "stack_offset": None,
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
            general structure of a while loop:
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

            # --- SPECIAL-CASE: if condition is a comparison expression,
            # use flags + a single conditional jump to the loop-end.
            if cond.get("node") == "binaryExpression" and cond.get("type") in (
                ">",
                "<",
                ">=",
                "<=",
                "==",
                "!=",
            ):
                left = cond["left"]
                right = cond["right"]

                left_reg = gen_expr(left)
                right_reg = gen_expr(right)
                emit(f"cmp {left_reg}, {right_reg}")

                # Map condition to jump-to-end when FALSE (inverse jump)
                inverse_jump = {
                    ">": "jle",
                    "<": "jge",
                    ">=": "jl",
                    "<=": "jg",
                    "==": "jne",
                    "!=": "je",
                }[cond["type"]]

                emit(f"{inverse_jump} {end_label}")

                # free only temps (don't free variable-owned regs)
                free_reg(left_reg)
                free_reg(right_reg)

            else:
                # Generic case: evaluate condition to a register and compare to 0
                reg = gen_expr(cond)
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
            emit(f"sub {target_register}, {reg}, {target_register}")
            free_reg(reg)

        elif branch["node"] == "plusAssign":
            target = branch["target"]
            value = branch["value"]
            target_register = get_reg_for_var(target)
            reg = gen_expr(value)
            emit(f"add {target_register}, {reg}, {target_register}")
            free_reg(reg)
    return output


def optimize(assembly):
    # rule of thumb: if you delete a line, dont increment i
    changed = False

    i = 0
    """
    optimize:
        lod [immediate], [regA]
        lod [regA], [regDest]
    to:
        lod [immediate] [regDest]
    """
    while i < len(assembly):

        match = re.match(r"\s*lod\s+(\d+),\s*(r\d+)", assembly[i])
        if match:
            immediate = match.group(1)
            regA_1 = match.group(2)

            if i + 1 < len(assembly):
                match2 = re.match(r"\s*lod\s+(r\d+),\s*(r\d+)", assembly[i + 1])
                if match2:
                    regA_2 = match2.group(1)
                    regDest = match2.group(2)

                    if regA_1 == regA_2:
                        assembly[i] = f"  lod {immediate}, {regDest}"
                        del assembly[i + 1]
                        changed = True
                        continue
        i += 1

    i = 0
    """
    optimize:
        lod [immediate], [regA]
        [instruction] [regB], [regA]
    to:
        [instruction] [regB] [immediate]
    """
    while i < len(assembly):

        match = re.match(r"\s*lod\s+(\d+),\s*(r\d+)", assembly[i])
        if match:
            immediate = match.group(1)
            regA_1 = match.group(2)

            if i + 1 < len(assembly):
                match2 = re.match(r"\s*([a-z]{3})\s+(r\d+),\s*(r\d+)", assembly[i + 1])
                if match2:
                    instr = match2.group(1)
                    regB = match2.group(2)
                    regA_2 = match2.group(3)

                    if regA_1 == regA_2:
                        if instr in ["add", "sub", "mul", "div"]:
                            assembly[i] = f"  {instr} {regB}, {immediate}, {regB}"
                        else:
                            assembly[i] = f"  {instr} {regB}, {immediate}"
                        del assembly[i + 1]
                        changed = True
                        continue
        i += 1

    i = 0
    """
    optimize:
        lod [regA], [regA]
    to:
        (None)
        
    and
    
    change:
        lod [regA], [regB]
    to:
        mrd [regA], [regB]
    """
    while i < len(assembly):

        match = re.match(r"\s*lod\s+(r\d+),\s*(r\d+)", assembly[i])
        if match:
            regA = match.group(1)
            regB = match.group(2)

            if regA == regB:
                del assembly[i]
                changed = True
                continue
            else:
                assembly[i] = f"  mrd {regA}, {regB}"
                changed = True
        i += 1

    i = 0
    """
    optimize:
        add [regA], [immediate0], [regA]
        sub [regA], [immediate1], [regA]
    to:
        add [regA], [immediate0 - immediate1], [regA] if [immediate0 > immediate1]
        (OR)
        sub [regA], [immediate1 - immediate0], [regA] if [immediate0 < immediate1]
        (OR)
        (None) if [immediate0 == immediate1]
    """
    while i < len(assembly):

        match = re.match(r"\s*add\s+(r\d+),\s*([0-9]+),\s*(r\d+)", assembly[i])
        if match:
            regA_1 = match.group(1)
            immediate0 = int(match.group(2))
            regA_2 = match.group(3)

            match2 = re.match(r"\s*sub\s+(r\d+),\s*([0-9]+),\s*(r\d+)", assembly[i + 1])
            if match2:
                regA_3 = match2.group(1)
                immediate1 = int(match2.group(2))
                regA_4 = match2.group(3)

                if regA_1 == regA_2 == regA_3 == regA_4:
                    if immediate0 > immediate1:
                        assembly[i] = (
                            f"  add {regA_1}, {immediate0 - immediate1}, {regA_1}"
                        )
                        del assembly[i + 1]
                        continue
                    elif immediate1 > immediate0:
                        assembly[i] = (
                            f"  sub {regA_1}, {immediate1 - immediate0}, {regA_1}"
                        )
                        del assembly[i + 1]
                        continue
                    elif immediate0 == immediate1:
                        del assembly[i + 1]
                        del assembly[i]
                        continue
        i += 1

    if changed:
        # Call recursively until no optimization occurs
        return optimize(assembly)
    else:
        return assembly
