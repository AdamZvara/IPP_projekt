<?php
include "error_codes.php";
include "context.php";
include "dirsearch.php";
include "filehandler.php";
include "testmodules.php";
include "htmlcreator.php";

$context = new Context($argc);
$dirsearch = new DirectorySearch($context->directory, $context->recursive);
$fileHandler = new FileHandler();

$parseTester = new ParseTester($context->parse_script, $context->jexampath, $context->clean);
$interpretTester = new InterpretTester($context->int_script, $context->clean);
$multiTester = new MultiTester($context->parse_script, $context->int_script, $context->jexampath, $context->clean);

$testsPassed = array();
$testsFailed = array();
$allTests = array();

function add_to_array($fileName, $directoryName, &$array)
{
    if (array_key_exists($directoryName, $array)) {
        array_push($array[$directoryName], $fileName);
    } else {
        $array[$directoryName] = array($fileName);
    }
}

while ($file = $dirsearch->get_file()) {
    $fileHandler->check_files($file);

    $separatorPos = strrpos($file, '/') + 1;
    $directoryName = substr($file, 0, $separatorPos);
    $fileName = substr($file, $separatorPos);

    if ($context->parse_only) {
        $retval = $parseTester->test($file);
    } else if ($context->int_only) {
        $retval = $interpretTester->test($file);
    } else {
        $retval = $multiTester->test($file);
    }

    if ($retval) {
        add_to_array($fileName, $directoryName, $testsPassed);
    } else {
        add_to_array($fileName, $directoryName, $testsFailed);
    }

    if (!array_key_exists($directoryName, $allTests)){
        $allTests[$directoryName] = false;
    }
}

# count elements recursively and subtract the first layer (keys only)
$passedCount = count($testsPassed, COUNT_RECURSIVE) - count($testsPassed);
$failedCount = count($testsFailed, COUNT_RECURSIVE) - count($testsFailed);

ksort($allTests);

$html = new HTMLCreator();
$html->start();
$html->summary($passedCount, $failedCount);
$html->content($testsPassed, $testsFailed, $allTests);
$html->end();

?>