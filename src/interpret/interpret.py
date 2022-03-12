from program import Program, Instruction
from xml_representation import XML_representation
from variable_manager import Variable_manager
from input import Input
from sys import exit

input_files = Input()
xml = XML_representation(input_files.get_source())
program = Program()

# Parse XML file into program object
for instruction_element in xml.get_root():
    xml.instruction_valid(instruction_element)
    attribute = instruction_element.attrib
    # create new instruction object to be inserted into program instructions
    instr = Instruction(attribute['opcode'], attribute['order'])
    for argument in instruction_element:
        xml.argument_valid(argument)
        instr.newarg(argument)
    instr.arg_valid_amount()
    program.add_instruction(instr)

# Sort program instruction by their order and for each instruction
#   sort their arguments
program.sort()
program.create_labels()

# Go through each instruction in program object and interpret it
while instruction := program.get_instruction():
    opcode = instruction.opcode
    if (opcode == 'DEFVAR'):
        program.defvar(instruction[0])
    elif (opcode == 'WRITE'):
        program.print(instruction[0])
    elif (opcode == 'MOVE'):
        program.move(instruction[0], instruction[1])
    elif (opcode == 'CREATEFRAME'):
        program.createframe()
    elif (opcode == 'PUSHFRAME'):
        program.pushframe()
    elif (opcode == 'POPFRAME'):
        program.popframe()
    elif (opcode == 'JUMP'):
        program.jump(instruction[0])
    elif (opcode == 'JUMPIFEQ'):
        program.jumpifeq(instruction)
    elif (opcode == 'JUMPIFNEQ'):
        program.jumpifneq(instruction)
    elif (opcode in program.arithmetics):
        program.arithmetic_functions(instruction)
    elif (opcode == 'DPRINT'):
        program.dprint(instruction[0])
    elif (opcode == 'EXIT'):
        program.exit(instruction[0])
    elif (opcode == 'TYPE'):
        program.type(instruction[0], instruction[1])
    elif (opcode == 'CALL'):
        program.call(instruction[0])
    elif (opcode == 'RETURN'):
        program.return_function()
    elif (opcode == 'READ'):
        user_input = input_files.get_input_line()
        program.read(instruction[0], instruction[1], user_input)
    elif (opcode == 'PUSHS'):
        program.pushs(instruction[0])
    elif (opcode == 'POPS'):
        program.pops(instruction[0])
    elif (opcode == 'FLOAT2INT'):
        program.float2int(instruction[0], instruction[1])
    elif (opcode == 'INT2FLOAT'):
        program.int2float(instruction[0], instruction[1])
    elif (opcode == 'INT2CHAR'):
        program.int2char(instruction[0], instruction[1])
    elif (opcode == 'STRI2INT'):
        program.stri2int(instruction[0], instruction[1])
    elif (opcode == 'STRI2INTS'):
        program.stri2ints()
    elif (opcode == 'CONCAT'):
        program.concat(instruction[0], instruction[1], instruction[2])
    elif (opcode == 'STRLEN'):
        program.strlen(instruction[0], instruction[1])
    elif (opcode == 'GETCHAR'):
        program.getchar(instruction[0], instruction[1], instruction[2])
    elif (opcode == 'SETCHAR'):
        program.setchar(instruction[0], instruction[1], instruction[2])
    elif (opcode == 'AND'):
        program.andfunction(instruction[0], instruction[1], instruction[2])
    elif (opcode == 'OR'):
        program.orfunction(instruction[0], instruction[1], instruction[2])
    elif (opcode == 'NOT'):
        program.notfunction(instruction[0], instruction[1])
    elif (opcode == 'EQ'):
        program.eq(instruction[0], instruction[1], instruction[2])
    elif (opcode == 'GT'):
        program.gt(instruction[0], instruction[1], instruction[2])
    elif (opcode == 'LT'):
        program.lt(instruction[0], instruction[1], instruction[2])
    elif (opcode == 'LABEL'):
        pass
    else:
        exit(32)
    program.next_instr()

#print(program)
