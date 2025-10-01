output = []
symbol_table = {}
stack_offset = 0  # will ALWAYS be 0 at the start of every functon
label_counter = 0


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
        else:
            return False

    def is_full_free(self):
        if self.name not in Registers.fixed_registers:
            return self.low is None and self.high is None and self.full is None
        else:
            return False


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


def spill_register(register):
    global stack_offset
    for var, entry in symbol_table.items():
        if entry["location"] == register:
            stack_offset += 2  # assuming int = 2 bytes
            entry["location"] = f"[rbp-{stack_offset}]"
            entry["stack_offset"] = stack_offset
            emit(f"str {register}, [rbp-{stack_offset}]")
            registers[register].set_full(None)
            break


def get_reg_for_var(var):
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


def generator(tree):
    for branch in tree:
        # print(branch["node"])

        if branch["node"] == "functionDefinition":
            function_name = branch["name"]
            emit(f"{function_name}:", False)
            emit("psh rbp")
            emit("mov rbp, rsp")
            # add code here to support return typed, and parameters and stuff
            body = branch["body"]
            generator(body)

            emit("pop bp")
            emit("rtn")
        elif branch["node"] == "variableDeclarationList":
            for variable in branch["declarations"]:
                variable_name = variable["name"]
                variable_type = variable["type"]
                variable_value = variable["value"]
                # print(variable_name, symbol_table)
                if variable_name in symbol_table:
                    # already allocated
                    variable_entry = symbol_table[variable_name]
                    variable_register = variable_entry["location"]
                else:
                    if variable_type in ("short", "char"):
                        variable_register = alloc_half_reg(variable_name)
                    else:
                        variable_register = alloc_full_reg(variable_name)

                    # put into symbol_table in the new format
                    symbol_table[variable_name] = {
                        "location": variable_register,
                        "stack_offset": None,  # not spilled yet
                    }

                if variable_value is None:
                    emit(f"lod 0, {variable_register}")
                else:
                    if variable_value["node"] == "literal":
                        emit(f"lod {variable_value['value']}, {variable_register}")
                    else:
                        # TODO: handle expressions
                        pass

        elif branch["node"] == "while":
            global label_counter

            start_label = f"WHILE_START_{label_counter}"
            end_label = f"WHILE_END_{label_counter}"
            label_counter += 1

            emit(f"{start_label}:", False)

            cond = branch["condition"]

            # Handle literal or identifier condition
            if cond["node"] == "literal":
                if cond["value"] == "0":
                    emit(f"jmp {end_label}")
                # if literal 1, infinite loop, skip cmp
            elif cond["node"] == "identifier":
                cond_reg = get_reg_for_var(cond["value"])
                emit(f"cmp {cond_reg}, 0")
                emit(f"je {end_label}")
                # optional: free_reg(cond_reg) if temporary

            # recursive body
            generator(branch.get("body", []))

            emit(f"jmp {start_label}")
            emit(f"{end_label}:", False)

    return output
