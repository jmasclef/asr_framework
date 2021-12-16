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

import datetime

from zlib import compress as zlib_compress, decompress as zlib_decompress
from gzip import compress as gzip_compress, decompress as gzip_decompress
from operator import itemgetter
from hashlib import md5 as hashlib_md5
from os import path as os_path, getcwd as os_getcwd, mkdir as os_mkdir
from csv import reader as csv_reader
from zipfile import ZipFile
from shutil import rmtree as shutil_rmtree

from .asr_constantes import *

def asr_hashString_md5(string:str):
    return hashlib_md5(string.encode()).hexdigest()

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

def asr_compress_string(chaine:str,input_format='utf-8',zip_module='zlib'):
    #https://www.rootusers.com/gzip-vs-bzip2-vs-xz-performance-comparison/
    #9 est le plus long à COMPRIMER (x4) mais le plus rapide à DECOMPRIMER (+8%)
    possible_modules = {'zlib','gzip'}
    possible_formats = {'utf-8','binary'}
    func_name=__name__+'.'+'asr_compress_string'

    if zip_module not in possible_modules:
        erreur_msg='{0}: Mauvais nom de module de dé/compression, choisir parmi {1} '.format(func_name,possible_modules)
        asr_logger.error(erreur_msg)
        if ASR_MODE==ASR_MODE_DEBUG:
            raise NameError(erreur_msg)
        else:
            zip_module='zlib'
            asr_logger.warning("{0}: Fixe le module de dé/compression à {1}".format(func_name,zip_module))
    elif input_format not in possible_formats:
        erreur_msg='{0}: Mauvais format de dé/compression, choisir parmi {1} '.format(func_name,possible_formats)
        asr_logger.error(erreur_msg)
        if ASR_MODE==ASR_MODE_DEBUG:
            raise NameError(erreur_msg)
        else:
            input_format='utf-8'
            asr_logger.warning("{0}: Fixe le format de fichier à {1}".format(func_name,input_format))
    else:
        if input_format=='utf-8':
            if zip_module=='zlib':
                return zlib_compress(chaine.encode('utf-8'))
            elif zip_module=='gzip':
                return gzip_compress(chaine.encode('utf-8'), compresslevel=9)
        elif input_format=='binary':
            if zip_module=='zlib':
                return zlib_compress(chaine,level=1)
            elif zip_module=='gzip':
                return gzip_compress(chaine, compresslevel=1)

def asr_decompress_toString(chaine:bytearray,input_format='utf-8',zip_module='zlib'):
    if chaine is None:
        return None
    else:
        possible_modules = {'zlib','gzip'}
        possible_formats = {'utf-8','binary'}
        func_name=__name__+'.'+'asr_decompress_toString'

        if zip_module not in possible_modules:
            erreur_msg='{0}: Mauvais nom de module de dé/compression, choisir parmi {1} '.format(func_name,possible_modules)
            asr_logger.error(erreur_msg)
            if ASR_MODE==ASR_MODE_DEBUG:
                raise NameError(erreur_msg)
            else:
                zip_module='zlib'
                asr_logger.warning("{0}: Fixe le module de dé/compression à {1}".format(func_name,zip_module))
        elif input_format not in possible_formats:
            erreur_msg='{0}: Mauvais format de dé/compression, choisir parmi {1} '.format(func_name,possible_formats)
            asr_logger.error(erreur_msg)
            if ASR_MODE==ASR_MODE_DEBUG:
                raise NameError(erreur_msg)
            else:
                input_format='utf-8'
                asr_logger.warning("{0}: Fixe le format de fichier à {1}".format(func_name,input_format))
        else:
            if zip_module=='zlib':
                unzip_function=zlib_decompress
            elif zip_module=='gzip':
                unzip_function=gzip_decompress
            if input_format == 'utf-8':
                return unzip_function(chaine).decode('utf-8')
            elif input_format == 'binary':
                return unzip_function(chaine)

def asr_decompress_toList(chaine:bytearray,zip_module='zlib')->list:
    if chn:=asr_decompress_toString(chaine,zip_module=zip_module) is None:
        return []
    else:
        return eval(chn)

