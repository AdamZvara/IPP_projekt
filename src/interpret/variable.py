# Class for storing variables of interpreted program
# Frame (GF/LF/TF), name and value are stored for each variable
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




