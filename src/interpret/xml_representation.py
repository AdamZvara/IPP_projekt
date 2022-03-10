import xml.etree.ElementTree as ET
from program import Instruction
from sys import exit

# Class to encapsulate working with XML representation
# to checking validity of arguments, instructions, tags and so on
class XML_representation:

    # parse source xml file using ElementTree
    def __init__(self, source : str) -> None:
        try:
            self.tree = ET.parse(source)
            # check validity of used 'arg' tags for instructions when not in order
            self.max_args = ['arg'+str(i) for i in range(1, Instruction.get_instruction_max_args()+1)]
        except ET.ParseError:
            exit(31)
        self.__set_root()

    # Set root and check if program element tags are valid
    def __set_root(self) -> None:
        self.root = self.tree.getroot()
        if self.root.tag != 'program' or ('language','IPPcode22') not in self.root.attrib.items():
            exit(32)

    # Get program root
    def get_root(self) -> ET.Element:
        return self.root

    # Check if given instruction is in valid format
    def instruction_valid(self, instruction : ET.Element) -> None:
        if instruction.tag != 'instruction':
            exit(32)
        keys = instruction.attrib.keys()
        if 'order' not in keys or 'opcode' not in keys:
            exit(32)

    # Check if given argument is in range arg(0) .. arg(max_arg_cnt)
    def argument_valid(self, argument : ET.Element) -> None:
        if argument.tag not in self.max_args or 'type' not in argument.attrib.keys():
            exit(32)