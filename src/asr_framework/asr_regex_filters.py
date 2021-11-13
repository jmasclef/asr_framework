import re

asr_regex_keepFilteredCharacters=re.compile("[^A-Za-z0-9'&µç_ùûüÿàâæçéèêëïîôœ-]+")
asr_regex_keepOnlytLetters=re.compile("[^A-Za-z'&µç_ùûüÿàâæçéèêëïîôœ-]+")
asr_regex_keepOnlyNumbers=re.compile("\D")
asr_regex_isValidEmailAdress=re.compile("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$")
asr_regex_cid=re.compile('cid[0-99]')
asr_regex_parenthesis=re.compile('\(.+\)')
asr_regex_brackets=re.compile('\[.+\]')


def asr_extract_parenthesis(input_string):
    return asr_regex_parenthesis.sub("",input_string)

def asr_extract_brackets(input_string):
    return asr_regex_brackets.sub("",input_string)

def asr_extract_brackets_content(input_string:str,opening_car='(',closing_car=')'):
    #les regex retirent tout entre l'ouverture de la toute première et la fermeture de la tout dernière
    string = input_string
    brackets_set = set(opening_car+closing_car)
    while set(string).intersection(brackets_set) == brackets_set:    #il y a les deux dans string
        first_opening_car = string.find(opening_car)
        first_closing_car = string.find(closing_car)
        # print(first_opening_car,first_closing_car,string)
        if first_closing_car>first_opening_car:
            #elles sont bien ordonnées
            string=string[:first_opening_car]+string[first_closing_car+1:]
        else:
            #elles sont inversées comme )ceci( => deux blanks
            tableau=list(string)
            tableau[first_opening_car]=' '
            tableau[first_closing_car]=' '
            string=''.join(tableau)

    if set(string).intersection(brackets_set) != set():
        #S'il en reste l'un des deux => blanks
        string=string.replace(opening_car,' ').replace(closing_car,' ')

    return string
