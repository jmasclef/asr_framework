"""
    Copyright 2021 SEIDO CONSEILS S.A.S.
    This file is part of Framework Assistance Sémantique au Recrutement (ASR).

    Framework Assistance Sémantique au Recrutement (ASR) is free software:
    you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Framework Assistance Sémantique au Recrutement (ASR) is distributed
    in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Framework Assistance Sémantique au Recrutement (ASR).
    If not, see <https://www.gnu.org/licenses/>.
"""

import unittest
from unicodedata import category as unicodedata_category, normalize as unicodedata_normalize
from asr_framework.asr_constantes import *
from asr_framework.asr_regex_filters import *
asr_cleanRule_replaceWithSectionsMarkups = [
    # ATTENTION A L'ORDRE DES TRANSFORMATIONS!!! TOUS LES DOUBLONS EN PREMIERS PUIS LES COMPOSES
    ("...", MARKUP_EOP), (".\n", MARKUP_EOL), ("\n", MARKUP_EOL), (".", MARKUP_EOP), ("…", MARKUP_EOP),
    ("?", MARKUP_EOP), ("!", MARKUP_EOP),
    (MARKUP_EOL+'  '+MARKUP_EOL, MARKUP_EOL), (MARKUP_EOP+'  '+MARKUP_EOP, MARKUP_EOP),
    (MARKUP_EOP+'  '+MARKUP_EOL, MARKUP_EOL), (MARKUP_EOL+'  '+MARKUP_EOP, MARKUP_EOL)]

#Ici on remplace ce qui sera supprimé par ce qui sera gardé
asr_cleanRule_replace = [
    ("’", "'"), ("´", "'"), ("‘", "'"), ("''", "'"), #toutes les formes d'apostrophe sont simpifiées
    ("–","-"),
    ("œ", "oe"), ("æ", "ae"),                       #les ligatures sont simpifiées
    ("\\n", "\n"), ("\r", "\n"), ("\u2029", "\n"), ("\u2028", "\n"), ("\x85", "\n"), ("\x1e", "\n"), ("\x1d", "\n"),
    ("-\n", "\n"), ("&\n", "\n"),   #troncages de fin de ligne
    ("av. j.-c", "avant-jesus-christ"),("ap. j.-c", "après-jesus-christ"),("apr. j.-c", "après-jesus-christ"),
    ("[réf. nécessaire]"," ") #wiki
    ]


def asr_tokenize_string(input_string:str, split_in_sections_with_markups:bool=False,
                        drop_brackets_content:bool=False)->list[str]:
    """
    Nettoie une chaîne de caractères et retourne une liste de mots.
    Cette opération nettoie tous les nombres, caractères spéciaux, applique toutes les règles statiques et non grammaticales
    Les règles appliquées sont essentiellement des regex et des opérations sur les caractères
    :param input_string_line: un document constitué d'une chaîne de caractère complète, non splitée
    :param fill_with_section_markups: remplace les , . etc par des markups ?
    :param remove_brackets_contents: supprime tout ce qui est contenu dans () et dans [] ? (pour wikipedia)
    :return: liste de mots
    """

    futur_output_string = input_string.lower()

    if drop_brackets_content:
        #retire les contenus  (*****) ou [*****]
        futur_output_string=asr_drop_brackets_content(input_string=futur_output_string,opening_car='[',closing_car=']')
        futur_output_string=asr_drop_brackets_content(input_string=futur_output_string,opening_car='(',closing_car=')')
        futur_output_string=asr_drop_brackets_content(input_string=futur_output_string,opening_car='{',closing_car='}')

    #STEP 1 - Que des corrections, pas d'intervention sur les ponctuations - ex
    futur_output_string = asr_characterSubstitution(input_string=futur_output_string)

    #STEP 2 - Avant de modifier la ponctuation, retire les URL et les e-mails
    futur_output_string = asr_filterExpressionsWithPunctuations(input_string=futur_output_string)

    #STEP 3 - Isole les ponctuations des mots: 'salut!' devient 'salut !'
    futur_output_string = asr_isolatePunctuations(input_string=futur_output_string)

    #STEP 4 - Isolement de tous les \n (des mots et les uns des autres) puis agrégation
    futur_output_string = futur_output_string.replace('\n',' \n ')  # Isolement de chacun
    futur_output_string = " ".join(futur_output_string.split())     # Suppression des doubles blanks donc '\n \n'
    while '\n \n' in futur_output_string:
        futur_output_string = futur_output_string.replace('\n \n', '\n\n')  # Agrégation

    #STEP 5 - OPTION - Insère des balises pour repérer les fins de phrase et de ligne
    if split_in_sections_with_markups:
        #Cette opération supprime tous les \n et certaines ponctuations
        futur_output_string = asr_splitInSectionWithMarkups (input_string_line=futur_output_string)

    #STEP 6 - Remplace les dernières poncutations et certains caractères par des blanks
    futur_output_string = asr_regex_keepPonctuation.sub(" ",futur_output_string)
    futur_output_string== asr_regex_toBlank.sub(" ",futur_output_string)
    # On remplace certains caractères par des blanks: $,£,€,%,{,},(,),[,],§
    # Splitte certaines valeurs qui seront ensuite filtrées en nombres et sépare certaines () et []

    #STEP 7 - Filtre les mots, jette
    output_words_list = asr_cleanDrop_list(input_string=futur_output_string)
    if 'cid' in set(output_words_list):
        print("CID trouvé dans {}".format(input_string))
    # if "20072010" in output_words_list:
    #     print("Ici)")
    return output_words_list

