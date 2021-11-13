
asr_cleanRule_miseEnBlanks = [",", "  ", "", "◆", "(", ")", "\f", "", "►", "►", "", "", "", "■", "▪", "", "", "", "",
                             "", "➢", "\x02", "\xa0", "\u0000", "\u0004", "\t", "", "·",
                             "—", "–", "◦", "❖", "", "", "<", ">", ">", "›", "", "‐", "✓", "●", "", "•", "", "",
                             "", "*", "=", "", "",
                             "", "", "", "", "", "", "", "", "❑", "▫", "−", "ø", "→", "§", "¤", "|", "|", "{",
                             "}", "", " etc ", "", "", "", "✔",
                             "★", "✩", "", "- ", " -", "", "☎", "", "", "℡", "", "", "", "", "", "", "",
                             "", "", "", "", "", "", "",
                             "", "", "☆", "", "", "", "", "✰", "", "", "", "",
                             "[réf. nécessaire]"]

asr_cleanRule_suppressions = ["“", "”", "\"", "«", "»", "%"]  # ,"-"]

asr_cleanRule_remplacementsSections = [("...", " asr_eop_asr "), ("…", " asr_eop_asr "),
                                      (". ", " asr_eop_asr "), (".\n", " asr_eop_asr asr_eol_asr "), (".", " "),
                                      ("?", " asr_eop_asr "), ("!", " asr_eop_asr "),
                                      ("\n\n", " asr_eos_asr "), ("asr_eop_asr asr_eos_asr", "asr_eos_asr"),
                                      ("\n", " asr_eol_asr "),
                                      ("asr_eol_asr asr_eol_asr", "asr_eos_asr"), ("asr_eop_asr asr_eop_asr", "asr_eop_asr"),
                                      ("asr_eos_asr asr_eos_asr", "asr_deos_asr"), ("asr_eos_asr asr_eol_asr", "asr_deos_asr"),
                                      ('asr_deos_asr asr_eos_asr','asr_deos_asr'),('asr_deos_asr asr_deos_asr','asr_deos_asr'),
                                      ("asr_eol_asr asr_eos_asr", "asr_deos_asr"), ("asr_eop_asr", " "),
                                      ("asr_eol_asr", " ")]  # ,("asr_eol_asr"," "),("asr_eos_asr"," ")]

asr_cleanRule_remplacements = [
    # ("/", "-"), ("#","_sharp"),("+","_plus"),
    ("’", "'"), ("´", "'"), ("‘", "'"), ("''", "'"),
    # ("--", "-"), ("²", "2"),
    ("Œ", "oe"), ("œ", "oe"), ("æ", "ae"), ("__", "_"),
    (",,", " "), #wiki
    ("\r", "\n"), ("\n.", "\n"),
    ("\u2029", "\n"), ("\u2028", "\n"), ("\x85", "\n"), ("\x1e", "\n"), ("\x1d", "\n"),
    (" \n", "\n"), ("\n ", "\n"), ("\no ", "\n"),
    (" \n", "\n"), ("\n-", "\n"), ("-\n", "\n"),
    ("av. j.-c", "avant-jesus-christ"),("ap. j.-c", "après-jesus-christ"),("apr. j.-c", "après-jesus-christ")
    ]


def asr_cleanTokenize_doc(document, keep_empty_line=False, fill_with_section_markups=False, export_mails=False):
    # applique à une chaîne str ou une liste de chaînes str
    if isinstance(document, list):
        isString = False
        if fill_with_section_markups:
            document = MARKUP_EOL.join(document)
            document = [document]
    else:
        isString = True
        document = [document]

    new_document = []
    for str_line in document:
        str_line = str_line.lower()
        str_line = asr_clean_string(str_line, fill_with_section_markups)

        str_line = str_line.split()
        str_line = asr_tokenize_line(str_line)

        if not keep_empty_line and len(str_line) == 0:
            continue

        str_line = " ".join(str_line)

        new_document.append(str_line)

    if isString or fill_with_section_markups:
        new_document = " ".join(new_document)
        # if isString:
        #     new_document=" ".join(new_document)
        # if fill_with_section_markups:
        #     new_document = MARKUP_EOL.join(new_document)
    return new_document


