from argument import Argument

# class containing instruction opcode, order, argument list and argument counter
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
    def arg_add(self, argument) -> None:
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
