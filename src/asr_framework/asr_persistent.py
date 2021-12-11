import unittest

from os import path as os_path, walk as os_walk
from csv import writer as csv_writer, reader as csv_reader, QUOTE_ALL as csv_QUOTE_ALL

from asr_framework.asr_constantes import *

def asr_load_doc(file_name,encoding_value="utf-8",base_dir:str=None,split_lines:bool=False)->list:
    """
    Fonction standard de chargement d'un document texte
    :param file_name: nom relatif ou absolu, relatif à base_dir si défini sinon ou au dossier actif
    :param encoding_value: utf-8 par défaut
    :param base_dir: dossier de travail relatif ou absolu
    :param split_lines: split chaque ligne de mots
    :return: Une liste de chaînes non traitées ou, si split_lines est True, une liste de listes de mots
    """
    func_name = __name__ + '.' + 'asr_load_doc'
    if base_dir:
        file_to_open = os_path.normpath( os_path.join(os_path.abspath(base_dir), file_name) )
    else:
        file_to_open = os_path.abspath(file_name)

    if os_path.isfile(file_to_open):
        doc=[]
        with open(file_to_open,"r",encoding=encoding_value) as f:
            line=f.readline()
            while line:
                line = line[:-1] if line[-1]=="\n" else line
                doc.append(line.split() if split_lines else line)
                line=f.readline()
        return doc
    else:
        erreur_msg="{0}: Fichier introuvable '{1}'".format(func_name,file_to_open)
        asr_logger.error(erreur_msg)
        if ASR_MODE == ASR_MODE_DEBUG:
            raise NameError(erreur_msg)
        else:
            return None

def asr_save_doc(document:list,file_name:str,base_dir=None,encoding_value="utf-8",
                 binaryMode:bool=False,append_mode:bool=False,replace_if_exists:bool=True,join_lines:bool=False)->bool:
    """
    Fonction standard d'enregistrement fichier d'un document
    :param document: liste de chaînes de caractères non splittées
    :param file_name: nom relatif ou absolu, relatif à base_dir si défini sinon ou au dossier actif
    :param encoding_value: utf-8 par défaut
    :param base_dir: dossier de travail relatif ou absolu
    :param binaryMode: False par défaut, True=>mode binaire sans collation
    :param append_mode: Mode append, crée ou ajoute en fin de fichier existant, False par défaut
    :param replace_if_exists: Si le fichier existe déjà,écrase le par défaut (True) sinon retourne une erreure
    :param join_lines: document n'est pas une liste de chaines mais une liste de listes de mots. Joindre chaque ligne.
    :return: true
    """
    func_name = __name__ + '.' + 'asr_save_doc'
    if base_dir:
        file_to_open = os_path.normpath( os_path.join(os_path.abspath(base_dir), file_name) )
    else:
        file_to_open = os_path.abspath(file_name)

    if binaryMode:
        mode = "ab" if append_mode else "wb"
        encoding_param=None
    else:
        mode = "a" if append_mode else "w"
        encoding_param=encoding_value
    if not replace_if_exists:
        mode = mode.replace("w","x")
    try:
        with open(file_to_open,mode,encoding=encoding_param) as f:
            for line in document:
                f.write(" ".join(line) if join_lines else line)
                f.write("\n")
    except Exception as erreur:
        erreur_msg="{0}: Sauvegarde impossible pour '{1}'".format(func_name,file_to_open)
        asr_logger.error(erreur_msg)
        if ASR_MODE == ASR_MODE_DEBUG:
            raise NameError(erreur)
        else:
            erreur_msg="{0}: Erreur rencontrée: '{1}'".format(func_name,erreur)
            asr_logger.error(erreur_msg)
            return False

    if os_path.isfile(file_to_open):
        log_msg="{0}: Sauvegarde réussie pour '{1}'".format(func_name,file_to_open)
        asr_logger.debug(log_msg)
        return True
    else:
        log_msg="{0}: Sauvegarde impossible pour '{1}'".format(func_name,file_to_open)
        asr_logger.error(log_msg)
        if ASR_MODE == ASR_MODE_DEBUG:
            raise NameError(log_msg)
        else:
            return False

def asr_load_csv_rules(file_name:str=None,base_dir:str=None)->dict():
    """
    Charge un dictionnaire de corrections types static_rules ou dynamic_rules
    Les règles inscrites dans les static_rules sont inscrites manuellement et en complément des dynamic_rules
    Les dynamic_rules sont automatiquement produites par apprentissage et itérations successives
    :param file_name: nom du fichier de règles comme asr_static_rules.csv ou chemin complet
    :param base_dir: dossier de travail, souvent le dossier du dictionnaire ASR open-data/dictionnaires
    :return:
    """
    rules_dict = dict()
    func_name = __name__ + '.' + 'asr_load_csv_rules'
    if base_dir:
        file_to_open = os_path.normpath( os_path.join(os_path.abspath(base_dir), file_name) )
    else:
        file_to_open = os_path.abspath(file_name)
    if os_path.isfile(file_to_open):
        with open(file_to_open, newline='\n', encoding="utf-8") as csvfile:
            csv_dict = csv_reader(csvfile, delimiter=',', quotechar='\"')
            for line in csv_dict:
                rules_dict[line[0]] = line[1]
        return rules_dict
    else:
        erreur_msg="{0}: Fichier introuvable '{1}'".format(func_name,file_to_open)
        asr_logger.error(erreur_msg)
        if ASR_MODE == ASR_MODE_DEBUG:
            raise NameError(erreur_msg)
        else:
            return None

