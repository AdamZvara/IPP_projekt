from instruction import Instruction
from argument import Argument
from variable_manager import Variable_manager
from label import Label
from stack import Stack, Stack_item
from re import search, sub

# Class used for interpreting program
# Contains instruction objects stored in list and keeps position of currently
#   interpreted variable in internal counter instructions_pos
class Program:
    __instructions = list()
    __instructions_pos = 0
    __call_stack = list()
    __stack = Stack()
    __var_manager = Variable_manager()
    __types = ['int', 'bool', 'nil', 'string', 'float']
    __arithmetic = ['ADD', 'SUB', 'IDIV', 'MUL', 'DIV', 'ADDS', 'SUBS', 'IDIVS', 'MULS']

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

    # INSTRUCTION METHODS

    def defvar(self, arg):
        self.__var_manager.add(arg)

    def move(self, src, arg):
        arg, arg_t = self.__literal_or_variable(arg)
        self.__var_manager.insert_value(src, arg, arg_t)

    # FRAMES

    def createframe(self):
        self.__var_manager.TF_create()

    def pushframe(self):
        self.__var_manager.TF_push()

    def popframe(self):
        self.__var_manager.TF_pop()

    # DEBUG

    def dprint(self, value):
        self.__var_manager.dprint(value)

    def exit(self, arg):
        value, value_t = self.__literal_or_variable(arg)
        if (value_t != 'int'):
            exit(53)
        if value < 0 or value > 49:
                exit(57)
        exit(value)

    def type(self, var, symbol):
        for type in self.__types:
            if (symbol.type == type):
                self.__var_manager.insert_value(var, type, 'string')
        if (symbol.type == 'var'):
            self.__var_manager.insert_value(var, self.__var_manager.get_type(symbol.value), 'string')

    # INPUT OUTPUT FUNCTIONS

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
            elif arg.type == 'bool':
                if arg.value == True:
                    result='true'
                else:
                    result='false'
            else:
                result = arg.value
        print(result, end='')

    def readcheck(self, var, type):
        # check if variable exists
        self.__var_manager.get_value(var.value)
        if type.value not in ['int', 'string', 'bool', 'float']:
            exit(53)

    def read(self, var, type, user_input):
        try:
            if (user_input == None):
                raise Exception
            if (type.value == 'bool'):
                if (user_input.lower() == 'true'):
                    self.__var_manager.insert_value(var, True, 'bool')
                else:
                    self.__var_manager.insert_value(var, False, 'bool')
            elif (type.value == 'int'):
                self.__var_manager.insert_value(var, int(user_input), 'int')
            elif (type.value == 'string'):
                self.__var_manager.insert_value(var, user_input, 'string')
            elif (type.value == 'float'):
                self.__var_manager.insert_value(var, float.fromhex(user_input), 'float')
        except Exception:
            self.__var_manager.insert_value(var, 'nil', 'nil')

    # JUMP FUNCTIONS

    def jump(self, label : Argument):
        if not (label := self.label_find(label.value)):
            exit(52)
        self.__instructions_pos = label.pos

    def call(self, label : Argument):
        self.__call_stack.append(self.__instructions_pos)
        self.jump(label)

    def return_function(self):
        if (len(self.__call_stack) > 0):
            self.__instructions_pos = self.__call_stack.pop()
        else:
            exit(56)

    # STACK BASIC FUNCTIONS

    def pushs(self, arg : Argument) -> None:
        if (arg.type != 'var'):
            value = arg.value
            type = arg.type
        else:
            value = self.__var_manager.get_value(arg.value)
            type = self.__var_manager.get_type(arg.value)
        self.__stack.push(value, type)

    def pops(self, var : Argument) -> None:
        if (var.type != 'var'):
            exit(56)
        stack_item = self.__stack.pop()
        self.__var_manager.insert_value(var, stack_item.value, stack_item.type)

    # COMPARISON METHODS

    def __set_args(self, value1, value2):
        value1, value1_t, value2, value2_t = self.__pre_comparison(value1, value2)
        if value1_t != 'nil' and value2_t != 'nil':
            if value1_t != value2_t:
                exit(53)
        return (value1,value2)

    def jumpifeq(self, instruction):
        target, value1, value2 = instruction
        (value1,value2) = self.__set_args(value1, value2)
        if (value1 == value2):
            self.jump(target)

    def jumpifneq(self, instruction):
        target, value1, value2 = instruction
        (value1,value2) = self.__set_args(value1, value2)
        if (value1 != value2):
            self.jump(target)

    # ARITHMETIC FUNCTIONS

    def __set_args_arithmetics(self, op1, op2):
        allowed = ['int', 'var', 'float']
        if op1.type not in allowed or op2.type not in allowed:
            exit(53)

        val1, val1_t = self.__literal_or_variable(op1)
        val2, val2_t = self.__literal_or_variable(op2)

        if (val1 == None or val2 == None):
            exit(56)

        if val1_t != val2_t:
            exit(53)

        if type(val1) is float:
            result_type = 'float'
        else:
            result_type = 'int'
        return (val1,val2, result_type)

    def __set_args_arithmetics_stack(self):
        allowed = ['int', 'var']
        value2 = self.__stack.pop()
        value1 = self.__stack.pop()
        if value1.type not in allowed or value2.type not in allowed or type(value1.value) != type(value2.value):
            exit(53)
        return (value1.value, value2.value, 'int')

    def __arithmetics_stack(self, opcode, value1, value2):
        if opcode == 'ADDS':
            self.__stack.push(value1+value2)
        elif opcode == 'SUBS':
            self.__stack.push(value1-value2)
        elif opcode == 'MULS':
            self.__stack.push(value1*value2)
        elif opcode == 'IDIVS':
            if value2 == 0:
                exit(57)
            self.__stack.push(value1//value2)

    def __arithmetics_intfloat(self, opcode, var, value1, value2, result_type):
        if opcode == 'ADD':
            self.__var_manager.insert_value(var, value1+value2, result_type)
        elif opcode == 'SUB':
            self.__var_manager.insert_value(var, value1-value2, result_type)
        elif opcode == 'MUL':
            self.__var_manager.insert_value(var, value1*value2, result_type)
        elif opcode == 'IDIV':
            if value2 == 0:
                exit(57)
            self.__var_manager.insert_value(var, value1//value2, result_type)
        elif opcode == 'DIV':
            if type(value1) is not float or type(value2) is not float:
                exit(53)
            if value2 == 0:
                exit(57)
            self.__var_manager.insert_value(var, value1//value2, result_type)

    def arithmetic_functions(self, instruction):
        if instruction.opcode[-1] == 'S':
            (value1, value2, result_type) = self.__set_args_arithmetics_stack()
            self.__arithmetics_stack(instruction.opcode, value1, value2)
        else:
            var, operand1, operand2 = instruction
            (value1, value2, result_type) = self.__set_args_arithmetics(operand1, operand2)
            self.__arithmetics_intfloat(instruction.opcode, var, value1, value2, result_type)

    def __literal_or_variable(self, operand):
            if (operand.type == 'var'):
                value = self.__var_manager.get_value(operand.value)
                value_type = self.__var_manager.get_type(operand.value)
                if (value == None):
                    exit(56)
                return value, value_type
            else:
                return operand.value, operand.type

    # CONVERSION METHODS

    def __pre_conversion(self, value, desired_type):
        val, val_t = self.__literal_or_variable(value)
        if val == None:
            exit(56)
        elif val_t != desired_type:
            exit(53)
        return val

    def float2int(self, dst, value):
        val = self.__pre_conversion(value, 'float')
        try:
            self.__var_manager.insert_value(dst, int(val), 'int')
        except Exception:
            exit(58)

    def int2float(self, dst, value):
        val = self.__pre_conversion(value, 'int')
        try:
            self.__var_manager.insert_value(dst, float(val), 'float')
        except Exception:
            exit(58)

    def int2char(self, dst, value):
        val = self.__pre_conversion(value, 'int')
        try:
            self.__var_manager.insert_value(dst, chr(val), 'string')
        except Exception:
            exit(58)

    def stri2int(self, dst, value):
        val = self.__pre_conversion(value, 'string')
        try:
            self.__var_manager.insert_value(dst, ord(val), 'int')
        except Exception:
            exit(58)

    def __pre_conversion_stack(self, value, desired_type):
        if value == None:
            exit(56)
        elif type(value) is not desired_type:
            exit(53)
        return value

    def stri2ints(self):
        val = self.__stack.pop()
        dest = self.__stack.pop()
        val = self.__pre_conversion_stack(val.value, int)
        try:
            self.__stack.push(ord(dest.value[val]), 'int')
        except Exception:
            exit(58)

    def concat(self, dest, str1, str2):
        str1, str1_t = self.__literal_or_variable(str1)
        str2, str2_t = self.__literal_or_variable(str2)
        if (str1_t != 'string' or str2_t != 'string'):
            exit(53)
        self.__var_manager.insert_value(dest, str1+str2, 'string')

    def strlen(self, dest, string):
        string, string_t = self.__literal_or_variable(string)
        if (string_t != 'string'):
            exit(53)
        self.__var_manager.insert_value(dest, len(string), 'int')

    def getchar(self, dest, string, pos):
        string, string_t = self.__literal_or_variable(string)
        pos, pos_t = self.__literal_or_variable(pos)
        if (string_t != 'string' or pos_t != 'int'):
            exit(53)
        try:
            self.__var_manager.insert_value(dest, string[pos], 'string')
            if (pos < 0):
                raise IndexError
        except IndexError:
            exit(58)

    def setchar(self, dest, pos, new_symbol):
        dest_string = list(self.__var_manager.get_value(dest.value))
        pos, pos_t = self.__literal_or_variable(pos)
        new_symbol, ns_t = self.__literal_or_variable(new_symbol)

        if (pos_t != 'int' or ns_t != 'string'):
            exit(53)

        try:
            pos = int(pos)
            dest_string[pos] = new_symbol[0]
        except Exception:
            exit(58)
        self.__var_manager.insert_value(dest, ''.join(dest_string), 'string')

    # LOGIC FUNCTIONS

    def andfunction(self, dest, bool1, bool2):
        bool1, bool1_t = self.__literal_or_variable(bool1)
        bool2, bool2_t = self.__literal_or_variable(bool2)

        if bool1_t != 'bool' or bool2_t != 'bool':
            exit(53)

        self.__var_manager.insert_value(dest, bool1 and bool2, 'bool')

    def orfunction(self, dest, bool1, bool2):
        bool1, bool1_t = self.__literal_or_variable(bool1)
        bool2, bool2_t = self.__literal_or_variable(bool2)

        if bool1_t != 'bool' or bool2_t != 'bool':
            exit(53)

        self.__var_manager.insert_value(dest, bool1 or bool2, 'bool')

    def notfunction(self, dest, bool1):
        bool1, bool1_t = self.__literal_or_variable(bool1)

        if bool1_t != 'bool':
            exit(53)

        self.__var_manager.insert_value(dest,  not bool1, 'bool')

    # COMPARISONS

    def __pre_comparison(self, value1, value2):
        value1, value1_t = self.__literal_or_variable(value1)
        value2, value2_t = self.__literal_or_variable(value2)
        if (value1_t == 'string'):
            value1 = self.__escape_sequences(value1)
        if (value2_t == 'string'):
            value2 = self.__escape_sequences(value2)
        return value1, value1_t, value2, value2_t


    def eq(self, dest, value1, value2):
        value1, value1_t, value2, value2_t = self.__pre_comparison(value1, value2)
        if value1_t != 'nil' and value2_t != 'nil':
            if value1_t != value2_t:
                exit(53)
        self.__var_manager.insert_value(dest, value1 == value2, 'bool')

    def gt(self, dest, value1, value2):
        value1, value1_t, value2, value2_t = self.__pre_comparison(value1, value2)
        if value1_t == 'nil' or value2_t == 'nil' or value1_t != value2_t:
            exit(53)
        self.__var_manager.insert_value(dest, value1 > value2, 'bool')

    def lt(self, dest, value1, value2):
        value1, value1_t, value2, value2_t = self.__pre_comparison(value1, value2)
        if value1_t == 'nil' or value2_t == 'nil' or value1_t != value2_t:
            exit(53)
        self.__var_manager.insert_value(dest, value1 < value2, 'bool')
