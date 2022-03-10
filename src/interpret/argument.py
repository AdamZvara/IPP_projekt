# Argument class which contains argument type (var, int, string ...)
# and text (actual data)
class Argument:
    def __init__(self, argument) -> None:
        self.type = argument.attrib['type']
        if self.type == 'int':
            self.value = self.__to_int__(argument.text)
        elif self.type == 'float':
            self.value = self.__to_float__(argument.text)
        else:
            self.value = argument.text
        self.order = int(argument.tag[3:]) # for ordering arguments within instruction

    def __to_int__(self, value):
        try:
            return int(value)
        except ValueError:
            exit(32)

    def __to_float__(self, value):
        try:
            return float.fromhex(value)
        except ValueError:
            exit(32)

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

