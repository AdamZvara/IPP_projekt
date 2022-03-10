# Class for storing variables of interpreted program
class Variable():
    def __init__(self, whole_name : str) -> None:
        self.__frame = whole_name[:2]   # GF/TF/LF without @
        self.__name = whole_name[3:]    # actual name of variable
        self.__value = None
        self.__type = ''

    @property
    def frame(self):
        return self.__frame

    @frame.setter
    def frame(self, value):
        self.__frame = value

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        self.__value = val

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value