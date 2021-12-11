# definit les objet lemma et dictionary
import csv
import os
from operator import itemgetter, attrgetter
from difflib import SequenceMatcher
from csv import reader as csv_reader
from math import log
from numpy import linalg

from asr_framework.asr_constantes import *
from asr_framework.asr_tokenisation import asr_strip_accents
from asr_framework.asr_persistent import asr_load_csv_rules, asr_save_doc
asr_similarityLimit_forAttractivity=0.6

class asr_token:
    def __init__(self,libelle,load_full_data=False):
        self.text=libelle.lower()
        self.count = 1
        self.documents_count = 1
        # self.first_word=None
        # self.tf_idf = 0
        # self.inSpacyVocab=False
        self.inFrenchVocab=False
        if load_full_data==False:
            #creation d'un token
            self.length=len(self.text)
            self.woaccent=asr_strip_accents(libelle.lower())
            if self.woaccent != self.text:
                self.letters="".join(set(self.woaccent))
            else:
                self.woaccent=''
                self.letters="".join(set(self.text))
            self.letters_number=len(self.letters)
        else:
            #mode sans calcul toutes les infos sont chargees depuis un csv
            self.length=0
            self.letters=''
            self.letters_number=0
            self.woaccent=''

        self.idf=None
        self.attractivity=None
        self.frequency=None
        self.precision=None

    def __repr__(self):
            return repr((self.text, self.count, self.documents_count, self.idf,self.length,self.letters,self.letters_number))

    def COMPUTE_ATTRACTIVITY(self,gensim_model,default_similarity_floor=asr_similarityLimit_forAttractivity,max_wordsToScan=1000):
        if (self.text in gensim_model.wv.key_to_index) and (self.attractivity is None):
            lscore = 1
            minwords = 40
            pas = 10
            while lscore > default_similarity_floor and minwords < (
                    max_wordsToScan + pas):  # rentre des mots tant qu'on est dans la fenêtre de similarité
                sim_array = gensim_model.wv.most_similar(self.text, topn=minwords)
                lword, lscore = sim_array[-1]
                minwords += pas

            self.attractivity = len([word for word, score in sim_array if score >= default_similarity_floor])

        return self.attractivity

    def IS_LETTERS_DOUBLED(self):
        if self.letters.__len__()<8:
            return False
        if (set(self.text)==set(self.text[::2])) or (set(self.text)==set(self.text[::3])):
            return True
        else:
            return False