def asr_applyFunctionToMatrix(function,listA:list,listB:list):
    """
    Applique function à chaque binôme: function(element_de_listA,element_de_listB)
    Retourne la plus forte valeur avec les index
    Utilité à vérifier
    :param function:
    :param listA:
    :param listB:
    :return: plus forte valeur avec les index
    """
    # results=[]
    # for indexA,elementA in enumerate(listA):
    #     for indexB, elementB in enumerate(listB):
    #         results.append([function(elementA,elementB),indexA,indexB])
    # if len(results)>0:
    #     results.sort(key=itemgetter(0),reverse=True)
    #     return results[0]
    # else:
    #     return []
    raise NameError('Utilité de la fonction à vérifier')

def asr_listsIntersection(listA:list, listB:list):
    """
    Intersection de listes qui gère les doublons.
    Si un élément est deux fois présent dans les deux alors retourne l'élément en double,
    ce qui n'est pas le cas avec un set()
    De même, si on utilise [value for value in listA if value in listB]
    alors un doublon de listA présent une fois en listB est retrouné deux fois ce qui n'est pas le cas ici
    :param listA:liste A d'éléments
    :param listB:liste B d'éléments
    :return: liste d'éléments en intersection avec doublons potentiels
    """
    local_listA = listA.copy()
    local_listB = listB.copy()
    result=[]
    while len(local_listA)>0:
        #tant qu'il y a des éléments dans A, retire un élément
        if element:=local_listA.pop() in local_listB:
            #si l'élément retiré existe aussi dans B, alors 1) retire le de B
            local_listB.remove(element)
            # et 2) comme l'élément ETAIT présent dans les deux, inclue le dans l'intersection
            # donc si le même élément réapparait dans A il faudra aussi qu'il réapparaisse dans B pour apparaitre
            # deux fois dans l'intersection
            result.append(element)
    return result

def asr_listsSubstraction(listA:list, listB_to_substract:list)->list:
    """
    Soustraction de listes qui gère les doublons.
    Si un élément est deux fois présent dans listA mais une seule fois dans listB il ne sera retiré qu'une seule fois,
    ce qui n'est pas le cas avec un set()
    De même, si on utilise [value for value in listA if value not in listB]
    :param listA: liste A d'éléments, à réduire avec listB_to_substract
    :param listB_to_substract:liste B d'éléments à retirer de listA
    :return: liste d'éléments résultant de la soustracton
    """
    local_listA = listA.copy()
    local_listB = listB_to_substract.copy()
    if listA.__len__()>0:
        while len(local_listB)>0:
            #tant qu'il y a des éléments dans B, retire un élément
            if element:=local_listB.pop() in local_listA:
                #si l'élément retiré existe aussi dans A, alors 1) retire le de A
                local_listA.remove(element)
                # donc si le même élément réapparait dans B il faudra aussi qu'il réapparaisse dans A pour être retiré
                # deux fois
        return local_listA
    else:
        return []

def asr_concat_doc(line_of_words_list: list[str],end_line_carac=" ") :
    # if len(doc)==0:
    #     return ""
    # new_doc=doc[0]
    # for line in doc[1:]:
    #     new_doc=new_doc+end_line_carac+line
    # return  new_doc
    return end_line_carac.join(line_of_words_list)

