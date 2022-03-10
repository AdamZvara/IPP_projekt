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
        # add arguments to instruction object
        xml.argument_valid(argument)
        instr.arg_add(argument)
    instr.arg_valid_amount()
    program.add_instruction(instr)

# Sort program instruction by their order and for each instruction
#   sort their arguments
program.instructions_sort()
program.create_labels()

variable_manager = Variable_manager()

def set_args_arithmetics(instruction):
    op1 = instruction.get_argument(1)
    op2 = instruction.get_argument(2)
    allowed = ['int', 'var', 'float']
    if (op1.type not in allowed or op2.type not in allowed):
        exit(53)
    if (op1.type == 'var'):
        value1 = variable_manager.get_value(op1.value)
    else:
        value1 = op1.value
    if (op2.type == 'var'):
        value2 = variable_manager.get_value(op2.value)
    else:
        value2 = op2.value
    return (value1,value2)

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

arithmetic = ['ADD', 'SUB', 'IDIV', 'MUL']

# Go through each instruction in program object and interpret it
while instruction := program.get_instruction():
    opcode = instruction.get_opcode()
    if (opcode == 'DEFVAR'):
        variable_manager.add(instruction.get_argument(0))
    elif (opcode == 'WRITE'):
        variable_manager.print(instruction.get_argument(0))
        # TODO special characters &gt, &lt ...
    elif (opcode == 'MOVE'):
        src = instruction.get_argument(0)
        arg = instruction.get_argument(1)
        variable_manager.insert_value(src, arg.value, arg.type)
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
    elif (opcode in arithmetic):
        var = instruction.get_argument(0)
        (value1,value2) = set_args_arithmetics(instruction)
        if (opcode == 'ADD'):
            variable_manager.insert_value(var, value1+value2, 'int')
        elif (opcode == 'SUB'):
            variable_manager.insert_value(var, value1-value2, 'int')
        elif (opcode == 'MUL'):
            variable_manager.insert_value(var, value1*value2, 'int')
        elif (opcode == 'IDIV'):
            if value2 == 0:
                exit(57)
            variable_manager.insert_value(var, value1//value2, 'int')
    elif (opcode == 'DPRINT'):
        variable_manager.dprint(instruction.get_argument(0))
    elif (opcode == 'EXIT'):
        variable_manager.exit(instruction.get_argument(0))
    elif (opcode == 'TYPE'):
        var = instruction.get_argument(0)
        symb = instruction.get_argument(1)
        types = ['int', 'bool', 'nil', 'string']
        for type in types:
            if (symb.type == type):
                variable_manager.insert_value(var, type, 'string')
        if (symb.type == 'var'):
            variable_manager.insert_value(var, variable_manager.get_type(symb.value), 'string')
    elif (opcode == 'CALL'):
        label = instruction.get_argument(0)
        program.call(label)
    elif (opcode == 'RETURN'):
        program.return_function()
    elif (opcode == 'READ'):
        var = instruction.get_argument(0)
        type = instruction.get_argument(1)
        user_input = input_files.get_input_line()
        if (type.value == 'bool'):
            if (user_input.lower() == 'true'):
                variable_manager.insert_value(var, 'true', 'bool')
            else:
                variable_manager.insert_value(var, 'false', 'bool')
        elif (type.value == 'int'):
            variable_manager.insert_value(var, int(user_input), 'int')
        elif (type.value == 'string'):
            variable_manager.insert_value(var, user_input, 'string')
        else:
            exit(53)
    elif (opcode == 'PUSHS'):
        program.pushs(instruction.get_argument(0))
    elif (opcode == 'LABEL'):
        pass
    else:
        exit(32)
    program.next_instr()

#print(program)
