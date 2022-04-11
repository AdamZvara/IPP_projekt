<?php

# Class to retrieve source files for test and look for other files
# (or create them if they do not exist)

class FileHandler {
    function check_files($source) {
        $basePathName = substr($source, 0, -4);
        $this->srcfile = $source;

        # rc file check
        $pathname = $basePathName . '.rc';
        if (!file_exists($pathname)) {
            $this->_create_zero_file($pathname);
        }

        # in file check
        $pathname = $basePathName . '.in';
        if (!file_exists($pathname)) {
            $this->_create_empty_file($pathname);
        }

        # out file check
        $pathname = $basePathName . '.out';
        if (!file_exists($pathname)) {
            $this->_create_empty_file($pathname);
        }
    }

    function _create_zero_file($pathname) {
        //echo $pathname . ' created' . PHP_EOL;
        file_put_contents($pathname, 0);
    }

    function _create_empty_file($pathname) {
        //echo $pathname . ' created' . PHP_EOL;
        file_put_contents($pathname, '');
    }
}

?>