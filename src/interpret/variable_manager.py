from sys import stderr
from argument import Argument
from variable import Variable

# Manager class to work with variables in interpreted program
class Variable_manager():
    def __init__(self) -> None:
        self.__frames = dict({'GF':list(), 'TF':list(), 'LF':list()})
        self.__local_frames_stack = list()
        self.__temp_frame_active = False
        self.__local_frame_active = False

    # Append new variable object into self.frames based on given
    # variable name
    def add(self, variable : Argument) -> None:
        var = Variable(variable.value)
        try:
            if not self.find(variable.value):
                if var.frame == 'TF' and not self.__temp_frame_active:
                    exit(55)
                self.__frames[var.frame].append(var)
            else:
                exit(52)
        except KeyError:
            exit(55)

    # Return variable object with given name otherwise return None
    def find(self, name : str) -> Variable:
        frame = name[:2]
        if (frame == 'TF' and not self.__temp_frame_active) or (frame == 'LF' and self.__local_frame_active == False):
            exit(55)
        for var in self.__frames[frame]:
            if (var.name == name[3:]):
                return var
        return None

    # Insert value into variable, if variable exists
    def insert_value(self, dest : Argument, value : any, type : str) -> None:
        if var := self.find(dest.value):
            var.value = value
            var.type = type
        else:
            exit(54)

    def get_type(self, var_name : str):
        if var := self.find(var_name):
            return var.type
        else:
            exit(54)

    def get_value(self, var_name : str) -> any:
        if var := self.find(var_name):
            return var.value
        else:
            exit(54)

    # Return variable value, which will be printed
    def print(self, arg : Argument):
        if not (var := self.find(arg.value)):
            exit(54)
        if var.type == 'string':
            result = str(var.value)
        elif var.type == 'float':
            result = float.hex(var.value)
        elif var.type == 'nil':
            result = ''
        elif var.type == 'bool':
            if (var.value == True):
                result='true'
            else:
                result='false'
        else:
            result = var.value
        return result, var.type

    def dprint(self, arg : Argument) -> None:
        if (arg.type == 'var'):
            if not (var := self.find(arg.value)):
                exit(54)
            print(var.value, end='', file=stderr)
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
            arg.frame = 'LF'
        self.__frames.update({'TF':list()})
        self.__temp_frame_active = False
        self.__local_frame_active = True

    # Move active local frame into temporary frame, pop frame
    # from local frames stack and place its variables in local frame
    def TF_pop(self):
        if self.__local_frame_active == False:
            exit(55)
        self.__frames.update({'TF': self.__frames['LF']})
        if len(self.__local_frames_stack) > 0:
            LF_stack_top = self.__local_frames_stack.pop()
        else:
            LF_stack_top = list()
            self.__local_frame_active = False
        self.__frames.update({'LF': LF_stack_top})
        for arg in self.__frames['TF']:
            arg.frame = 'TF'
        self.__temp_frame_active = True

    def exit(self, arg : Argument) -> None:
        if (arg.type == 'var'):
            if not (var := self.find(arg.value)):
                exit(54)
            value = var.value
        else:
            value = arg.value
        if value < 0 or value > 49:
                exit(57)
        exit(value)