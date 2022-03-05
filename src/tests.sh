#!/bin/bash

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'

TESTS='ipp-2022-tests'
PARSE_TESTS="$TESTS/parse-only"
JEXAMXML_PATH="$TESTS/jexamxml/jexamxml.jar"
JEXAMXML_OPT_PATH="$TESTS"

INTERPRET_TESTS="$TESTS/interpret-only"

declare -i TEST_COUNT=0
declare -i TEST_PASSED=0

function parser_test()
{
    echo -e "${ORANGE}PARSE-ONLY${NC}"
    for DIR in $(ls $PARSE_TESTS)
    do
        echo -e "  ${CYAN}$DIR${NC}"
        for TEST_NAME in $(ls $PARSE_TESTS/$DIR | grep ".src")
        do
            TEST_COUNT+=1
            TEST_NAME=${TEST_NAME%.*}
            #echo -e -n "\t${BLUE}$TEST_NAME:${NC}"

            php8.1 parser/parse.php < "$PARSE_TESTS/$DIR/$TEST_NAME.src" > tmp
            RETVAL=$?
            RETVAL_EXPECTED=$(cat "$PARSE_TESTS/$DIR/$TEST_NAME.rc")

            # check if return codes match
            if [ $RETVAL != $RETVAL_EXPECTED ]; then
                echo -e " ${RED}FAILED${NC}"
            else
                if [ $RETVAL != 0 ]; then
                    # error occured, no need to do XML_DIFF
                    #echo -e " ${GREEN}PASSED${NC}"
                    TEST_PASSED+=1
                else
                    # no error occured, do XML_DIFF
                    XML_EXP=$PARSE_TESTS/$DIR/$TEST_NAME.out
                    java -jar $JEXAMXML_PATH tmp $XML_EXP $JEXAMXML_OPT_PATH/options>/dev/null
                    if [ $? -eq 0 ]; then
                        TEST_PASSED+=1
                        #echo -e " ${GREEN}PASSED${NC}"
                    else
                        echo -e " ${RED}FAILED${NC}"
                    fi
                fi
            fi
        done
    done
}

function interpret_test()
{
    echo -e "${ORANGE}INTERPRET-ONLY${NC}"
    for DIR in $(ls $INTERPRET_TESTS)
    do
        echo -e "  ${CYAN}$DIR${NC}"
        for TEST_NAME in $(ls $INTERPRET_TESTS/$DIR | grep ".src")
        do
            TEST_COUNT+=1
            TEST_NAME=${TEST_NAME%.*}
            echo -e -n "\t${BLUE}$TEST_NAME:${NC}"

            src=$INTERPRET_TESTS/$DIR/$TEST_NAME'.src'
            input=$INTERPRET_TESTS/$DIR/$TEST_NAME'.in'
            python3 interpret.py --source=$src --input=$input > tmp
            RETVAL=$?
            RETVAL_EXPECTED=$(cat "$INTERPRET_TESTS/$DIR/$TEST_NAME.rc")

            # check if return codes match
            if [ $RETVAL != $RETVAL_EXPECTED ]; then
                echo -e " ${RED}FAILED${NC}"
            else
                if [ $RETVAL != 0 ]; then
                    # error occured, no need to check output
                    TEST_PASSED+=1
                    echo -e " ${GREEN}PASSED${NC}"
                else
                    diff $INTERPRET_TESTS/$DIR/$TEST_NAME.'out' tmp >/dev/null
                    if [ $? -eq 0 ]; then
                       TEST_PASSED+=1
                        echo -e " ${GREEN}PASSED${NC}"
                    else
                        echo -e " ${RED}FAILED${NC}"
                    fi
                fi
            fi

        done
    done
}

PARSER_BONUS="$TESTS/parser_bonus"

function parser_bonus()
{
    echo -e "${ORANGE}PARSER-BONUS${NC}"

    for TEST_NAME in $(ls $PARSER_BONUS | grep ".run")
        do
            echo -e -n "\t${BLUE}$TEST_NAME:${NC}\n"
            while read -r line; do
                echo -e -n "\t\t$line:"
                TEST_COUNT+=1
                TEST_NAME=${TEST_NAME%.*}

                valid=$(echo $TEST_NAME | grep valid)
                empty=$(echo $TEST_NAME | grep empty)
                if [ $valid ]; then
                    php8.1 parser/parse.php $line < "$PARSER_BONUS/$TEST_NAME.in" >/dev/null
                else
                    php8.1 parser/parse.php $line > tmp
                fi

                RETVAL=$?
                RETVAL_EXPECTED=$(cat "$PARSER_BONUS/$TEST_NAME.rc")

                # check if return codes match
                if [ $RETVAL != $RETVAL_EXPECTED ]; then
                    echo -e " ${RED}FAILED${NC}"
                else
                    if [ $RETVAL != 0 ]; then
                        # error occured, no need to check output
                        TEST_PASSED+=1
                        echo -e " ${GREEN}PASSED${NC}"
                    else
                        if [ "$valid" = 'valid' ]; then
                            diff "$PARSER_BONUS/$TEST_NAME.out" file -E -B >/dev/null
                        elif [ "$valid" = 'valid2' ]; then
                            diff "$PARSER_BONUS/$TEST_NAME.out1" file -E -B >/dev/null
                            a=$?
                            diff "$PARSER_BONUS/$TEST_NAME.out2" file2 -E -B >/dev/null
                            b=$?
                            [ $((a-b)) == 0 ]
                        elif [ "$empty" ]; then
                            touch file
                            diff "$PARSER_BONUS/$TEST_NAME.out" file -E -B >/dev/null
                        else
                            diff "$PARSER_BONUS/$TEST_NAME.out" tmp -E -B >/dev/null
                        fi
                        if [ $? -eq 0 ]; then
                            TEST_PASSED+=1
                            echo -e " ${GREEN}PASSED${NC}"
                        else
                            echo -e " ${RED}FAILED${NC}"
                        fi
                    fi
                fi
            done < "$PARSER_BONUS/$TEST_NAME";
        done
}

if [ -z $1 ]; then
    parser_test
    interpret_test
elif [ $1 == 'parser' ]; then
    parser_test
elif [ $1 == 'interpret' ]; then
    interpret_test
elif [ $1 == 'pbonus' ]; then
    parser_bonus
fi

echo "Passed" $TEST_PASSED "tests out of" $TEST_COUNT

rm -rf tmp*