class asr_dictionary:
    def __init__(self,file_name=None,load_dynamic_rules=True,base_dir=None):
        # self.dictionary=[]
        self.index=0
        self.tokens=dict()
        self.static_rules_tokens=dict()
        self.dynamic_rules_tokens=dict()
        self.base_dir = None                    #version calculée sur la base ou non de base_dir
        self.base_dir = base_dir        #version originale de l'info pour distinguer le paramétrage automatique
        self.static_rules_loaded=False
        self.dynamic_rules_loaded = False
        self.commonUsesRules_loaded=False
        self.commonUsesRules_map=dict()         # initial/target possibilities
        self.commonUsesRules_classes = dict()   # classes d'usage des mots cibles
        self.static_rules = dict()
        self.linearized_documents_count_step=None
        self.max_documents_count=None
        self.similarity_sequence=[]
        self.similarity_sequence_isLoaded = False
        self.similarity_first_word=None
        self.romeLexic=None
        # self.linearized_tf_idf_index= dict()
        # self.linerization_preparation=False

        if base_dir is None:
            # self.base_dir=os.path.basename(os.getcwd())
            self.base_dir=os.getcwd() + "/"
        else:
            if base_dir[-1]!= "/":
                self.base_dir =base_dir+ "/"

        if file_name is None:
            return

        file_to_open=os.path.join(self.base_dir,file_name)
        with open(file_to_open, newline='\n',encoding="utf-8") as csvfile:
            csv_dict = csv.reader(csvfile, delimiter=',', quotechar='\"')
            for line in csv_dict:
                new_token=asr_token(line[0],load_full_data=True)
                new_token.woaccent=line[1]
                new_token.count=int(line[2])
                new_token.documents_count=int(line[3])
                new_token.idf=float(line[4])
                new_token.length=int(line[5])
                new_token.letters = line[6]
                new_token.letters_number = int(line[7])
                new_token.inFrenchVocab= True if (line[8]=="IFV" or line[8]=="ISV") else False
                # new_token.inSpacyVocab= True if line[8]=="ISV" else False
                if len(line)>9:
                    if line[9]=='None':
                        new_token.attractivity = None
                    else:
                        new_token.attractivity=float(line[9])
                if len(line)>10:
                    if line[10]=='None':
                        new_token.frequency = None
                    else:
                        new_token.frequency= float(line[10])
                if len(line)>11:
                    if line[11]=='None':
                        new_token.precision = None
                    else:
                        new_token.precision= float(line[11])
                if self.similarity_first_word is None:
                    #Garde le premier mot en point d'entrée pour la chaîne de similarités
                    self.similarity_first_word= new_token.text
                self.tokens[new_token.text]=new_token

        try:
            self.static_rules = asr_load_csv_rules(file_name=CTE_FILENAME_STATIC_RULES,base_dir=self.base_dir)
            self.static_rules_loaded = True
        except Exception as error:
            self.static_rules_loaded = False
            func_name=__name__+'.'+'__init__'
            error_msg= "{0}: Le chargement de static_rules a échoué: {1}".format(func_name,error)
            asr_logger.warning("{0}: Le chargement de static_rules a échoué: {1}".format(func_name,error))
            asr_logger.warning(("ATTENTION - Le dictionnaire chargé aura ses static_rules vides !"))
            self.static_rules = dict()


        if load_dynamic_rules:
            self.dynamic_rules = asr_load_csv_rules(base_dir=self.base_dir,file_name=CTE_FILENAME_DYNAMIC_RULES)
            self.dynamic_rules_loaded = True
        else:
            return

    def __repr__(self):
        return repr([lemma for lemma in self.tokens.keys()])

    def __iter__(self):
        self.index=len(self.tokens)
        return iter(self.tokens)

    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.dictionary[self.index]

    def EXISTS(self,lemma_text):
        if lemma_text in self.tokens.keys():
            return True
        else:
            return False

    def FIND(self,word):
        if word in self.tokens.keys():
            return self.tokens[word]
        else:
            return None

    def SAVE_TO_FILE(self,file_name:chr,base_dir:chr=None):
        if base_dir:
            file_to_open = base_dir + file_name
        else:
            file_to_open = self.base_dir + file_name
        with open(file_to_open,"w",encoding="utf_8") as opened_file:
            values=[lemma for lemma in self.tokens.values()]
            values.sort(key=attrgetter('count'),reverse=True)
            for token in values:
                idf=str(token.idf)
                if token.frequency is None:
                    frequency='None'
                else:
                    frequency = str(token.frequency)
                    frequency=frequency[0:8]
                # if token.woaccent!='':
                #     token.letters="".join(set(token.woaccent))
                inFrenchVocab="IFV" if token.inFrenchVocab else "OFV"
                line="\""+token.text+"\","+"\""+token.woaccent+"\","+ str(token.count)+","+str(token.documents_count)+"," \
                     + idf[0:8]+","+str(token.length)+","+"\""+str(token.letters)+"\","+str(token.letters_number)+"," \
                     + inFrenchVocab + "," + str(token.attractivity) + "," + frequency + "," + str(token.precision) + "\n"
                opened_file.write(line)
            opened_file.close()


    def BUILD_IDF(self,documents_number):
        for token in self.tokens.values():
            token.idf = log (documents_number/token.documents_count)

    def BUILD_SIMILARITY_SEQUENCE(self, gensimModel):
        if self.similarity_first_word is None:
            return False
        size = len(gensimModel.wv.key_to_index)
        self.similarity_sequence=[self.similarity_first_word]
        sequence_set= set(self.similarity_sequence)
        word=self.similarity_first_word
        while len(self.similarity_sequence)<size:
            topn = max(int(len(self.similarity_sequence)/10),10)
            candidates = [ word for word,score in gensimModel.wv.most_similar(word,topn=topn)
                           if word not in sequence_set]
            if len(candidates)==0:
                topn = int(len(self.similarity_sequence) / 2)
                candidates = [word for word, score in gensimModel.wv.most_similar(word, topn=topn)
                              if word not in sequence_set]
                if len(candidates) == 0:
                    topn = len(self.similarity_sequence)
                    candidates = [word for word, score in gensimModel.wv.most_similar(word, topn=topn)
                                  if word not in sequence_set]
                if len(candidates) == 0:
                    print("BUG")
                    return False
            next_word = candidates[0]
            self.similarity_sequence.append(next_word)
            sequence_set.add(next_word)
            index=len(sequence_set)
            word=next_word
            if index==100000 or index==200000 or index==400000 or index==600000:
                print(index)
        return True

    def SAVE_SIMILARITY_SEQUENCE(self,file_name:str,base_dir:str=None):
        if base_dir:
            file_to_open = base_dir + file_name
        else:
            file_to_open = self.base_dir + file_name
        try:
            ligne=self.similarity_sequence.__str__()
            # asr_save_doc(file_to_open,[ligne])
            asr_save_doc(document=[ligne],file_name=file_to_open)
            return True
        except:
            print_log("ERROR: could not save dictionary similarity sequence to file")
            return False

    def LOAD_SIMILARITY_SEQUENCE(self,file_name):
        file_to_open = self.base_dir + file_name
        try:
            ligne = asr_load_doc(file_to_open)
            self.similarity_sequence=eval(ligne[0])
            if isinstance(self.similarity_sequence,list) and len(self.similarity_sequence)>0:
                self.similarity_sequence_isLoaded = True
                return True
            else:
                print_log("ERROR: could not load dictionary similarity sequence from file 1")
                self.similarity_sequence_isLoaded = False
                return False
        except:
            print_log("ERROR: could not load dictionary similarity sequence from file 2")
            self.similarity_sequence_isLoaded = False
            return False


    def BUILD_ATTRACTIVITY(self,gensim_model,default_similarity_floor=asr_similarityLimit_forAttractivity,max_wordsToScan=1000):
        for token in self.tokens.values():
            if token.text in gensim_model.wv.key_to_index:
                token.COMPUTE_ATTRACTIVITY(gensim_model,
                                           default_similarity_floor=default_similarity_floor,
                                           max_wordsToScan=max_wordsToScan)

    def BUILD_PRECISION(self,gensim_model):
        # precision_dict=dict()
        #LA PRECISION SE CALCULE D'UNE FAçON RELATIVE LINEARISEE
        precision_values=[]
        for token in self.tokens.values():
            if token.text in gensim_model.wv.key_to_index:
                value = linalg.norm(gensim_model.wv[token.text]) / token.count
                precision_values.append([token.text,value])
        precision_values.sort(key=itemgetter(1),reverse=False)
        length=len(precision_values)
        zoom = 1 / length
        for index, [ word,lost ] in enumerate(precision_values):
            self.tokens[word].precision=zoom*index #on ne tien pas compte de la norme en elle-même mais de sa position dans le classement

    def FIND_NEIGHBOURHOOD(self,word,neighboorMinWordCount=10):
        length=len(word)
        letters=set(word)

        echantillon=[token for token in self.tokens.values()
                     if (length<=token.length+1 and length>=token.length-1 and token.count>3)
                     and (set(token.letters).issubset(letters) or letters.issubset(set(token.letters)))]

        echantillon.extend([token for token in self.static_rules_tokens.values()
                     if (length<=token.length+1 and length>=token.length-1 and token.count>3)
                     and (set(token.letters).issubset(letters) or letters.issubset(set(token.letters)))])

        echantillon.extend([token for token in self.dynamic_rules_tokens.values()
                     if (length<=token.length+1 and length>=token.length-1 and token.count>3)
                     and (set(token.letters).issubset(letters) or letters.issubset(set(token.letters)))])

        echantillon=[ [token.text, SequenceMatcher(None, word, token.text).ratio()] for token in echantillon
                      if token.count>=neighboorMinWordCount]
        echantillon=sorted(echantillon,key=itemgetter(1),reverse=True)
        echantillon= [ mot for mot,score in echantillon if score>=0.75]
        return echantillon

    def LOAD_COMMON_USE_CLASSES(self,quotechar='%'):
        self.commonUsesRules_map=dict()
        self.commonUsesRules_classes = dict()
        file_to_open = self.base_dir + "commonUsesRules_map.csv"
        with open(file_to_open, newline='\n', encoding="utf-8") as csvfile:
            csv_dict = csv.reader(csvfile, delimiter='|', quotechar=quotechar)
            for line in csv_dict:
                initial=line[0]
                target_set=eval(line[1])
                self.commonUsesRules_map[initial]=target_set
        file_to_open = self.base_dir + "commonUsesRules_classes.csv"
        with open(file_to_open, newline='\n', encoding="utf-8") as csvfile:
            csv_dict = csv.reader(csvfile, delimiter='|', quotechar=quotechar)
            for line in csv_dict:
                target=line[0]
                classes=eval(line[1])
                self.commonUsesRules_classes[target]=classes
        self.commonUsesRules_loaded = True

    def SAVE_COMMON_USES_CLASSES(self,quotechar='%'):
        if self.commonUsesRules_loaded==False:
            print("Won't save common uses classes rules: no rule to save, first load or create.")
            return
        pairs_to_remove=[]
        for initial in self.commonUsesRules_map.keys():
            for target in self.commonUsesRules_map[initial]:
                if target not in self.commonUsesRules_classes.keys():
                    # si la target n'a pas de classe (caculée vide), supprime la
                    pairs_to_remove.append([initial,target])

        for initial,target in pairs_to_remove:
            self.commonUsesRules_map[initial].remove(target)
            if len(self.commonUsesRules_map[initial]) == 0:
                self.commonUsesRules_map.pop(initial)  # si certains sets finissent vides: supprime les

        map_str = [quotechar + initial + quotechar+"|"+quotechar + str(self.commonUsesRules_map[initial]) + quotechar+"\n" for initial in self.commonUsesRules_map.keys()]
        map_str.sort()
        file_to_open = self.base_dir + "commonUsesRules_map.csv"
        with open(file_to_open, "w", encoding="utf_8") as file:
            for line in map_str:
                file.write(line)

        classes_str = [quotechar + target + quotechar+"|"+quotechar + str(self.commonUsesRules_classes[target]) + quotechar+"\n" for target in self.commonUsesRules_classes.keys()]
        classes_str.sort()
        file_to_open = self.base_dir + "commonUsesRules_classes.csv"
        with open(file_to_open, "w", encoding="utf_8") as file:
            for line in classes_str:
                file.write(line)
