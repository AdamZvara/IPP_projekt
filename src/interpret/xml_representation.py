import xml.etree.ElementTree as ET
from program import Instruction

# Class to encapsulate working with XML representation
# checking validity of arguments, instructions, tags etc ...
# max_arg_cnt is required to check validity of used XML attributes for arguments
class XML_representation:
    def __init__(self, source : str) -> None:
        try:
            self.tree = ET.parse(source)
            self.max_args = ['arg'+str(i) for i in range(1, Instruction.get_instruction_max_args()+1)]
        except ET.ParseError:
            exit(31)
        self._xml_valid()

    # Set root and check if program element tags are valid
    def _xml_valid(self) -> None:
        self.root = self.tree.getroot()
        if (self.root.tag != 'program' or ('language','IPPcode22') not in self.root.attrib.items()):
            exit(32)

    # Get program root
    def get_root(self) -> ET.Element:
        return self.root

    # Check if given instruction is in valid format
    def instruction_is_valid(self, instruction : ET.Element) -> None:
        if (instruction.tag != 'instruction'):
            exit(32)
        keys = instruction.attrib.keys()
        if ('order' not in keys or 'opcode' not in keys):
            exit(32)

    # Check if given argument is in range arg(0) .. arg(max_arg_cnt)
    def argument_is_valid(self, argument : ET.Element) -> None:
        if (argument.tag not in self.max_args):
            exit(32)
        if ('type' not in argument.attrib.keys()):
            exit(32)

