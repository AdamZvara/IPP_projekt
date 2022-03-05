<?php

class Statistics
{
    private $_loc          = 0;
    private $_comments     = 0;
    private $_jumps        = 0;
    private $_badjumps     = 0;
    private $_labels_count = 0;
    private $_fw_jumps     = 0;
    private $_back_jumps   = 0;
    private $_labels       = array();
    private $_jump_targets = array();

    # loc getter/setter
    public function add_loc() {$this->_loc += 1;}
    public function get_loc() {return $this->_loc;}

    # comments getter/setter
    public function add_comment() {$this->_comments += 1;}
    public function get_comments() {return $this->_comments;}

    # jumps getter
    public function get_jumps() {return $this->_jumps;}

    # forward jumps getter
    public function get_fwjumps(){return $this->_fw_jumps;}

    # back jumps getter
    public function get_backjumps(){return $this->_back_jumps;}

    # label counter getter
    public function get_labels(){return $this->_labels_count;}

    # get badjumps (subtract labels array from jump_targets)
    public function get_badjumps()
    {
        return count(array_diff_key($this->_jump_targets, $this->_labels));
    }

    # increace jump counter and add jump target into array
    public function add_jump($target, $position)
    {
        if (array_key_exists($target, $this->_jump_targets)) { # array of positions already exists
            array_push($this->_jump_targets[$target], $position);
        } else {
            $this->_jump_targets[$target] = array('0' => $position);
        }
        $this->_jumps += 1;
    }

    # add label into _labels if label does not exist, increment label counter
    public function add_label($label_name, $position)
    {
        if (array_key_exists($label_name, $this->_labels)) {
            array_push($this->_labels[$label_name], $position);
        } else {
            $this->_labels[$label_name] = array('0' => $position);
        }
        $this->_labels_count += 1;
    }

    # calculate forward and backward jumps
    public function calculate_fbjumps()
    {
        # iterate through each stored jump, which has positions in code
        # for each position of each jump, try to find jump target in labels
        # and decide, whether it is forward or backward jump
        foreach ($this->_jump_targets as $target => $target_positions) {
            foreach ($target_positions as $key1 => $target_location) {
                if (array_key_exists($target, $this->_labels)) {
                    foreach ($this->_labels[$target] as $key2 => $label_location)
                    if ($target_location - $label_location < 0) {
                        $this->_fw_jumps += 1;
                    } else {
                        $this->_back_jumps += 1;
                    }
                }
            }
        }
        return 0;
    }

}

?>