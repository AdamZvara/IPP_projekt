
# stack item containing value and type property
class Stack_item:
    def __init__(self, value, type):
        self.__value = value
        self.__type = type

    @property
    def value(self):
        return self.__value

    @property
    def type(self):
        return self.__type

# stack for stack instructions
class Stack:
    def __init__(self):
        self.__stack = list()

    # pop stack item from stack
    def pop(self):
        if len(self.__stack) == 0:
            exit(56)
        return self.__stack.pop()

    # push value and its type on stack
    def push(self, value, type='int'):
        self.__stack.append(Stack_item(value, type))

    def is_empty(self):
        return len(self.__stack) == 0