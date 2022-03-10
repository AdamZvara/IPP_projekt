from instruction import Instruction
from argument import Argument
from variable_manager import Variable_manager
from label import Label
from re import search, sub

# Class used for interpreting program
# Contains instruction objects stored in list and keeps position of currently
#   interpreted variable in internal counter instructions_pos
class Program:
    __instructions = list()
    __instructions_pos = 0
    __call_stack = list()
    __stack = list()
    __var_manager = Variable_manager()
    __types = ['int', 'bool', 'nil', 'string', 'float']
    __arithmetic = ['ADD', 'SUB', 'IDIV', 'MUL', 'DIV']

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
            if i.order == instr.order:
                exit(32)
        self.__instructions.append(instr)

    # sort instructions by order and sort arguments for each instruction
    # check if each instruction has arguments in correct format
        # e.g starting <arg2> is wrong, 1st argument should be <arg1>
    def sort(self):
        self.__instructions.sort(key=lambda x: x.order)
        for instruction in self.__instructions:
            instruction.sort()
            instruction.arg_valid()

    # Iterate thourgh instructions and set labels
    def create_labels(self):
        self.__labels = list()
        for pos, instruction in enumerate(self.__instructions):
            if instruction.opcode == 'LABEL':
                name = instruction[0].value
                if self.label_find(name):
                    exit(52)
                self.__labels.append(Label(name, pos))

    # Find and return label with given name, otherwise return None
    def label_find(self, name : str) -> Label:
        for l in self.__labels:
            if l.name == name:
                return l
        return None

    @property
    def arithmetics(self):
        return self.__arithmetic

    def defvar(self, arg):
        self.__var_manager.add(arg)

    def __escape_sequences(self, string : str):
        escape_re = "\\\\[0-9][0-9][0-9]"
        matches = search(escape_re, string)
        if matches != None:
            for escape in matches.regs:
                escaped = chr(int(string[escape[0]+1:escape[1]]))
                string = sub(escape_re, escaped, string)
        return string

    def print(self, arg):
        # TODO special characters &gt, &lt ...
        if (arg.type == 'var'):
            (result,type) = self.__var_manager.print(arg)
            if (type == 'string'):
                result = self.__escape_sequences(result)
        else:
            if (arg.type == 'string'):
                result = self.__escape_sequences(str(arg.value))
            elif (arg.type == 'float'):
                result = float.hex(arg.value)
            elif (arg.type == 'nil'):
                result = ''
            else:
                result = arg.value
        print(result, end='')

    def move(self, src, arg):
        self.__var_manager.insert_value(src, arg.value, arg.type)

    def createframe(self):
        self.__var_manager.TF_create()

    def pushframe(self):
        self.__var_manager.TF_push()

    def popframe(self):
        self.__var_manager.TF_pop()

    def dprint(self, value):
        self.__var_manager.dprint(value)

    def exit(self, value):
        self.__var_manager.exit(value)

    def type(self, var, symbol):
        for type in self.__types:
            if (symbol.type == type):
                self.__var_manager.insert_value(var, type, 'string')
        if (symbol.type == 'var'):
            self.__var_manager.insert_value(var, self.__var_manager.get_type(symbol.value), 'string')

    def read(self, var, type, user_input):
        try:
            if (type.value == 'bool'):
                if (user_input.lower() == 'true'):
                    self.__var_manager.insert_value(var, 'true', 'bool')
                else:
                    self.__var_manager.insert_value(var, 'false', 'bool')
            elif (type.value == 'int'):
                self.__var_manager.insert_value(var, int(user_input), 'int')
            elif (type.value == 'string'):
                self.__var_manager.insert_value(var, user_input, 'string')
            elif (type.value == 'float'):
                self.__var_manager.insert_value(var, float.fromhex(user_input), 'float')
        except Exception:
            self.__var_manager.insert_value(var, 'nil', 'nil')

    def jump(self, label : Argument):
        if not (label := self.label_find(label.value)):
            exit(52)
        self.__instructions_pos = label.pos

    def call(self, label : Argument):
        self.__call_stack.append(self.__instructions_pos)
        self.jump(label)

    def return_function(self):
        self.__instructions_pos = self.__call_stack.pop()

    def pushs(self, arg : Argument) -> None:
        if (arg.type != 'var'):
            self.__stack.append([arg.value, arg.type])
        else:
            name = self.__var_manager.get_value(arg.value)
            type = self.__var_manager.get_type(arg.value)
            self.__stack.append(name, type)

    def pops(self, var : Argument) -> None:
        if (var.type != 'var'):
            exit(56)
        stack_item = self.__stack.pop()
        self.__var_manager.insert_value(var, stack_item[0], stack_item[1])

    def jumpifeq(self, instruction):
        target = instruction[0]
        (value1,value2) = self.set_args(instruction)
        if (value1 == value2):
            self.jump(target)

    def jumpifneq(self, instruction):
        target = instruction[0]
        (value1,value2) = self.set_args(instruction)
        if (value1 == value2):
            self.jump(target)

    def arithmetic_functions(self, instruction):
        var = instruction[0]
        (value1, value2, result_type) = self.set_args_arithmetics(instruction)
        if instruction.opcode == 'ADD':
            self.__var_manager.insert_value(var, value1+value2, result_type)
        elif instruction.opcode == 'SUB':
            self.__var_manager.insert_value(var, value1-value2, result_type)
        elif instruction.opcode == 'MUL':
            self.__var_manager.insert_value(var, value1*value2, result_type)
        elif instruction.opcode == 'IDIV':
            if value2 == 0:
                exit(57)
            self.__var_manager.insert_value(var, value1//value2, result_type)
        elif instruction.opcode == 'DIV':
            if type(value1) is not float or type(value2) is not float:
                exit(53)
            if value2 == 0:
                exit(57)
            self.__var_manager.insert_value(var, value1//value2, result_type)

    def __literal_or_variable(self, operand):
            if (operand.type == 'var'):
                return self.__var_manager.get_value(operand.value)
            else:
                return operand.value

    def set_args(self, instruction):
        value1 = self.__literal_or_variable(instruction[1])
        value2 = self.__literal_or_variable(instruction[2])
        return (value1,value2)

    def set_args_arithmetics(self, instruction):
        op1 = instruction[1]
        op2 = instruction[2]
        allowed = ['int', 'var', 'float']
        if op1.type not in allowed or op2.type not in allowed:
            exit(53)

        value1 = self.__literal_or_variable(instruction[1])
        value2 = self.__literal_or_variable(instruction[2])

        if type(value1) != type(value2):
            exit(53)

        if type(value1) is float or type(value2) is float:
            result_type = 'float'
        else:
            result_type = 'int'
        return (value1,value2, result_type)

    def float2int(self, dst, value):
        val = self.__literal_or_variable(value)
        if val == None:
            exit(56)
        elif type(val) is not float:
            exit(53)
        self.__var_manager.insert_value(dst, int(val), 'int')

    def int2float(self, dst, value):
        val = self.__literal_or_variable(value)
        if val == None:
            exit(56)
        elif type(val) is not int:
            exit(53)
        self.__var_manager.insert_value(dst, float(val), 'float')