def asr_import_lexique383tsv(zip_file_name='Lexique383.tsv.zip',base_dir='./open-data/third-party/',remove_duplicates=True):
    """
    Importe les données de Lexique383
    Permet de construire une base de règles mot -> lemme
    Filtre les mots trop petits
    Construit aussi une liste de mots français
    :param zip_file_name: Le fichier source ne nécessite que le fichier tsv, l'archive Lexique383.tsv.zip a été reconstituée avec ce seul fichier
    :param remove_duplicates: les règles A->A sont par défaut supprimées
    :return: un dict de règles 'mot' : 'lemme' ainsi qu'une liste des mots français et une table de lemme possibles pour les mots désaccentués
    """
    func_name=__name__+'.'+'asr_load_lexique383tsv'
    rules_dict = dict()
    frenchWords_set = set()
    temp_folder_name=os_path.normpath(os_path.join(os_path.abspath(base_dir),'./temp_folder/'))
    target_file_name='Lexique383.tsv'
    existing_temp_folder=True if os_path.isdir(temp_folder_name) else False
    csv_file_to_read=os_path.join(temp_folder_name,target_file_name)
    extract_list=asr_extractZipToFolder(input_zip_filename=zip_file_name,base_dir=base_dir,
                                        target_folder_name=temp_folder_name,unzip_only_files={target_file_name})
    if extract_list.__len__()>0:
        asr_logger.info('{0}: Création du fichier temporaire {1}'.format(func_name,csv_file_to_read))
        with open(csv_file_to_read, newline='\n', encoding="utf-8") as csvfile:
            csv_dict = csv_reader(csvfile, delimiter='\t', quotechar='\"')
            for line in csv_dict:
                key = line[0]
                value = line[2]
                if len(key) > MIN_WORD_LENGTH and len(value) > MIN_WORD_LENGTH:
                    frenchWords_set.add(key)
                    if not remove_duplicates or key!=value:
                        rules_dict[key] = value

        if existing_temp_folder:
            asr_logger.warning('{0}: Le dossier temporaire {1} existait déjà; il ne sera pas supprimé'.format(func_name,temp_folder_name))
        else:
            try:
                shutil_rmtree(temp_folder_name, ignore_errors=True)
                asr_logger.info('{0}: Suppression du dossier temporaire {1}'.format(func_name,temp_folder_name))
            except:
                asr_logger.warning('{0}: Echec de la suppression du dossier temporaire {1}'.format(func_name,temp_folder_name))
    else:
        erreur_msg='{0}: Extraction des règles du Lexique383 a échoué'.format(func_name)
        asr_logger.error(erreur_msg)
        if ASR_MODE==ASR_MODE_DEBUG:
            raise NameError(erreur_msg)

    frenchWords_list=list(frenchWords_set)
    accented_lemmas_suggestions=dict()
    for word in frenchWords_list:
        woaccent= asr_strip_accents(word)
        if woaccent!=word:
            if woaccent in accented_lemmas_suggestions:
                accented_lemmas_suggestions[woaccent].append(word)
            else:
                accented_lemmas_suggestions[woaccent]= [ word ]


    frenchWords_list.sort()
    return rules_dict, frenchWords_list, accented_lemmas_suggestions

def asr_extractZipToFolder(*,input_zip_filename:str, base_dir:str=None, target_folder_name:str='temp_folder',
                           unzip_only_files:set = None )->dict:
    # Unzip un fichier
    extracted_files_dict=dict()
    func_name=__name__+'.'+'asr_extractZipToFolder'
    abs_target_folder_name=os_path.abspath(target_folder_name)
    if base_dir:
        abs_base_dir=os_path.abspath(base_dir)
        zip_filename=os_path.normpath(os_path.join(abs_base_dir,input_zip_filename))
        if not(os_path.isdir(abs_base_dir)):
            erreur_msg="{0}: Dossier introuvable '{1}'".format(func_name,abs_base_dir)
            asr_logger.critical(erreur_msg)
            raise NameError(erreur_msg)
    else:
        zip_filename = os_path.abspath(input_zip_filename)
    if os_path.isfile(zip_filename):
        asr_logger.debug("{0}: Ouverture du fichier ZIP: {1}".format(func_name,zip_filename))
    else:
        erreur_msg="{0}: Fichier ZIP introuvable '{1}'".format(func_name,zip_filename)
        asr_logger.critical(erreur_msg)
        raise NameError(erreur_msg)
    with ZipFile(zip_filename, 'r') as zipObj:
        if unzip_only_files:
            inZip_extracted_files_list = [ inZip_filename for inZip_filename in zipObj.namelist()
                                                if (os_path.split(inZip_filename)[1] ) in unzip_only_files ]
        else:
            inZip_extracted_files_list = zipObj.namelist()

        if inZip_extracted_files_list.__len__()>0:
            asr_logger.debug("{0}: Extraction de {1} fichier(s)".format(func_name,inZip_extracted_files_list.__len__()))
            if not os_path.isdir(abs_target_folder_name):
                asr_logger.info("{0}: Dossier {1} non trouvé, création du dossier".format(func_name,abs_target_folder_name))
                os_mkdir(abs_target_folder_name)
            zipObj.extractall(members=inZip_extracted_files_list,path=abs_target_folder_name)
        else:
            if unzip_only_files:
                asr_logger.warning('{0}: Le fichier ZIP {1} ne contient aucun fichier correspondant à la liste: {2}'
                                   .format(func_name,zip_filename,unzip_only_files))
            else:
                asr_logger.warning('{0}: Le fichier ZIP {1} ne contient aucun fichier'.format(func_name,zip_filename))

    return [ [ inZip_extracted_filename, os_path.normpath(os_path.join(abs_target_folder_name, inZip_extracted_filename)) ]
                    for inZip_extracted_filename in inZip_extracted_files_list ]