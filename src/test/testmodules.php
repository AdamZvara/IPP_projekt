<?php

interface ITestable {
    function test($filename);
}

abstract class Tester implements ITestable{
    //abstract protected function process_file($srcfile, $tmpfile, $infile);
    abstract protected function compare_results($outfile, $tmpFile);

    static protected $_clean;
    static protected $python = "python3";
    static protected $php = "php8.1";

    function test($filename)
    {
        $fileBaseName = substr($filename, 0, -4);

        $rcfile  = $fileBaseName . '.rc';
        $srcfile = $fileBaseName . '.src' ;
        $tmpfile = $fileBaseName . '.tmp';
        $infile  = $fileBaseName . '.in';
        $outfile = $fileBaseName . '.out';

        $rc_expected = file_get_contents($rcfile);
        $rc_actual = $this->process_file($srcfile, $tmpfile, $infile);

        if ($rc_expected != 0) {
            if ($rc_expected == $rc_actual) {
                $retval = true;
            } else {
                $retval = false;
            }
        } else {
            $rc = $this->compare_results($outfile, $tmpfile);
            if ($rc == 0) {
                $retval = true;
            } else {
                $retval = false;
            }
        }

        if (self::$_clean == true) {
            unlink($tmpfile);
        }

        return $retval;
    }
}

class ParseTester extends Tester {
    private $parse_script;
    private $jexampath;

    function __construct($parse_script, $jexampath, $clean)
    {
        $this->parse_script = $parse_script;
        $this->jexampath = $jexampath;
        parent::$_clean = $clean;
    }

    function process_file($srcfile, $tmpfile, $infile)
    {
        $result = null;
        $output = null;
        exec(parent::$php . ' '.$this->parse_script.' > '. $tmpfile.' < '.$srcfile, $output, $result);
        return $result;
    }

    function compare_results($outfile, $tmpFile)
    {
        $result = null;
        $output = null;
        exec('java -jar '.$this->jexampath.'jexamxml.jar'.' '.$tmpFile.' '.$outfile.' '.$this->jexampath.'options',
            $output,
            $result
        );
        return $result;
    }
}

class InterpretTester extends Tester {
    private $int_script;

    function __construct($int_script, $clean)
    {
        $this->int_script = $int_script;
        parent::$_clean = $clean;
    }

    function process_file($srcfile, $tmpfile, $infile)
    {
        $result = null;
        $output = null;
        exec(parent::$python . ' '.$this->int_script.' --source='.$srcfile.' --input='.$infile.' > '.$tmpfile . ' 2> /dev/null',
            $output,
            $result
        );
        return $result;
    }

    function compare_results($outfile, $tmpFile)
    {
        $result = null;
        $output = null;
        exec('diff '.$tmpFile.' '.$outfile, $output, $result);
        return $result;
    }
}

class MultiTester extends Tester
{
    private $int_script;
    private $parse_script;
    private $jexampath;

    function __construct($parse_script, $int_script, $jexampath, $clean)
    {
        $this->parse_script = $parse_script;
        $this->int_script = $int_script;
        $this->jexampath = $jexampath;
        parent::$_clean = $clean;
    }

    function parse_file($srcfile, $tmpfile, $infile)
    {
        $result = null;
        $output = null;
        exec(parent::$php . ' '.$this->parse_script.' > '. $tmpfile.' < '.$srcfile, $output, $result);
        return $result;
    }

    function interpret_file($srcfile, $tmpfile, $infile) {
        $result = null;
        $output = null;
        exec(parent::$python . ' '.$this->int_script.' --source='.$srcfile.' --input='.$infile.' > '.$tmpfile . ' 2> /dev/null',
            $output,
            $result
        );
        return $result;
    }

    function compare_results($outfile, $tmpFile)
    {
        $result = null;
        $output = null;
        exec('diff '.$tmpFile.' '.$outfile, $output, $result);
        return $result;
    }

    function test($filename)
    {
        $fileBaseName = substr($filename, 0, -4);

        $rcFile  = $fileBaseName . '.rc';
        $srcfile = $fileBaseName . '.src' ;
        $infile  = $fileBaseName . '.in';
        $tmpfile = $fileBaseName . '.tmp';
        $outfile = $fileBaseName . '.out';
        $interpretFile = $fileBaseName . '.int';

        $rc_expected = file_get_contents($rcFile);
        $rc_actual = $this->parse_file($srcfile, $interpretFile, $infile);

        // PARSER CHECKING
        if ($rc_actual != 0) {
            if ($rc_expected == $rc_actual) {
                $retval = true;
            } else {
                $retval = false;
            }
        } else {
            $rc = $this->interpret_file($interpretFile, $tmpfile, $infile);
            if ($rc != $rc_expected) {
                $retval = false;
            } else {
                if ($rc == 0) {
                    if ($this->compare_results($outfile, $tmpfile) == 0) {
                        $retval = true;
                    } else {
                        $retval = false;
                    }
                } else {
                    if ($rc != $rc_expected) {
                        $retval = false;
                    } else {
                        $retval = true;
                    }
                }
            }
        }

        if (self::$_clean == true) {
            unlink($tmpfile);
            unlink($interpretFile);
        }

        return $retval;
    }
}
?>