def asr_filterExpressionsWithPunctuations( input_string:str )->str:
    """
    Avant toute opération sur les sections et la ponctuation, extrait ce qui contient de la ponctuation comme les URL et les adresses e-mail
    :param input_string: un document constitué d'une chaîne de caractère complète, non splitée
    :return: un document constitué d'une chaîne de caractère complète, non splitée
    """
    regex_sub_list= [ asr_regex_isValidEmailAdress, asr_regex_cid, asr_regex_https, asr_regex_www ]
    input_list = input_string.split()
    futur_output_list = []
    for word in input_list:
        results = [ regex_sub.sub('',word) for regex_sub in regex_sub_list]
        if set(results)=={word}:
            futur_output_list.append(word)
        # for regex_filter_function in regex_filter_functions:
        #     if regex_filter_function(word) != word:
        #         continue
        # if asr_regex_cid.sub("", word) != word:
        #     #c'est un cid[**]
        #     continue
        # futur_output_list.append(word)
        # if "@" in word and asr_regex_isValidEmailAdress.sub("", word) != word:
        #     # C'est une adresse mail: drop
        #     continue
        # if asr_regex_cid.sub("", word) != word:
        #     #c'est un cid[**]
        #     continue
        # try:
        #     if word[:4] == "www." or word[:8] == "https://"  or word[:7] == "http://" or word[:4] == "cid:":
        #         # C'est une URL ou un CID: drop
        #         continue
        #     else:
        #         futur_output_list.append(word)
        # except:
        #     # Mot trop court donc non et passe au finally
        #     futur_output_list.append(word)
    return " ".join(futur_output_list)

def asr_characterSubstitution ( input_string:str )->str:
    """
    Cette méthode effectue des corrections de caractères à l'intérieur des mots (formes d'apostrophe, ligatures, ...)
    Les règles appliquées sont définies plus haut sours la forme  asr_cleanRule_replace
    :param input_string: un document constitué d'une chaîne de caractère complète, non splitée
    :return: un document constitué d'une chaîne de caractère complète, non splitée
    """
    output_str_line = input_string
    for (expression, remplacement) in  asr_cleanRule_replace:
        while output_str_line.find(expression) >= 0:
            output_str_line = output_str_line.replace(expression, remplacement)

    return output_str_line

def asr_isolatePunctuations ( input_string:str )->str:
    """
    Cette méthode isole les ponctuations en les séparant des débuts et fins de mots: 'bonjour,' -> 'bonjour ,'
    :param input_string: une chaîne de caractère complète, non splitée
    :return: une chaîne de caractère complète, non splitée
    """
    input_str_list = input_string.split()
    output_str_list = []
    for word in input_str_list:
        left_word = [] #futur mot à gauche
        right_word = []#futur mot à droite
        while (match := asr_regex_startsWithPonctuation.search(word)) is not None:
            left_word.append(match.group())
            word=word[1:]
        while (match := asr_regex_endsWithPonctuation.search(word)) is not None:
            right_word.append(match.group())
            word=word[:-1]

        if left_word.__len__()>0:
            output_str_list.append("".join(left_word))
        if word.__len__()>0:
            output_str_list.append(word)
        if right_word.__len__()>0:
            right_word.reverse()
            output_str_list.append("".join(right_word))

    output_str_line = " ".join(output_str_list)

    return output_str_line

def asr_splitInSectionsWithMarkups(input_string:str)->str:
    """
    A partir des règles de remplacements   asr_cleanRule_replaceWithSectionsMarkups, 
    remplace certains agencements de (.) et de (EOL) par des markups qui peuvent être utiles pour séparer des phrases
    et des sections
    :param input_string: une chaîne de caractère complète, non splitée
    :return: une chaîne de caractère complète, non splitée
    """
    futur_output_string = input_string
    for (expression, correction) in asr_cleanRule_replaceWithSectionsMarkups:
        while expression in futur_output_string:
            futur_output_string = futur_output_string.replace(expression, " {} ".format(correction))
    return futur_output_string


