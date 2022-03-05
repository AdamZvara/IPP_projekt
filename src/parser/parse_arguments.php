<?php

include 'error_codes.php';
include 'statistics.php';

const HELP_MESSAGE = "USAGE: php parse.php [OPT]\n" .
                     "Parse IPPcode22 source code from standard " .
                     "input into XML format which is printed to\n" .
                     "standard output\n\n" .
                     "OPTIONS:\n  --help\tprint out this message";

define('HELP',      "--help");
define('STATS',     "--stats");
define('LOC',       "--loc");
define('COMMENTS',  "--comments");
define('LABELS',    "--labels");
define('JUMPS',     "--jumps");
define('FWJUMPS',   "--fwjumps");
define('BACKJUMPS', "--backjumps");
define('BADJUMPS',  "--badjumps");

class Stats_file
{
    static private $_files_used = array();
    private $_filename;
    private $_file;
    private $_stats = array();

    # check if file was already used with --stats option and open given file
    function __construct($filename)
    {
        if (in_array($filename, self::$_files_used)) {
            exit(E_OUTFILE);
        }
        $this->_filename = $filename;
        array_push( self::$_files_used, $filename);
    }

    function add_stat($stat_name)
    {
        array_push($this->_stats, $stat_name);
    }

    function write_stats($stat_obj)
    {
        foreach ($this->_stats as $key => $stat) {
            switch ($stat) {
                case LOC:
                    fwrite($this->_file, $stat_obj->get_loc() . PHP_EOL);
                    break;

                case COMMENTS:
                    fwrite($this->_file, $stat_obj->get_comments() . PHP_EOL);
                    break;

                case LABELS:
                    fwrite($this->_file, $stat_obj->get_labels() . PHP_EOL);
                    break;

                case JUMPS:
                    fwrite($this->_file, $stat_obj->get_jumps() . PHP_EOL);
                    break;

                case FWJUMPS:
                    fwrite($this->_file, $stat_obj->get_fwjumps() . PHP_EOL);
                    break;

                case BACKJUMPS:
                    fwrite($this->_file, $stat_obj->get_backjumps() . PHP_EOL);
                    break;

                case BADJUMPS:
                    fwrite($this->_file, $stat_obj->get_badjumps() . PHP_EOL);
                    break;

                default:
                    break;
            }
        }
    }

    # open file
    function open()
    {
        if (($this->_file = fopen($this->_filename,"w")) == false)
            exit(E_INTERNAL);
    }

    # close file
    function close() {fclose($this->_file);}
}

class Bonus_arg_handler
{
    private $_arguments;
    private $_argc;
    private $_stats_array = array();

    public function __construct($argc, $command_args)
    {
        $this->_arguments = array_slice($command_args, 1);
        $this->_argc = $argc;
    }

    # parse arguments from command line into Stats_file objects
    public function parse_args()
    {
        # parse help option
        if (in_array(HELP, $this->_arguments)) {
            if ($this->_argc > 2) {
                # help with any other option
                exit(E_WRONGARG);
            }
            echo HELP_MESSAGE . PHP_EOL;
            exit(0);
        }

        foreach ($this->_arguments as $key => $value) {
            if (str_starts_with($value, STATS)) { # new file was added for statistics
                $value = substr($value, strlen(STATS)+1); # remove '=' from value
                array_push($this->_stats_array, new Stats_file($value));
                continue;
            }

            # option with no --stats file defined
            if (count($this->_stats_array) == 0)
                exit(E_WRONGARG);

            # valid options
            if ($value == LOC || $value == COMMENTS || $value == LABELS || $value == JUMPS ||
                $value == FWJUMPS|| $value == BACKJUMPS|| $value == BADJUMPS) {
                    # get last element from _stats_array since these options belong to it
                    end($this->_stats_array)->add_stat($value);
            } else {
                exit(E_WRONGARG);
            }
        }
    }

    public function write($stat)
    {
        foreach ($this->_stats_array as $key => $object) {
            $object->open();
            $object->write_stats($stat);
            $object->close();
        }
    }
}
?>