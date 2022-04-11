from argparse import ArgumentParser
from sys import stdin, exit

# Class for parsing input and handling source and input files
class Input:

    # parse arguments from command line and open internal files
    # to get source or input
    def __init__(self) -> None:
        args = self.__parse_args()
        args_input = args.input
        args_source = args.source

        self.__input = None     # input file handle
        self.__source = stdin   # source filename

        if args_source is None and args_input is None:
            exit(10)

        if args_input is not None:
            self.__open_input_file(args_input)

        if args_source is not None:
            self.__source = args_source

    # parse given arguments from command line
    def __parse_args(self):
        arg_parser = ArgumentParser(description='Interpret code given in XML format')
        arg_parser.add_argument('--source', help='source XML file')
        arg_parser.add_argument('--input', help='input to interpreted program')
        return arg_parser.parse_args()

    # try to open given input file
    def __open_input_file(self, input_filename):
        try:
            self.__input = open(input_filename, "r")
        except FileNotFoundError:
            exit(11)

    # return single line from input
    def get_input_line(self):
        if self.__input is None:
            try:
                return input()
            except EOFError:
                return None
        line = self.__input.readline() # get line and remove trailing newline
        if (line == ''):
            return None
        line = line.rstrip('\n')
        return line

    # get source filename
    def get_source(self):
        return self.__source

    # close input file on deletion
    def __del__(self):
        if (self.__input != None):
            self.__input.close()