def asr_cleanDrop_list(input_string: str)->list[str]:
    """
    Filtre certains mots:
    Trop courts si < MIN_WORD_LENGTH
    Retire une racine qu' puisqu' l' j' d' t' m' s' c' n'
    Retire les extrémités parmi -'& de façon récursive
    Retire les calculs, les nombres purs ou commençants par #
    Ne conserve que les caractères acceptés par asr_regex_keepFilteredCharacters

    :param input_string: une chaîne de caractère complète, non splitée
    :return: une liste de mots
    """
    # La longueur moyenne d’un mot est de 4,8 caractères.
    # Le mot médian a une longueur de 4 caractères.
    # Moins de 5% des mots ont plus de 10 caractères
    intput_words_list = asr_regex_toBlank.sub(" ",input_string).split()
    output_words_list = []

    for word in intput_words_list:
        if len(word) < MIN_WORD_LENGTH:
            continue
        try:
            if word[:3] in {"qu'"}:
                if len(word) > 3:
                    word = word[3:]
                else:
                    continue
            if word[:7] in {"puisqu'"}:
                if len(word) > 7:
                    word = word[7:]
                else:
                    continue
        except:
            pass
        try:
            while word[:1] in {"-", "'", "&"}:
                word = word[1:]
            while word[-1:] in {"-", "'", "&"}:
                word = word[:-1]
        except:
            pass
        try:
            if word[:2] in {"l'", "j'", "d'", "t'", "m'", "s'", "c'", "n'"}:
                if len(word) > 2:
                    word = word[2:]
                else:
                    continue
        except:
            pass

        if asr_regex_plushashtagnumber.sub("", word) == '':
            # c'est un mot du type #33 ou +45 etc
            continue
        if asr_regex_keepCalculus.sub("", word) == '':
            # c'est un nombre ou un calcul (-12.3+(54*5))=10ee4
            continue

        word = asr_regex_keepFilteredCharacters.sub("", word)  # ne garde que les lettres, chiffres et qlq caracteres
        # word_keepOnlyLetters = asr_regex_keepOnlytLetters.sub("", word)

        only_numbers_str= asr_regex_keepOnlyNumbers.sub("", word)
        if only_numbers_str == word:
            # c'est un nombre pur
            continue

        if (len(word)>10) and (2*len(only_numbers_str)>len(word)) :
            asr_logger.info("Abandon du mot {}".format(word))
            #C'est un mot de plus de 10 digits dont plus de la moitié sont des chiffres -> poubelle
            #RT-2012, iso50001 ok
            continue

        if len(word) < MIN_WORD_LENGTH:
            continue
        elif len(set(word))==1 and len(word)>4: # c'est un mot de 5 lettres constitué d'une répétition d'une seule lettre aaaaa xxxxx
            continue

        if (len(word)>10) and ( (extract_word:=asr_correct_letters_doubled(word)) !=word):
            asr_logger.info("Remplacement de {} par {}".format(word,extract_word))
            word=extract_word


        # if asr_regex_cid.sub('', word)=='':  # c'est un CID résidu d'un extract PDF
        #     continue

        output_words_list.append(word)

    return output_words_list


def asr_dropBracketsContents(input_string:str,opening_car='[',closing_car=']'):
    """
    Retire les contenus complets entre () ou {} ou []
    Utile pour wikipedia qui s'en sert pour les références et des liens externes
    Une regex simple retirerait tout entre l'ouverture de la toute première et la fermeture de la tout dernière
    :param input_string:  un document constitué d'une chaîne de caractère complète, non splitée
    :param opening_car: Ce qui ouvre la section à jeter
    :param closing_car: Ce qui ferme la section à jeter
    :return:  un document constitué d'une chaîne de caractère complète, non splitée
    """
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


def asr_filter_stopwords(line_of_words_list: list, filter_section_markups=True)->list:
    if filter_section_markups:
        stop_words_custom_list = FRENCH_STOPWORDS_LIST_W_MARKUPS
    else:
        stop_words_custom_list = FRENCH_STOPWORDS_LIST_WO_MARKUPS

    new_doc = [word for word in line_of_words_list
               if (word.lower() not in stop_words_custom_list)
               and not asr_isComposedWithStopwordsOrNumbers(word.lower())]

    return new_doc


def asr_filter_sectionsMarkups(resume):
    return " ".join([word for word in resume.split() if word not in RESUME_SECTIONS_MARKUPS])


def asr_isComposedWithStopwordsOrNumbers(word:str)->bool:
    """
    Décompose un mot articulé de - ou & ou / et vérifie si chaque composant est un stopword ou un nombre
    Filtre les 'oui/non', '25/12/2021' etc
    :param word: mot composé
    :return: vrai si tous ( all() ) les mots extraits sont des nombres ou des stopwords
    """
    if "-" not in word and "&" not in word and "/" not in word:
        return False
    word = word.replace('&', '-').replace('/', '-')
    words = word.split('-')
    areStopWords = all(
        [(word in FRENCH_STOPWORDS_LIST_WO_MARKUPS) or (asr_regex_keepOnlyNumbers.sub("", word) == word)
            for word in words])
    return areStopWords


