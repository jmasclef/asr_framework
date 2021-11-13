import unicodedata
import datetime
import zlib
import gzip
from operator import itemgetter

from .asr_constantes import log_file_name

def asr_strip_accents(word):
    return ''.join(c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) != 'Mn')

def asr_correct_letters_doubled(word):
    # ne fonctionne pas: "tttaaannnttt"
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

def print_log(str, new=False,double_output=False,file_name=log_file_name):
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%X")
    if new:
        mode = 'w'
    else:
        mode = 'a'
    if host_adress == host_adresses["local"]:
        print(timestamp, ':', str)
        if double_output:
            f = open(file_name, mode, encoding="utf_8")
            f.write(timestamp + ' : ' + str + '\n')
    else:
        f = open(file_name, mode, encoding="utf_8")
        f.write(timestamp + ' : ' + str + '\n')
        if double_output:
            print(timestamp, ':', str)

def print_log_double_output(str):
    print_log(str,double_output=True)

def asr_chunks(list, width):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(list), width):
        yield list[i:i + width]

def asr_compress_string(chaine:str,input_format='utf-8',zip_module=zlib):
    #https://www.rootusers.com/gzip-vs-bzip2-vs-xz-performance-comparison/
    #9 est le plus long à COMPRIMER (x4) mais le plus rapide à DECOMPRIMER (+8%)
    if input_format=='utf-8':
        if zip_module==zlib:
            result = zlib.compress(chaine.encode('utf-8'))
        elif zip_module==gzip:
            result = gzip.compress(chaine.encode('utf-8'), compresslevel=9)
        else:
            result = zip_module.compress(chaine.encode('utf-8'))
        return result #level= ne fonctionne pas sous linux
    elif input_format=='binary':
        if zip_module==zlib:
            result = zlib.compress(chaine,level=1)
        elif zip_module==gzip:
            result = gzip.compress(chaine, compresslevel=1)
        else:
            result = zip_module.compress(chaine)
        return result
    else:
        raise NameError('Unknown format')

def asr_decompress_toString(chaine:bytearray,input_format='utf-8',zip_module=zlib):
    if chaine is None:
        return None
    else:
        if input_format == 'utf-8':
            return zip_module.decompress(chaine).decode('utf-8')
        elif input_format == 'binary':
            return zip_module.decompress(chaine)
        else:
            raise NameError('Format Inconnu pour '+zip_module+'.decompress')
            return None


def asr_decompress_toList(chaine:bytearray,zip_module=zlib):
    chn= asr_decompress_toString(chaine,zip_module=zip_module)
    if chn is None:
        return []
    else:
        return eval(chn)

def asr_applyFunctionToMatrix(function,listA:list,listB:list):
    results=[]
    for indexA,elementA in enumerate(listA):
        for indexB, elementB in enumerate(listB):
            results.append([function(elementA,elementB),indexA,indexB])
    if len(results)>0:
        results.sort(key=itemgetter(0),reverse=True)
        return results[0]
    else:
        return []

def asr_listsIntersection(listA:list, listB:list):
    local_listA = listA.copy()
    local_listB = listB.copy()
    result=[]
    while len(local_listA)>0:
        element=local_listA.pop()
        if element in local_listB:
            local_listB.remove(element)
            result.append(element)
    return result

def asr_listsSubstraction(listA:list, listB_to_substract:list):
    local_listA = listA.copy()
    local_listB = listB_to_substract.copy()
    while len(local_listB)>0:
        element=local_listB.pop()
        if element in local_listA:
            local_listA.remove(element)
    return local_listA

def asr_concat_doc(line_of_words_list: list[str],end_line_carac=" ") :
    # if len(doc)==0:
    #     return ""
    # new_doc=doc[0]
    # for line in doc[1:]:
    #     new_doc=new_doc+end_line_carac+line
    # return  new_doc
    return end_line_carac.join(line_of_words_list)