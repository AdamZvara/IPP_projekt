import xml.etree.ElementTree as ET

# Argument class which contains argument type (var, int, string ...)
# and text (actual data)
class Argument:
    def __init__(self, argument : ET.Element) -> None:
        self.type = argument.attrib['type']
        if self.type == 'int':
            self.value = self.__to_int__(argument.text)
        else:
            self.value = argument.text
        self.order = int(argument.tag[3:])

    def __to_int__(self, value):
        try:
            return int(value)
        except ValueError:
            exit(53)

    def __eq__(self, other) -> bool:
        if (self.type != 'nil' and other.type != 'nil'):
            if (self.type == other.type and self.value == other.value):
                return True
            else:
                return False
        else:
            if (self.type == 'nil' and other.type == 'nil'):
                return True
            else:
                return False

# Instruction class containing instruction opcode, order, argument list
# and argument counter
class Instruction:
    __instructions = {('CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK') : 0,
                    ('DEFVAR', 'LABEL', 'WRITE', 'CALL', 'PUSHS', 'POPS', 'JUMP',
                     'EXIT', 'DPRINT') : 1,
                    ('MOVE', 'READ', 'INT2CHAR', 'STRLEN', 'TYPE') : 2,
                    ('ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND',
                     'OR', 'NOT', 'STR2INT', 'CONCAT', 'GETCHAR', 'SETCHAR',
                     'JUMPIFEQ', 'JUMPIFNEQ') : 3}

    def __init__(self, opcode : str, order : str) -> None:
        try:
            int_order = int(order)
            if (int_order < 1):
                exit(32)
        except ValueError:
            exit(32)
        self.args = list()
        self.opcode = opcode.upper()
        self.order = int_order
        self.arg_count = 0

    def get_order(self) -> int:
        return self.order

    def get_opcode(self) -> str:
        return self.opcode

    # Add new argument to objects argument list
    def arg_add(self, argument : ET.Element) -> None:
        self.args.append(Argument(argument))
        self.arg_count += 1

    # Sort arguments based on XML element <argX>
    def arg_sort(self) -> None:
        self.args.sort(key=lambda x: x.order)

    # Check if instruction has the right amount of arguments
    def arg_valid_amount(self) -> None:
        for opcodes in self.__instructions.items():
            if self.opcode in opcodes[0]:
                if self.arg_count != opcodes[1]:
                    exit(32)

    # Validate that sorted arguments begin from number 1 up to arg_count - 1
    def arg_valid(self) -> None:
        for i in range(self.arg_count):
            if (self.args[i].order != i+1):
                exit(32)

    # Fetch argument at given position
    def get_argument(self, pos : int) -> Argument:
        try:
            return self.args[pos]
        except KeyError:
            return None

    # Maximum amount of arguments in instruction based on language definition
    @classmethod
    def get_instruction_max_args(cls):
        return max(cls.__instructions.values())

    ####################### DELETE LATER #######################
    def __str__(self):
        s = "[ order="+str(self.order)+"; opcode="+self.opcode+" args:"
        if (self.arg_count != 0):
            for arg in self.args:
                s += "["+"type="+arg.type+"; value="+arg.value+"]"
            s += "]"
        return s

class Label:
    def __init__(self, name : str, pos : int) -> None:
        self.__name = name
        self.__pos = pos

    def get_name(self):
        return self.__name

    def get_pos(self):
        return self.__pos

# Class used for interpreting program
# Contains instruction objects stored in list and keeps position of currently
#   interpreted variable in internal counter instructions_pos
class Program:
    __instructions = list()
    __instructions_pos = 0
    labels = list()
    call_stack = list()

    def __init__(self):
        pass

    # Get next interpreted instruction but do not change instruction_pos
    # If there are no more instructions return None
    def get_instruction(self) -> Instruction:
        if self.__instructions_pos < len(self.__instructions):
            return self.__instructions[self.__instructions_pos]
        else:
            return None

    # Increate instructions_pos counter to interpret following instruction
    def next_instr(self) -> None:
        self.__instructions_pos += 1

    # Add instruction object to internal instruction list
    # check if instruction order was not used already
    def add_instruction(self, instr : Instruction) -> None:
        for i in self.__instructions:
            if instr.get_order() == i.get_order():
                exit(32)
        self.__instructions.append(instr)

    # sort instructions by order and sort arguments for each instruction
    # check if each instruction has arguments in correct format
        # e.g starting <arg2> is wrong, 1st argument should be <arg1>
    def instructions_sort(self):
        self.__instructions.sort(key=lambda x: x.order)
        for instruction in self.__instructions:
            instruction.arg_sort()
            instruction.arg_valid()

    # Iterate thourgh instructions and set labels
    def create_labels(self):
        for pos, instruction in enumerate(self.__instructions):
            if instruction.get_opcode() == 'LABEL':
                name = instruction.get_argument(0).value
                label = Label(name, pos)
                if self.label_find(name):
                    exit(52)
                self.labels.append(label)

    # Find and return label with given name, otherwise return None
    def label_find(self, name : str) -> Label:
        for l in self.labels:
            if l.get_name() == name:
                return l
        return None

    def jump(self, label : Argument):
        if not (label := self.label_find(label.value)):
            exit(56)
        self.__instructions_pos = label.get_pos()

    def add(self, op1 : Argument, op2 : Argument) -> int:
        pass

    ####################### DELETE LATER #######################
    def __str__(self):
        s = "Variables:\n"
        for key in self.variables:
            s += "\t"+key+": "
            for var in self.variables[key]:
                s += var
                s += ", "
            s += "\n"
        s += "\nLabels: "
        for label in self.labels:
            s += label
            s += ", "
        s += "\n"
        for inst in self.__instructions:
            s += str(inst)
            s += "\n"
        return s