def asr_save_csv_rules(rules_dict:dict,file_name:str=None,base_dir:str=None)->bool:
    """
    Enregistre un dictionnaire de corrections types static_rules ou dynamic_rules
    :param file_name: nom du fichier de règles comme asr_static_rules.csv ou chemin complet
    :param base_dir: dossier de travail, souvent le dossier du dictionnaire ASR open-data/dictionnaires
    :return:
    """
    func_name = __name__ + '.' + 'asr_save_csv_rules'
    if base_dir:
        file_to_open = os_path.normpath( os_path.join(os_path.abspath(base_dir), file_name) )
    else:
        file_to_open = os_path.abspath(file_name)

    try:
        with open(file_to_open, 'w', newline='\n', encoding="utf-8") as csvfile:
            writer = csv_writer(csvfile, delimiter=',',
                                quotechar='\"', quoting=csv_QUOTE_ALL)
            rules_list = [ [ key , rules_dict[key] ] for key in rules_dict.keys()]
            rules_list.sort()
            writer.writerows(rules_list)
        return True
    except Exception as erreur:
        erreur_msg="{0}: Sauvegarde impossible pour '{1}'".format(func_name,file_to_open)
        asr_logger.error(erreur_msg)
        if ASR_MODE == ASR_MODE_DEBUG:
            raise NameError(erreur)
        else:
            erreur_msg="{0}: Erreur rencontrée: '{1}'".format(func_name,erreur)
            asr_logger.error(erreur_msg)
            return False


def mp_save_list(file_name:str,list_to_save:list,encoding_value="utf-8",binaryMode=False,append_mode=False,sort_list=True):
    # changes_str = ["\"" + word + "\",\"" + wholeIterationsRules[word] + "\"\n" for word in wholeIterationsRules.keys()]
    doc=[]
    for line in list_to_save:
        liste=[";".join(element) if isinstance(element,list) else str(element) for element in line ]
        liste_str=",".join(liste)
        doc.append(liste_str)
    if sort_list:
        doc.sort()
    asr_save_doc(file_name=file_name,document=doc,encoding_value=encoding_value,binaryMode=binaryMode,append_mode=append_mode)

def mp_load_list(file_name:str,encoding_value="utf-8"):
    doc=asr_load_doc(file_name=file_name,encoding_value=encoding_value)
    result=[]
    for line in doc:
        if "," in line:
            t=line.split(",")
            if ";" in t[1]:
                t0=t[0]
                t1=t[1].split(";")
                result.append([t0,t1])
            else:
                result.append(t)
        # else:
        #     result.append(line)
    return result

def asr_scan_folder(extension:str=".txt",base_dir:str=".")->list:
    # list = []
    # for root, dirs, files in os_walk(base_dir):
    #     for filename in files:
    #         if filename.endswith(extension):
    #             t = os_path.join(base_dir, filename)
    #             list.append(t)
    files_list=[]
    abs_base_dir=os_path.abspath(base_dir)
    for root, dirs, files in os_walk(abs_base_dir):
        for file_name in files:
            if root==abs_base_dir:
                files_list.append(file_name)
            else:
                # rep=os_path.normpath(root)
                files_list.append(os_path.join(root, file_name))
    return files_list

class test_asr_persistent_methods(unittest.TestCase):
    def setUp(self):
        self.test_filename="test_doc.txt"
        self.test_base_dir="../../open-data/misc"

    def test_asr_load_doc(self):
        doc_test=asr_load_doc(file_name=self.test_filename,base_dir=self.test_base_dir)
        self.assertEqual(doc_test,['Ligne 1', 'Ligne 2'])

    def test_asr_save_doc(self):
        doc_test=asr_load_doc(file_name=self.test_filename,base_dir=self.test_base_dir)
        self.assertTrue(asr_save_doc(document=doc_test,file_name=self.test_filename,base_dir=self.test_base_dir))
        # with self.assertRaises(Exception) as cm:
        #     asr_save_doc(document=doc_test,file_name=self.test_filename,base_dir=self.test_base_dir,replace_if_exists=False)
        #     the_exception = cm.exception
        # self.assertEqual(the_exception.error_code, 17)
        self.assertFalse(asr_save_doc(replace_if_exists=False,
                                      document=doc_test,file_name=self.test_filename,base_dir=self.test_base_dir))
        self.assertTrue(asr_save_doc(replace_if_exists=True,
                                     document=doc_test,file_name=self.test_filename,base_dir=self.test_base_dir))

if __name__ == '__main__':
    ASR_MODE=ASR_MODE_PRODUCTION
    unittest.main()