<?php
ini_set('display_errors', 'stderr');

$help_message = "USAGE: php parse.php [OPT]\n" .
                "Parse IPPcode22 source code from standard " .
                "input into XML format which is printed to\n" .
                "standard output\n\n" .
                "OPTIONS:\n  --help\tprint out this message";


# Getting arguments from command line
$longopt = array("help",);

$options = getopt("", $longopt);

if (key_exists("help", $options)) {
    # help with any other option
    if ($argc > 2) {
        fprintf(STDERR, 'help used with another param' . PHP_EOL);
        exit(10);
    }

    echo $help_message . PHP_EOL;
    exit(0);
}

# Create xml file
$xml = new XMLWriter();
$xml->openMemory();
$xml->setIndent(1);
$xml->setIndentString('  ');
$xml->startDocument('1.0', 'UTF-8');

function strip_comment($line)
{
    $comment_start = strpos($line, '#');
    if ($comment_start === false) {
        return $line;
    } else {
        return $line = substr_replace($line, '', $comment_start);
    }
}

# look for header
while ($line = fgets(STDIN)) {
    $line = strip_comment($line);
    $line = trim($line);
    if (strlen($line) == 0)
        continue;

    $tokens = preg_split('/\s+/', $line);
    $instr = strtoupper($tokens[0]);

    if ($instr === '.IPPCODE22') {
        $xml->startElement('program');
        $xml->writeAttribute('language', 'IPPcode22');
        break;
    } else {
        exit(21);
    }
}

class Instruction
{
    private static $order = 0;
    private $opcode;
    private $arg_counter = 1;

    const VAR_FRAME_R = '(LF|GF|TF)@';
    const VAR_IDENT_R = '[_\-$&%*!?a-zA-Z][_\-$&%*!?a-zA-Z0-9]*';
    const VAR_R = '/^'. self::VAR_FRAME_R . self::VAR_IDENT_R.'$/';
    const TYPE_R = '/^(int|string|bool)$/';
    const BOOL_R = '/^bool@(true|false)$/';
    const INT_R  = '/^int@[-|+]?[0-9]+$/';
    const STRING_R = '/^string@([^\\\]|\\\[0-9][0-9][0-9])*$/';
    const NIL_R = '/^nil@nil$/';

    function __construct($opcode)
    {
        self::$order++;
        $this->opcode = $opcode;
    }

    private function var_match($arg)
    {
        if (!preg_match(self::VAR_R, $arg))
            exit(23);
    }

    private function symb_match($arg)
    {
        if (!preg_match(self::BOOL_R, $arg)   && !preg_match(self::INT_R, $arg) &&
            !preg_match(self::STRING_R, $arg) && !preg_match(self::NIL_R, $arg) &&
            !preg_match(self::VAR_R, $arg))
            exit(23);
    }

    private function label_match($arg)
    {
        if (!preg_match('/^' . self::VAR_IDENT_R . '$/', $arg))
            exit(23);
    }

    private function type_match($arg)
    {
        if (!preg_match(self::TYPE_R, $arg))
            exit(23);
    }

    public function write_start($xml)
    {
        $xml->startElement('instruction');
        $xml->writeAttribute('order', self::$order);
        $xml->writeAttribute('opcode', $this->opcode);
    }

    public function write_end($xml)
    {
        $xml->endElement();
    }

    private function get_symbol_type($symbol)
    {
        $remove;
        if (str_starts_with($symbol, 'GF@') ||
            str_starts_with($symbol, 'LF@') ||
            str_starts_with($symbol, 'TF@')) {
                $remove = 'var';
                return array($remove, $symbol);
        }

        if (str_starts_with($symbol, 'string@')) {
            $remove = 'string';
        } elseif (str_starts_with($symbol, 'int@')) {
            $remove = 'int';
        } elseif (str_starts_with($symbol, 'bool@')) {
            $remove = 'bool';
        } elseif (str_starts_with($symbol, 'nil@')) {
            $remove = 'nil';
        }

        return array($remove, substr_replace($symbol, '', 0, strlen($remove)+1));
    }

    public function write_arguments($xml, $arg, $arg_types)
    {
        # check number of arguments
        if (count($arg) != count($arg_types))
            exit(23);

        foreach($arg_types as $value => $type) {
            $xml->startElement('arg' . $this->arg_counter);
            $curr_arg = $arg[$this->arg_counter-1];
            switch ($type) {
                case 'var':
                    $this->var_match($curr_arg);
                    $xml->writeAttribute('type', $type);
                    $xml->text($curr_arg);
                    break;

                case 'symb':
                    $this->symb_match($curr_arg);
                    $type_value = $this->get_symbol_type($curr_arg);
                    $xml->writeAttribute('type', $type_value[0]);
                    $xml->text($type_value[1]);
                    break;

                case 'label':
                    $this->label_match($curr_arg);
                    $xml->writeAttribute('type', $type);
                    $xml->text($curr_arg);
                    break;

                case 'type':
                    $this->type_match($curr_arg);
                    $xml->writeAttribute('type', $type);
                    $xml->text($curr_arg);

                default:
                    break;
            }

            $xml->endElement();
            $this->arg_counter++;
        }
    }
}

# parsing actual source file
while ($line = fgets(STDIN)) {
    # remove potential comments from line and strip whitespaces
    $line = strip_comment($line);
    $line = trim($line);
    if (strlen($line) == 0)
        continue;

        # separate into array based on whitespaces
    $tokens = preg_split('/\s+/', $line);

    # create separate variables for instruction and arguments
    $instr = strtoupper($tokens[0]);
    $arguments = array_slice($tokens, 1);

    $instr_obj = new Instruction($instr);
    $instr_obj->write_start($xml);

    switch ($instr) {
        # INSTR
        case 'CREATEFRAME':
        case 'PUSHFRAME'  :
        case 'POPFRAME'   :
        case 'RETURN'     :
        case 'BREAK'      :
            $arg_types = array();
            break;

        # INSTR var
        case 'DEFVAR':
        case 'POPS'  :
            $arg_types = array('var');
            break;

        # INSTR symb
        case 'DPRINT':
        case 'EXIT'  :
        case 'WRITE' :
        case 'PUSHS' :
            $arg_types = array('symb');
            break;

        # INSTR label
        case 'LABEL':
        case 'JUMP' :
        case 'CALL' :
            $arg_types = array('label');
            break;

        # INSTR var type
        case 'READ':
            $arg_types = array('var', 'type');
            break;

        # INSTR var symbol
        case 'MOVE'    :
        case 'INT2CHAR':
        case 'STRLEN'  :
        case 'TYPE'    :
        case 'NOT'     :
            $arg_types = array('var', 'symb');
            break;

        # INSTR label symb symb
        case 'JUMPIFEQ' :
        case 'JUMPIFNEQ':
            $arg_types = array('label', 'symb', 'symb');
            break;

        # INSTR var symb symb
        case 'ADD'    :
        case 'SUB'    :
        case 'MUL'    :
        case 'IDIV'    :
        case 'LT'     :
        case 'GT'     :
        case 'EQ'     :
        case 'AND'    :
        case 'OR'     :
        case 'STRI2INT':
        case 'CONCAT' :
        case 'GETCHAR':
        case 'SETCHAR':
            $arg_types = array('var', 'symb', 'symb');
            break;

        default:
            exit(22);
    }

    $instr_obj->write_arguments($xml, $arguments, $arg_types);
    $instr_obj->write_end($xml);
}

$xml->endElement(); #program element
$xml->endDocument();
echo $xml->outputMemory();
?>