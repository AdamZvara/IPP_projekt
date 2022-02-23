import argparse
from program import Program, Instruction
from xml_representation import XML_representation
from variable import Variable_manager

# parse given arguments from command line
parser = argparse.ArgumentParser(description='Interpret code given in XML format')
parser.add_argument('--source', help='source XML file')
parser.add_argument('--input', help='input to interpreted program')

args = parser.parse_args()
if ((args.input == None) and (args.source == None)):
    exit(10)

xml = XML_representation(args.source)
program = Program()

# Parse XML file into program object
for instruction_element in xml.get_root():
    xml.instruction_is_valid(instruction_element)
    attribute = instruction_element.attrib
    # create new instruction object to be inserted into program instructions
    instr = Instruction(attribute['opcode'], attribute['order'])
    for argument in instruction_element:
        # add arguments to instruction object
        xml.argument_is_valid(argument)
        instr.arg_add(argument)
    instr.arg_valid_amount()
    program.add_instruction(instr)

# Sort program instruction by their order and for each instruction
#   sort their arguments
program.instructions_sort()
program.create_labels()

variable_manager = Variable_manager()

def set_args(instruction):
    op1 = instruction.get_argument(1)
    op2 = instruction.get_argument(2)
    if (op1.type == 'var'):
        value1 = variable_manager.get_value(op1.value)
    else:
        value1 = op1.value
    if (op2.type == 'var'):
        value2 = variable_manager.get_value(op2.value)
    else:
        value2 = op2.value
    return (value1,value2)

# Go through each instruction in program object and interpret it
while instruction := program.get_instruction():
    opcode = instruction.get_opcode()
    if (opcode == 'DEFVAR'):
        variable_manager.add(instruction.get_argument(0))
    elif (opcode == 'WRITE'):
        variable_manager.print(instruction.get_argument(0))
        # TODO escape sequences, special characters &gt, &lt ...
    elif (opcode == 'MOVE'):
        src = instruction.get_argument(0)
        arg = instruction.get_argument(1)
        variable_manager.insert_value(src, arg.value)
    elif (opcode == 'CREATEFRAME'):
        variable_manager.TF_create()
    elif (opcode == 'PUSHFRAME'):
        variable_manager.TF_push()
    elif (opcode == 'POPFRAME'):
        variable_manager.TF_pop()
    elif (opcode == 'JUMP'):
        target = instruction.get_argument(0)
        program.jump(target)
    elif (opcode == 'JUMPIFEQ'):
        target = instruction.get_argument(0)
        (value1,value2) = set_args(instruction)
        if (value1 == value2):
            program.jump(target)
    elif (opcode == 'JUMPIFNEQ'):
        target = instruction.get_argument(0)
        if (instruction.get_argument(1) != instruction.get_argument(2)):
            program.jump(target)
    elif (opcode == 'ADD'):
        var = instruction.get_argument(0)
        (value1,value2) = set_args(instruction)
        variable_manager.insert_value(var, value1+value2)
    elif (opcode == 'SUB'):
        var = instruction.get_argument(0)
        (value1,value2) = set_args(instruction)
        variable_manager.insert_value(var, value1-value2)
    elif (opcode == 'IDIV'):
        var = instruction.get_argument(0)
        (value1,value2) = set_args(instruction)
        if value2 == 0:
            exit(57)
        variable_manager.insert_value(var, value1/value2)

    #elif (opcode == '')
    elif (opcode == 'LABEL'):
        pass
    else:
        exit(32)
    program.next_instr()

#print(program)