def asr_isFrench(document_as_string: str,floor_ratio=None)->float:
    """
    Retourne un ratio de stopwords français dans le texte ou un booleen, indicateur de document français
    Sur quelques essais, il ressort une moyenne de 39% de stopwords dans une phrase française
    :param document_as_string: string car opération avant la tokenisation
    :param ratio_seuil: si None, la fonction retourne un score sous forme de float, sinon un booleen
    :return: booleen si seuil est défini sinon ratio
    """
    if isinstance(document_as_string,list):
        func_name=__name__+'.'+'asr_isFrench'
        asr_logger.info("{0} demande une chaine (opération de pré-tokenisation), {0} a convertit la liste en chaîne".format(func_name))
        document_as_string=" ".join(document_as_string)

    line_of_words_list = document_as_string.lower().split() #supprime les double blanks courants en texte brut et filtré

    if len(line_of_words_list)==0:
        ratio=0
    else:
        extract_sw=[word for word in line_of_words_list if word in FRENCH_STOPWORDS_LIST_WO_MARKUPS]
        ratio=len(extract_sw)/len(line_of_words_list)
    if floor_ratio:
        return True if ratio>floor_ratio else False
    else:
        return ratio

def asr_strip_accents(word):
    return ''.join(c for c in unicodedata_normalize('NFD', word) if unicodedata_category(c) != 'Mn')

def asr_correct_letters_doubled(word):
    if word.__len__() < 8:
        return word
    n_word=word
    n_word_sub=n_word[::2]
    while ("".join([lettre*2 for lettre in list(n_word_sub)]) == n_word):
        n_word=n_word_sub
        n_word_sub = n_word[::2]
    n_word_sub=n_word[::3]
    while ("".join([lettre*3 for lettre in list(n_word_sub)]) == n_word):
        n_word=n_word_sub
        n_word_sub = n_word[::3]
    return n_word

class test_asr_tokenisation_methods(unittest.TestCase):

    def test_asr_isComposedWithStopwordsOrNumbers(self):
        self.assertTrue(asr_isComposedWithStopwordsOrNumbers('27-12-2021'))
        self.assertTrue(asr_isComposedWithStopwordsOrNumbers('oui/non'))

    def test_asr_isFrench(self):
        self.assertEqual(asr_isFrench('Voici bien du français pourtant'),0.8)
        self.assertTrue(asr_isFrench('Voici bien du français pourtant',floor_ratio=0.5))

    def test_asr_filter_stopwords(self):
        self.assertEqual(asr_filter_stopwords('Voici bien du français pourtant'.split()),['français'])

    def test_asr_dropBracketsContents(self):
        self.assertEqual(asr_dropBracketsContents('Faut jeter [ça] stp').split(),['Faut', 'jeter', 'stp'])

    def test_asr_cleanDrop_list(self):
        self.assertEqual(asr_cleanDrop_list('\'avait\' &oui& -ça-'),['avait', 'oui', 'ça'])
        self.assertEqual(asr_cleanDrop_list('qu\'il puisqu\'il j\'ai t\'as l\'a d\'abord m\'a s\'est c\'est n\'ont'),
                         ['il', 'il', 'ai', 'as', 'abord', 'est', 'est', 'ont'])
        self.assertEqual(asr_cleanDrop_list('a 345 12.34 12,34 2*(4+3)=14 c++ c#'),['c++', 'c#'])
        self.assertEqual(asr_cleanDrop_list('(pp, mm, sd)'),['pp', 'mm', 'sd'])
        self.assertEqual(asr_cleanDrop_list('fffooorrrmmmaaatttiiiooonnn'),['formation'])
        self.assertEqual(asr_cleanDrop_list('___________'),[])
        self.assertEqual(asr_cleanDrop_list('eric-256484'),[])

    def test_asr_isolatePunctuations(self):
        self.assertEqual(asr_isolatePunctuations("bon, alors? écoute: ça va. si.non; je le dirai!"),
                         'bon , alors ? écoute : ça va . si.non ; je le dirai !')

    def test_asr_characterSubstitution(self):
        self.assertEqual(asr_characterSubstitution(" l’ l´ l‘ œ''æ"), " l' l' l' oe'ae")

    def test_asr_filterExpressionsWithPunctuations(self):
        self.assertEqual(
            asr_filterExpressionsWithPunctuations("une url www.monurl.com https://www.monurl.com https://monurl.com et ma mail ma.mail@mailbox.com"),
            "une url et ma mail")

if __name__ == '__main__':
    unittest.main()
