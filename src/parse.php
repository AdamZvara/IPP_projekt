<?php
ini_set('display_errors', 'stderr');

$help_message = "this will be printed out help message";

# Getting arguments from command line
$longopt = array(
    "help",
    "stats:",
    "loc",
    "comments",
    "labels",
    "jumps",
    "fwjumps",
    "backjumps",
    "badjumps");

$options = getopt("", $longopt);
$stat_used = "";

if (key_exists("help", $options)) {
    if (count($options) > 1) {
        fprintf(STDERR, "Help option used with another option" . PHP_EOL);
        exit(10);
    }
    echo $help_message . PHP_EOL;
} else {
    $stats_defined = false;
    foreach ($options as $key => $value) {
        if ($key == "stats") {
            $stats_defined = true;
        } else {
            if ($stats_defined == false) {
                fprintf(STDERR, "Stats parameter used without specified file" . PHP_EOL);
                exit(10);
            } else if ($stat_used != "") {
                fprintf(STDERR, "Multiple stats parameters used" . PHP_EOL);
                exit(12);
            } else {
                switch ($key)
                {
                    case "loc":
                        $stat_used = "loc";
                        break;
                    case "comments":
                        $stat_used = "comments";
                        break;
                    case "labels":
                        $stat_used = "labels";
                        break;
                    case "jumps":
                        $stat_used = "jumps";
                        break;
                    case "fwjumps":
                        $stat_used = "fwjumps";
                        break;
                    case "backjumps":
                        $stat_used = "backjumps";
                        break;
                    case "badjumps":
                        $stat_used = "badjumps";
                        break;
                    default:
                        break;
                }
            }
        }
    }
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

const VAR_FRAME_R = '(LF|GF|TF)@';
const VAR_IDENT_R = '[_\-$&%*!?a-zA-Z][_\-$&%*!?a-zA-Z0-9]*';
const VAR_R = '/^'.VAR_FRAME_R.VAR_IDENT_R.'$/';
const TYPE_R = '/^(int|string|bool)$/';
const BOOL_R = '/^bool@(true|false)$/';
const INT_R  = '/^int@[-|+]?[0-9]+$/';
const STRING_R = '/^string@([^\\\]|\\\[0-9][0-9][0-9])*$/';
const NIL_R = '/^nil@nil$/';

class Instruction
{
    private static $order = 0;
    private $opcode;
    private $arg_counter = 1;

    function __construct($opcode)
    {
        self::$order++;
        $this->opcode = $opcode;
    }

    private function var_match($arg)
    {
        if (!preg_match(VAR_R, $arg)) {
            exit(23);
        }
    }

    private function symb_match($arg)
    {
        if (!preg_match(BOOL_R, $arg)   && !preg_match(INT_R, $arg) &&
            !preg_match(STRING_R, $arg) && !preg_match(NIL_R, $arg) &&
            !preg_match(VAR_R, $arg)) {
            exit(23);
        }
    }

    private function label_match($arg)
    {
        if (!preg_match('/^' . VAR_IDENT_R . '$/', $arg)) {
            exit(23);
        }
    }

    private function type_match($arg)
    {
        if (!preg_match(TYPE_R, $arg)) {
            exit(23);
        }
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
        if (count($arg) != count($arg_types)) {
            exit(23);
        }

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
while (FALSE !== ($line = fgets(STDIN))) {
    # remove potential comments from line
    if (($comment_start = strpos($line, '#')) !== false) {
        $line = substr_replace($line, '', $comment_start);
        if (strlen($line) == 0) {
            continue;
        }
    }

    # separate into array based on whitespaces
    $line = trim($line);
    $tokens = preg_split('/\s+/', $line);

    # create separate variables for instruction and arguments
    $instr = strtoupper($tokens[0]);
    $arguments = array_slice($tokens, 1);

    $instr_obj = new Instruction($instr);
    $instr_obj->write_start($xml);

    switch ($instr) {
        # INSTR
        case 'CREATEFRAME':
        case 'PUSHFRAME':
        case 'POPFRAME':
        case 'RETURN':
        case 'BREAK':
            $instr_obj->write_arguments($xml, $arguments, array());
            break;

        # INSTR var
        case 'DEFVAR':
        case 'POPS':
            $instr_obj->write_arguments($xml, $arguments, array('var'));
            break;

        # INSTR symb
        case 'DPRINT':
        case 'EXIT':
        case 'WRITE':
        case 'PUSHS':
            $instr_obj->write_arguments($xml, $arguments, array('symb'));
            break;

        # INSTR label
        case 'LABEL':
        case 'JUMP':
        case 'CALL':
            $instr_obj->write_arguments($xml, $arguments, array('label'));
            break;

        # INSTR var type
        case 'READ':
            $instr_obj->write_arguments($xml, $arguments, array('var', 'type'));
            break;

        # INSTR var symbol
        case 'MOVE':
        case 'INT2CHAR':
        case 'STRLEN':
        case 'TYPE':
            $instr_obj->write_arguments($xml, $arguments, array('var', 'symb'));
            break;

        # INSTR label symb symb
        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':
            $arg = array('label', 'symb', 'symb');
            $instr_obj->write_arguments($xml, $arguments, $arg);
            break;

        # INSTR var symb symb
        case 'ADD'  :
        case 'SUB'  :
        case 'MUL'  :
        case 'DIV'  :
        case 'LT'   :
        case 'GT'   :
        case 'EQ'   :
        case 'END'  :
        case 'OR'   :
        case 'NOT'  :
        case 'STR2INT'  :
        case 'CONCAT'   :
        case 'GETCHAR'  :
        case 'SETCHAR'  :
            $arg = array('var', 'symb', 'symb');
            $instr_obj->write_arguments($xml, $arguments, $arg);
            break;

        default:
            exit(22);
            break;
    }

    $instr_obj->write_end($xml);
}

$xml->endElement(); #program element
$xml->endDocument();
echo $xml->outputMemory();
?>

