<?php
#context class containing info about file locations, noclean, recursive options etc

include "error_codes.php";

class Context
{
    private $help_message = "USAGE: php test.php [OPT]" . PHP_EOL .
        "Test parser or interpret scripts" . PHP_EOL .
        "OPTIONS:" . PHP_EOL .
            "\t--help\t\t\tprint out this message" . PHP_EOL .
            "\t--recursive\t\ttest directory is searched recursively" . PHP_EOL .
            "\t--noclean\t\tfiles created for testing will be deleted" . PHP_EOL .
            "\t--parse-only\t\trun parser tests" . PHP_EOL .
            "\t--int-only\t\trun interpret tests" . PHP_EOL .
            "\t--directory=path\ttest directory (implicit current directory)" . PHP_EOL .
            "\t--parse-script=file\tparer.php file (implicit file \"parse.php\" in current directory)" . PHP_EOL .
            "\t--int-script=file\tinterpret.py file (implicit file \"interpret.py\" in current directory)" . PHP_EOL .
            "\t--jexampath=path\tpath to jexamxml.jar to compare output xml files" . PHP_EOL;

    private $longopt = array(
        "help",
        "directory:",
        "recursive",
        "parse-script:",
        "int-script:",
        "parse-only",
        "int-only",
        "jexampath:",
        "noclean"
        );

    public $recursive = false;
    public $clean = true;
    public $parse_only = false;
    public $int_only = false;
    public $parse_script = "parse.php";
    public $int_script = "interpret.py";
    public $directory = null;
    public $jexampath = "/pub/courses/ipp/jexamxml/";

    function __construct($argc)
    {
        $this->directory = dirname(__FILE__);
        $options = getopt("", $this->longopt);

        foreach ($options as $key => $value) {
            if ($key == "help") {
                if ($argc > 2)
                    exit(E_WRONGARG);
                echo $this->help_message . PHP_EOL;
                exit(0);
            } elseif ($key == "recursive") {
                $this->recursive = true;
            } elseif ($key == "noclean") {
                $this->clean = false;
            } elseif ($key == "parse-only") {
                if (key_exists("int-only", $options) || key_exists("int-script", $options))
                    exit(E_WRONGARG);
                $this->parse_only = true;
            } elseif ($key == "int-only") {
                if (key_exists("parse-only", $options) || key_exists("parse-script", $options))
                    exit(E_WRONGARG);
                $this->int_only = true;
            } elseif ($key == "directory") {
                if (!is_readable($value)) {
                    exit(E_NOFILE);
                } else {
                    $this->directory = $value;
                }
            } elseif ($key == "parse-script") {
                if (!is_readable($value)) {
                    exit(E_NOFILE);
                } else {
                    $this->parse_script = $value;
                }
            } elseif ($key == "int-script") {
                if (!is_readable($value)) {
                    exit(E_NOFILE);
                } else {
                    $this->int_script = $value;
                }
            } elseif ($key == "jexampath") {
                if (!is_readable($value)) {
                    exit(E_NOFILE);
                } else {
                    if (!str_ends_with($value, '/'))
                    $value = $value . '/';
                $this->jexampath = $value;
                }
            }
        }
    }

}

?>