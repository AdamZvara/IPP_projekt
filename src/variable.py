# Class for storing variables of interpreted program
# Frame (GF/LF/TF), name and value are stored for each variable
from program import Argument
from sys import stderr
import re

class Variable():
    def __init__(self, whole_name : str) -> None:
        self.__frame = whole_name[:2]   # GF/TF/LF without @
        self.__name = whole_name[3:]    # actual name of variable
        self.__value = None
        self.__type = ''

    def get_frame(self) -> str:
        return self.__frame

    def get_name(self) -> str:
        return self.__name

    def get_value(self) -> any:
        return self.__value

    def set_value(self, value : any) -> None:
        self.__value = value

    def set_type(self, type : str) -> None:
        self.__type = type

    def get_type(self) -> str:
        return self.__type

    def TF_to_LF(self) -> None:
        self.__frame = 'LF'

    def LF_to_TF(self) -> None:
        self.__frame = 'TF'

# Manager class to work with variables in interpreted program
class Variable_manager():
    def __init__(self) -> None:
        self.__frames = dict({'GF':list(), 'TF':list(), 'LF':list()})
        self.__local_frames_stack = list()
        self.__temp_frame_active = False

    # Append new variable object into self.frames based on given
    # variable name
    def add(self, variable : Argument) -> None:
        var = Variable(variable.value)
        frame = var.get_frame()
        try:
            if not self.find(variable.value):
                if frame == 'TF' and not self.__temp_frame_active:
                    exit(55)
                self.__frames[frame].append(var)
            else:
                exit(52)
        except KeyError:
            exit(55)

    # Return variable object with given name otherwise return None
    def find(self, name : str) -> Variable:
        frame = name[:2]
        if (frame == 'TF') and not self.__temp_frame_active:
            exit(55)
        for var in self.__frames[frame]:
            if (var.get_name() == name[3:]):
                return var
        return None

    # Insert value into variable, if variable exists
    def insert_value(self, dest : Argument, value : any, type : str) -> None:
        if var := self.find(dest.value):
            var.set_value(value)
            var.set_type(type)
        else:
            exit(54)

    def get_type(self, var_name : str):
        if var := self.find(var_name):
            return var.get_type()
        else:
            exit(54)

    def get_value(self, var_name : str) -> any:
        if var := self.find(var_name):
            return var.get_value()
        else:
            exit(54)

    def escape_sequences(self, string : str):
        escape_re = "\\\\[0-9][0-9][0-9]"
        matches = re.search(escape_re, string)
        if matches != None:
            for escape in matches.regs:
                escaped = chr(int(string[escape[0]+1:escape[1]]))
                string = re.sub(escape_re, escaped, string)
        return string

    # Print out value of given variable
    def print(self, arg : Argument) -> None:
        if (arg.type == 'var'):
            if not (var := self.find(arg.value)):
                exit(54)
            if var.get_type() == 'string':
                result = self.escape_sequences(str(var.get_value()))
            elif var.get_type() == 'float':
                result = float.hex(var.get_value())
            else:
                result = var.get_value()
        else:
            if (arg.type == 'string'):
                result = self.escape_sequences(str(arg.value))
            elif (arg.type == 'float'):
                result = float.hex(arg.value)
            else:
                result = arg.value
        print(result, end='')

    def dprint(self, arg : Argument) -> None:
        if (arg.type == 'var'):
            if not (var := self.find(arg.value)):
                exit(54)
            print(var.get_value(), end='', file=stderr)
        else:
            print(arg.value, end='', file=stderr)

    # Empty temporary frame (if it exists) and create new one
    def TF_create(self):
        if (self.__temp_frame_active):
            self.__frames.update({'TF':list()})
        self.__temp_frame_active = True

    # Push created temporary frame to local frame, save previous local frame in
    # local_frames_stack
    def TF_push(self):
        if not self.__temp_frame_active:
            exit(55)
        if len(self.__frames['LF']) != 0:
            self.__local_frames_stack.append(self.__frames['LF'])
        self.__frames.update({'LF':self.__frames['TF']})
        for arg in self.__frames['LF']:
            arg.TF_to_LF()
        self.__frames.update({'TF':list()})
        self.__temp_frame_active = False

    # Move active local frame into temporary frame, pop frame
    # from local frames stack and place its variables in local frame
    def TF_pop(self):
        if len(self.__local_frames_stack) == 0:
            exit(55)
        LF_stack_top = self.__local_frames_stack.pop()
        self.__frames.update({'TF': self.__frames['LF']})
        self.__frames.update({'LF': LF_stack_top})
        for arg in self.__frames['LF']:
            arg.LF_to_TF()
        self.__temp_frame_active = True

    def exit(self, arg : Argument) -> None:
        if (arg.type == 'var'):
            if not (var := self.find(arg.value)):
                exit(54)
            value = var.get_value()
        else:
            value = arg.value
        if value < 0 or value > 49:
                exit(57)
        exit(value)


