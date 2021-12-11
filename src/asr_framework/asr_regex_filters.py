from re import compile as re_compile

# asr_regex_keepFilteredCharacters=re_compile("[^A-Za-z0-9'&µç_ùûüÿàâæçéèêëïîôœ-]+")

asr_regex_keepFilteredCharacters=re_compile("[^A-Za-z0-9'&µçùûüÿàâçéèêëïîô\-²+#_]+")
#tous les caractères conservés par le clean
#le + est conservé pour c++ ou j++ principalement
#le # et le _ sont conservés pour c# ou #tous_ensemble
asr_regex_keepOnlytLetters=re_compile("[^A-Za-z'&µç_ùûüÿàâæçéèêëïîôœ\-]+")
asr_regex_keepOnlyNumbers=re_compile("\D")  #les nombres à virgule et point sont splites par virgule et point
asr_regex_isValidEmailAdress=re_compile("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$")
asr_regex_cid=re_compile('\[?\(?cid:?[0-9]+\]?\)?')
asr_regex_https=re_compile('\[?\(?https?://')
asr_regex_www=re_compile('\[?\(?www\.')
asr_regex_parenthesis=re_compile('\(.+\)')  #.+ séquence quelconque
asr_regex_brackets          =re_compile('\[.+\]')     #.+ séquence quelconque
asr_regex_plushashtagnumber =   re_compile('[\#\+]\d+')
asr_regex_keepCalculus=re_compile("[?*?/?\+?\-?\=\d+?,?\.\d+ee?\(?\)?\[?\]<>!]")  #contient <>!=+-*/()[],. ee et nombre
asr_regex_punctuation = '[\.,!\?;:…\n]'
asr_regex_toBlank = re_compile('[\$£€%\{\}\(\)\[\]§]')
asr_regex_keepPonctuation =   re_compile(asr_regex_punctuation) #asr_regex_keepPonctuation.sub(" ",chn)
asr_regex_startsWithPonctuation =   re_compile('^'+asr_regex_punctuation) #asr_regex_keepPonctuation.sub(" ",chn)
asr_regex_endsWithPonctuation =   re_compile(asr_regex_punctuation+'$') #asr_regex_keepPonctuation.sub(" ",chn)

# asr_regex_markup = re_compile('.+\#ASR_EO.\#.+') fonctionne pas

# https://docs.python.org/fr/3/library/re.html
# . any char + one or more times .+ any repeated char
# ? once or zero time ex home?-brew pour home-brew ou homebrew
def asr_extract_parenthesis(input_string):
    return asr_regex_parenthesis.sub("",input_string)

def asr_extract_brackets(input_string):
    return asr_regex_brackets.sub("",input_string)

