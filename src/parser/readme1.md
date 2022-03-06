Implementační dokumentace k 1. úloze do IPP 2021/2022
Jméno a příjmení: Adam Zvara
Login: xzvara01

POVODNE:Backed enumeration (enum s ciselnou hodnotou) je pouzity na vracianie ERROR CODES.
Nakoniec som sa rozhodol pouzit konstanty uložené v súbore error_codes.php, pretoze tie enums su celkom nepekne na citanie (je potrebne pristupovat ku value)

Options programu sú parsované pomocou getopt.
Hľadanie headeru ".IPPCODE22" prebieha vo while cykle aby sme preskočili možné komentáre na začiatku súboru.
Každý riadok je pred spracovaním zbavený komentárov a whitespacov.

Trieda Instruction reprezentuje jednu inštrukciu načítanú zo vstupu. Objekt inštrukcie je vytvorený po načítaní riadku a parameter pre vytvorenie je opcode. Priamo v konštruktore
sa inkrementuje počet inštrukcie (order), ktorý je statický pre celú triedu. Trieda inštrukcie má 2 metódy (start/end)element na začatie zapisovania v XML formáte.
Načítaný riadok je rozdelený na inštrukciu a argumenty. Následuje switch-case podľa typu načítanej inštrukcie. Jednotlivé vetvy switch-casu odpovedajú typom inštrukcií
(typ inštrukcie je daný počtom a typom argumentov zo zadania).

Po určení typu inštrukcie sa spustí metóda na zápis argumentov (write_arguments), ktorej parametrami sú načítané argumenty a predané typy argumentov. Argumenty sú prechádzané postupne a kontroluje sa, či sedí ich typ s príslušným regexom. Pre argument typu symbol sa identifikuje jeho typ: ak je to premenná, ponechá sa v celom tvare a jeho type bude 'var'.
Ak je to literál, rozdelí sa na čast pred '@' a časť po ňom. Pre ostané typy sú zavolané metody na porovnavanie s regexami, ktoré sú vytvorené zo stringového mena typu:

call_user_func(array($this, $type.'_match'), $curr_arg);
na príklad: pre type='var', sa zavolá funkcia $this->var_match($curr_arg)

Premienanie specialnych znakov zabezpecuje kniznica XMLWriter

