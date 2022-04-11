<?php

class HTMLCreator
{
    private $dom;
    private $html;
    private $body;

    function start()
    {
        $imp = new DOMImplementation;
        $dtd = $imp->createDocumentType('html', '', '');
        $this->dom = $imp->createDocument("", "", $dtd);
        $this->dom->encoding = 'UTF-8';
        $this->dom->formatOutput = true;

        $this->html = $this->dom->createElement('html');
        $this->dom->appendChild($this->html);

        $this->body = $this->dom->createElement("body");
        $this->html->appendChild($this->body);
    }

    function summary($passedCount, $failedCount)
    {
        $div = $this->dom->createElement('div');
        $this->body->appendChild($div);
        $div->setAttribute("style", "background-color:lightgray; padding: 5px 10px; text-align: center;");

        $summary = $this->dom->createElement('h1');
        $div->appendChild($summary);

        $summary->appendChild($this->dom->createTextNode('Summary'));

        $passed = $this->dom->createElement('p');
        $div->appendChild($passed);
        $passed->appendChild($this->dom->createTextNode('Passed: ' . $passedCount));
        $passed->setAttribute("style", "color:green; font-weight:bold; line-height: 20%");

        $failed = $this->dom->createElement('p');
        $div->appendChild($failed);
        $failed->appendChild($this->dom->createTextNode("\nFailed: ". $failedCount));
        $failed->setAttribute("style", "color:red; font-weight:bold; line-height: 20%");

        $total = $this->dom->createElement('p');
        $div->appendChild($total);
        $total->appendChild($this->dom->createTextNode("\nTotal: ". $failedCount+$passedCount));
        $total->setAttribute("style", "font-weight:bold; font-size: large; line-height: 20%");
    }

    function content($passed, $failed, $all)
    {
        foreach ($all as $key => $value) {
            if (!array_key_exists($key, $passed)) {
                $this->single_directory($key, array(), $failed[$key]);
            } else if (!array_key_exists($key, $failed)) {
                $this->single_directory($key, $passed[$key], array());
            } else {
                $this->single_directory($key, $passed[$key], $failed[$key]);
            }
        }
    }

    private function single_directory($dirname, $passedTests, $failedTests)
    {
        $div = $this->dom->createElement('div');
        $this->body->appendChild($div);
        $div->setAttribute("style", "border-style: dashed;border-color:black; border-radius: 25px; padding-left: 10px; margin-top: 10px;");

        $name = $this->dom->createElement('h3');
        $div->appendChild($name);

        $name->appendChild($this->dom->createTextNode($dirname . "\n"));

        $boldFailed = $this->dom->createElement('b');
        $div->appendChild($boldFailed);
        $boldFailed->appendChild($this->dom->createTextNode(' FAILED:'));
        $boldFailed->setAttribute("style", "color:red; margin-left: 2%;");
        $div->appendChild($this->dom->createElement('br'));

        foreach ($failedTests as $key => $value) {
            $this->single_test($value, 'red', $div);
        }

        $boldPassed = $this->dom->createElement('b');
        $div->appendChild($boldPassed);
        $boldPassed->appendChild($this->dom->createTextNode(' PASSED:'));
        $boldPassed->setAttribute("style", "color:green; margin-left: 2%;");
        $div->appendChild($this->dom->createElement('br'));

        foreach ($passedTests as $key => $value) {
            $this->single_test($value, 'green', $div);
        }
    }
    private function single_test($testname, $color, &$div) {
        $name = $this->dom->createElement('p');
        $name->setAttribute("style", "line-height: 0%; margin-left: 3%;");
        $div->appendChild($name);
        $name->appendChild($this->dom->createTextNode($testname));
    }

    function end()
    {
        $this->dom->saveHTMLFile("index.html");
    }

}
?>