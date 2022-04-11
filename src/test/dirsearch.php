<?php

# Class to look for test files, provides API to actual tester to get next batch of test files

class DirectorySearch {

    private $_iterator;

    # Create recursive iterator to traverse thourgh directories
    # and set its maximum depth based on recursive option
    function __construct($directory, $recursive)
    {
        $dictIterator = new RecursiveDirectoryIterator($directory);
        $this->_iterator = new RecursiveIteratorIterator($dictIterator);

        if ($recursive == null)
            $this->_iterator->setMaxDepth(0);
    }

    # Get next file in directory (subdirectories) that has '.src' extension
    function get_file()
    {
        if ($this->_iterator->valid() == true) {
            $file = $this->_iterator->current();
            $this->_iterator->next();
            if ($file->getExtension() == 'src') {
                $pathname = $file->getPathname();
                if (!$file->isDir())
                    return $pathname;
                else
                    return $this->get_file();
            }
            return $this->get_file();
        } else {
            return false;
        }
    }
}

?>