def asr_clean_string(input_str_line, fill_with_section_markups=False, remove_brackets_contents=False):
    output_str_line = input_str_line.copy()

    if remove_brackets_contents:
        output_str_line = asr_extract_brackets_content(output_str_line)  # supprime les output_str_lines (*****)
        output_str_line = asr_extract_brackets_content(output_str_line, opening_car='[',
                                                       closing_car=']')  # supprime les output_str_lines (*****)

    for (expression, remplacement) in asr_cleanRule_remplacements:
        while output_str_line.find(expression) >= 0:
            output_str_line = output_str_line.replace(expression, remplacement)

    for expression in asr_cleanRule_miseEnBlanks:
        while output_str_line.find(expression) >= 0:
            output_str_line = output_str_line.replace(expression, " ")

    for expression in asr_cleanRule_suppressions:
        while output_str_line.find(expression) >= 0:
            output_str_line = output_str_line.replace(expression, "")

    for (expression, remplacement) in asr_cleanRule_remplacements:
        while output_str_line.find(expression) >= 0:
            output_str_line = output_str_line.replace(expression, remplacement)

    if fill_with_section_markups:
        for (expression, remplacement) in asr_cleanRule_remplacementsSections:
            while expression in output_str_line:
                output_str_line = output_str_line.replace(expression, remplacement)
    else:
        while '\\n' in output_str_line:
            output_str_line = output_str_line.replace('\\n', ' ')
        while '\n' in output_str_line:
            output_str_line = output_str_line.replace('\n', ' ')
    # attention traitement conditionnel des points plus en amont, ceux qui ont survécu sont remplacés par des blancs
    output_str_line = output_str_line.replace('.', ' ')

    output_str_line = " ".join(output_str_line.split())
    return output_str_line


def asr_tokenize_line(line_of_words_list: list[str]):
    output_line_of_words_list = []

    for word in line_of_words_list:
        if len(word) < MIN_WORD_LENGTH:
            continue
        if "@" in word:
            if asr_regex_isValidEmailAdress.sub("", word) == '':
                continue
        if "€" in word:
            continue
        try:
            if word[:3] == "www" or word[:4] == "cid:":
                continue
            if word[:3] in {"qu'"}:
                if len(word) > 3:
                    word = word[3:]
                else:
                    continue
        except:
            pass
        try:
            while word[:1] in {".", "-", "'"}:
                word = word[1:]
            while word[-1:] in {".", "-", "'"}:
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
        word = asr_regex_keepFilteredCharacters.sub('', word)  # ne garde que les lettres, chiffres et qlq caracteres
        word_keepOnlyNumbers = asr_regex_keepOnlyNumbers.sub("", word)
        # word_keepOnlyLetters = asr_regex_keepOnlytLetters.sub("", word)
        if len(word) < MIN_WORD_LENGTH:
            continue
        if word_keepOnlyNumbers == word:  # c'est un nombre pur
            continue
        # if word_keepOnlyLetters == "_plus":  # c'est un +33 par ex
        #     continue
        # if word_keepOnlyLetters == "_sharp":  # c'est un #5 par ex
        #     continue
        # if asr_regex_cid.sub('', word)=='':  # c'est un CID
        #     continue

        # if (len(word)>=5) and (len(word_keepOnlyNumbers)>len(word_keepOnlyLetters)):    #mix de chiffres et de lettres
        #         continue

        output_line_of_words_list.append(word)

    return output_line_of_words_list


def asr_filter_stopwords(line_of_words_list: list, filter_section_markups=True):
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


def asr_isComposedWithStopwordsOrNumbers(word):
    if "-" not in word and "&" not in word and "/" not in word:
        return False
    word = word.replace('&', '-').replace('/', '-')
    words = word.split('-')
    areStopWords = all(
        [(word in FRENCH_STOPWORDS_LIST_WO_MARKUPS) or (asr_regex_keepOnlyNumbers.sub("", word) == word) for word in
         words])
    return areStopWords
