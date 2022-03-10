from instruction import Instruction
from argument import Argument
from label import Label

# Class used for interpreting program
# Contains instruction objects stored in list and keeps position of currently
#   interpreted variable in internal counter instructions_pos
class Program:
    __instructions = list()
    __instructions_pos = 0
    __call_stack = list()
    __stack = list()

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
            if instr.order == i.order:
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
        self.__labels = list()
        for pos, instruction in enumerate(self.__instructions):
            if instruction.opcode == 'LABEL':
                name = instruction.get_argument(0).value
                if self.label_find(name):
                    exit(52)
                self.__labels.append(Label(name, pos))

    # Find and return label with given name, otherwise return None
    def label_find(self, name : str) -> Label:
        for l in self.__labels:
            if l.name == name:
                return l
        return None

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
        if (arg.type == 'var'):
            self.__stack.append(arg)