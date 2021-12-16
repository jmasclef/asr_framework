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

import json
import collections
from operator import itemgetter
from difflib import SequenceMatcher
import numpy
import pandas
import gensim

from .asr_constantes import *
from .asr_dictionary import asr_dictionary
from .asr_regex_filters import *
from .asr_tokenisation import asr_filter_stopwords, asr_tokenize_string,  asr_strip_accents
from .asr_rules_dict import asr_apply_rules_dict, asr_trackRuleTarget
asr_similarityLimit_forAggregation=0.5  #score minimum d'aggrégation thématique entre mots pour qu'ils soient associés à un même thème


class asr_topic():
    def __init__(self,words_list=None, useJSONDump=None):
        if useJSONDump:
            self.LOADS(input=useJSONDump, mode='JSONDump')
        else:
            if words_list:
                self.content= sorted (words_list.copy())
                self.content_set = sorted(list(set(self.content)))
                self.length=len(self.content)
                self.weight=0
                # # prend le centre du groupe
                # centre = self.model.wv.most_similar_cosmul(positive=self.content)[0][0]
                # # retire l'élément du groupe le plus proche
                # self.title = self.model.wv.most_similar_to_given(centre, self.content)
            else:
                self.content = []
                self.content_set = {}
                self.title = ''
                self.length = 0
                self.weight = 0

    def __new__(cls):
        return object.__new__(cls)

    def to_dict(self):
        sortie=dict()
        sortie['title']=self.title
        sortie['length']=self.length
        sortie['content']=self.content
        sortie['content_set'] = self.content_set
        sortie['weight']=round(self.weight,CTE_ROUND_SAAS_SERVER_DECIMAL_NUMBERS)
        # return sortie.__repr__()
        return sortie
    def __repr__(self):
        sortie=json.loads('{}')
        sortie['title']=self.title
        sortie['length']=self.length
        sortie['content']=self.content
        sortie['content_set'] = self.content_set
        sortie['weight']=round(self.weight,CTE_ROUND_SAAS_SERVER_DECIMAL_NUMBERS)
        # return sortie.__repr__()
        return json.dumps(sortie, ensure_ascii=False, sort_keys=True)

    def DUMPS(self,mode='JSONDump'):
        if mode=='JSONDump':
            return self.__repr__()

    def LOADS(self,input,mode='JSONDump'):
        if mode=='JSONDump':
            try:
                dump=json.loads(input)
                self.title = dump['title']
                self.length= dump['length']
                self.content = dump['content']
                self.content_set = dump['content_set']
                self.weight = dump['weight']
                return True
            except:
                raise NameError('Unable to load JSON dump')
                return False
        else:
            raise NameError('Unknown dump mode')
            return False

    def COMPUTE_MEAN_VECTOR(self, gensim_model):
        v = [gensim_model.wv.get_vector(word) for word in self.content]
        if len(v) == 0:
            return None
        else:
            return numpy.array(v).mean(axis=0)

class asr_sentence():
    def __init__(self,sentence:str,dictionary:asr_dictionary,model:gensim.models.Word2Vec):
        # le test suivant a été repoussé à la fonction FILTER
        # if dictionary is not None and dictionary.dynamic_rules_loaded==False:
        #     raise NameError('Dictionary must have loaded its dynamic rules')
        self.dictionary=dictionary
        self.model=model
        if isinstance(sentence,list):
            self.original =sentence
        else:
            if sentence is None:
                self.original = None
            else:
                self.original=str(sentence).lower()
                # self.original=str(sentence).lower().split()
        self.justCleanAndStopwords = []
        self.inTheVocabulary=[]
        self.outOfVocabulary=[]
        self.OOV_suggestCorrections=dict()
        self.wasFiltered=False
        self.withDeclinaisons=[]
        self.wasPreparedToMigrate=False
        self.allCombinations=[]
        self.allCombinationsDone=False
        self.lastMigration=[]
        self.hasMigrated=False
        self.topics=[]
        self.topics_globalLength=0
        self.sumUpWord=None
        self.precision=None
        self.precision_libelle= None
        self.topicsConvergence=None
        self.topicsConvergence_libelle = None
        self.sortedConvergenceWords=[]
        self.sortedConvergenceWords_excluded=[]
        self.tf_idf=None
        # self.topicsConvergenceWordsAVG=None
        # self.bullseyeVector=None


    def __repr__(self):
        return str(self.original)

    def COMPUTE_TF_IDF(self):
        if not self.wasFiltered:
            self.FILTER()

        self.tf_idf=dict()
        local_counter=collections.Counter(self.inTheVocabulary)

        for word in set(self.inTheVocabulary):
            self.tf_idf[word]=(1+log(local_counter[word]))*self.dictionary.tokens[word].idf

        if len(self.tf_idf.keys())>0:
            return True
        else:
            return False

    def COMPUTE_TOPICS_WEIGTHS(self,use_tfIdf=True):
        if use_tfIdf:
            if self.tf_idf is None:
                self.COMPUTE_TF_IDF()
            if len(self.tf_idf.keys())==0:
                return False
            else:
                for topic in self.topics:
                    topic.weight = sum([self.tf_idf[word] for word in topic.content])
                totalWeight = sum([topic.weight for topic in self.topics])
                for topic in self.topics:
                    topic.weight = topic.weight / totalWeight
                return True
        else:
            for topic in self.topics:
                topic.weight = topic.length / self.topics.topics_globalLength
        return True


    def COMPUTE_MEAN_VECTOR(self, minPrecisionLimit=None, useDeclinaisons=False):
        if useDeclinaisons:
            # if not self.wasPreparedToMigrate:
            #     self.PREPARE_TO_MIGRATE()
            v=[]
            for occurence in self.withDeclinaisons:
                if isinstance(occurence,list):
                    declinaison=numpy.array([self.model.wv.get_vector(word) for word in occurence]).mean(axis=0)
                    v.append(declinaison)
                else:
                    v.append(self.model.wv.get_vector(occurence))
        else:
            # if not self.wasFiltered:
            #     self.FILTER()
            if minPrecisionLimit is None:
                v = [self.model.wv.get_vector(word) for word in self.inTheVocabulary]
            else:
                v = [self.model.wv.get_vector(word) for word in self.inTheVocabulary
                     if self.dictionary.tokens[word].precision >= minPrecisionLimit ]
            # return gensim.matutils.unitvec(numpy.array(v).mean(axis=0))
        if len(v)==0:
            return None
        else:
            return numpy.array(v).mean(axis=0)

    def COMPUTE_PRECISION(self):
        #la précision globale d'une phrase est la moyenne des précisions des mots qui la composent
        t=[ self.dictionary.tokens[word].precision  for word in self.inTheVocabulary
            if self.dictionary.tokens[word].precision is not None]
        if len(t)>0:
            self.precision= sum(t)/len(t)
            if self.precision < 0.05:
                self.precision_libelle = "très faible"
            elif self.precision < 0.1:
                self.precision_libelle = "faible"
            elif self.precision < 0.3:
                self.precision_libelle = "moyenne"
            elif self.precision < 0.5:
                self.precision_libelle = "élevée"
            else:
                self.precision_libelle = "très élevée"
            self.precision_libelle=self.precision_libelle.upper()
        else:
            self.precision = 0
            self.precision_libelle = "N/A"
        del t
        return self.precision

    def COMPUTE_TOPICS_CONVERGENCE(self,filtering=True, replaceITV=False,effectifMin=0.5, relativeMinPrecision=0.1):
        #la convergence thématique est la mesure de la polarité d'une phrase normalisée
        #plus la phrase normalisée est polarisée plus la résultante est longue
        #la valeur est elle-même normalisée

        self.topicsConvergence_libelle = None
        self.topicsConvergence = None
        if len(self.inTheVocabulary)==0:
            self.topicsConvergence = 0
            self.topicsConvergence_libelle = "N/A"
            return None
        minPrecision = self.COMPUTE_PRECISION() * relativeMinPrecision
        meanVector = self.COMPUTE_MEAN_VECTOR(minPrecisionLimit=minPrecision)
        if meanVector is None:
            self.topicsConvergence = 0
            self.topicsConvergence_libelle = "N/A"
            return None

        bullEye_vector= gensim.matutils.unitvec( meanVector) #produit scalaire => normaliser
        tab = []
        simTOT = 0
        for word in set(self.inTheVocabulary):
            # cosine similarity est le produit scalaire de deux vecteurs normalisés
            sim = numpy.dot(bullEye_vector, gensim.matutils.unitvec(self.model.wv.word_vec(word)))
            simTOT += sim
            tab.append( [word, sim ] )
        tab.sort(key=itemgetter(1),reverse=True)
        self.topicsConvergence = simTOT / len(tab)
        if self.topicsConvergence < 0.4:
            self.topicsConvergence_libelle = "très faible"
            simLimit = 0.4
        elif self.topicsConvergence < 0.45:
            self.topicsConvergence_libelle = "faible"
            simLimit = self.topicsConvergence
        elif self.topicsConvergence < 0.5:
            self.topicsConvergence_libelle = "moyenne"
            simLimit = self.topicsConvergence
        elif self.topicsConvergence < 0.6:
            self.topicsConvergence_libelle = "élevée"
            simLimit = 0.5
        else:
            self.topicsConvergence_libelle = "très élevée"
            simLimit = 0.5

        self.topicsConvergence_libelle = self.topicsConvergence_libelle.upper()
        if filtering:

            self.sortedConvergenceWords = [ word for [ word, score ] in tab if score >= simLimit]

            self.sortedConvergenceWords_excluded = [ word for word in self.inTheVocabulary
                                                    if word not in self.sortedConvergenceWords]
            if replaceITV:
                self.inTheVocabulary=self.sortedConvergenceWords
        else:
            self.sortedConvergenceWords = [ word for [ word, lost ] in tab]
            self.sortedConvergenceWords_excluded = []
        return self.topicsConvergence

    def BUILD_SUMUPWORD(self):
        if len(self.inTheVocabulary)==0:
            self.sumUpWord=  None
        else:
            self.sumUpWord = self.model.wv.most_similar(positive=self.inTheVocabulary,topn=1)[0][0]

    def PREDICT(self,context_window=5,last_words_window=5,topn=10):
        if len(self.inTheVocabulary)==0:
            return None
        else:
            self.COMPUTE_TOPICS_CONVERGENCE()
            context_words = self.sortedConvergenceWords[0:context_window]
            #ICI
            scan_window= self.inTheVocabulary[-last_words_window:] + context_words
            #j'ai essayé d'enlever les doublons avec un set() mais les résultats sont plus répétitifs et moins poussés, comme ci ajouter les vecteurs allait chercher des suggestions plus loin
            candidates = self.model.wv.most_similar(positive=scan_window,topn=100)
            candidates_w_score = []
            itv_set=set(self.inTheVocabulary)
            for (word, score) in candidates:
                token=self.dictionary.FIND(word)
                if token.documents_count<3:
                    continue
                if token.IS_LETTERS_DOUBLED():
                    continue
                if score<0.5:
                    continue
                # attractivity=token.COMPUTE_ATTRACTIVITY(gensim_model=self.model)
                if word not in itv_set:
                    try:
                        candidates_w_score.append((word, score/token.precision/token.idf))
                    except:
                        continue #si precision ou idf is none ou 0

            candidates_w_score.sort(key=itemgetter(1),reverse=True)
            next_words = [ word for (word,_) in candidates_w_score[:topn] ]
            # return next_words
            return candidates_w_score[:topn]

    def COMPLETE(self,new_words=1,context_window=5,last_words_window=5):
        new_words_list=[]
        while new_words>0:
            next_words = self.PREDICT(context_window=context_window,last_words_window=last_words_window)
            if next_words is None:
                break
            else:
                self.original.append(next_words[0])
                self.inTheVocabulary.append(next_words[0])
                new_words_list.append(next_words[0])
                new_words-=1
        return new_words_list
                #ICI canadidates_w_p
    def LOAD_TOPICS_FROM_DICT(self,dict_topics):
        #Récupère une liste de liste
        #construit chaque topic avec son titre
        #calcule les poids

        self.topics_globalLength=0
        self.topics=[]
        for topic in dict_topics:
            nTopic = asr_topic()
            nTopic.content=topic['content']
            nTopic.content_set = topic['content_set']
            nTopic.weight = topic['weight']
            nTopic.length = topic['length']
            nTopic.title = topic['title']
            self.topics.append(nTopic)
            self.topics_globalLength += nTopic.length


    def LOAD_TOPICS_FROM_LIST(self,liste):
        #Récupère une liste de liste
        #construit chaque topic avec son titre
        #calcule les poids
        if isinstance(liste,list):
            liste_de_liste=liste
        else:
            liste_de_liste=eval(liste)    #cas courant => valeurs téléchargées de la BDD donc '[[...],[...]]'

        self.topics_globalLength=0
        self.topics=[]
        for index,liste in enumerate(liste_de_liste):
            nTopic = asr_topic(words_list=liste)
            nTopic.title= "Imp"+str(index)
            self.topics.append(nTopic)
            self.topics_globalLength += nTopic.length
        self.COMPUTE_TOPICS_WEIGTHS()

    def EXTRACT_TOPICS_AS_LIST(self):
        result=[]
        for topic in self.topics:
            result.append(topic.content)

        return result

    def EXTRACT_TOPICS_AS_JSON_LIST(self):
        return [topic.DUMPS() for topic in self.topics]


    def SERIALIZE_DECLINAISONS(self):
        result=[]
        for occurence in self.withDeclinaisons:
            if isinstance(occurence,list):
                result.extend(occurence)
            else:
                result.append(occurence)
        return result


    def FILTER(self,split_in_sections_with_markups=False,dealWithOOV=True,suggestCorrections=False, justCleanAndStopwords=False):

        def asr_filter_sentence(sentence_to_analyse: str, final_gensim_model, dictionary, filter_section_markups=True,
                               split_in_sections_with_markups=False, dealWithOOV=True, justCleanAndStopwords=False):
            # KEY FUNCTION => TRANSFORM ANY TEXT WITH RESPECT TO THE MODEL

            # step_TOKENIZE
            tokenized_sentence = asr_tokenize_string(input_string=sentence_to_analyse,split_in_sections_with_markups=split_in_sections_with_markups)

            # step_FILTER_STOPWORDS
            filtered_tokenized_sentence = asr_filter_stopwords(tokenized_sentence, filter_section_markups=(not split_in_sections_with_markups))

            # sentence_to_analyse = " ".join(sentence_to_analyse)
            # # correct lost .
            # sentence_to_analyse = sentence_to_analyse.replace('.', ' ')

            if justCleanAndStopwords:
                # return (sentence_to_analyse.split(), [])
                return (filtered_tokenized_sentence, [])

            # step APPLY_STATIC_RULES
            filtered_tokenized_sentence = asr_apply_rules_dict(line_of_words_list=filtered_tokenized_sentence,
                                                       rules_dict=dictionary.static_rules)
            # step APPLY_DYNAMIC_RULES
            filtered_tokenized_sentence = asr_apply_rules_dict(line_of_words_list=filtered_tokenized_sentence,
                                                       rules_dict=dictionary.dynamic_rules)

            missing_words_oovmodel = list(set([word for word in filtered_tokenized_sentence
                                               if word not in final_gensim_model.wv
                                               # if word not in final_gensim_model.wv
                                               and word not in FRENCH_STOPWORDS_LIST_W_MARKUPS]))

            if dealWithOOV:
                sentence_to_analyse, missing_words_oovmodel = asr_dealWithOOV(filtered_tokenized_sentence,
                                                                             missing_words_oovmodel,
                                                                             final_gensim_model, dictionary)

            if not split_in_sections_with_markups:
                new_sentence = [word for word in filtered_tokenized_sentence if word in final_gensim_model.wv]
            else:
                new_sentence = [word for word in filtered_tokenized_sentence if
                                ((word in final_gensim_model.wv) or (word in RESUME_SECTIONS_MARKUPS))]

            # new_sentence = " ".join(new_sentence)
            return (new_sentence, missing_words_oovmodel)

        if justCleanAndStopwords:
            (self.justCleanAndStopwords, self.outOfVocabulary) = asr_filter_sentence(self.original, self.model,
                                        self.dictionary, filter_section_markups=filterSectionsMarkups,
                                        dealWithOOV=dealWithOOV, justCleanAndStopwords=justCleanAndStopwords)
            return False
        else:
            if self.dictionary is not None and self.dictionary.dynamic_rules_loaded == False:
                raise NameError('Dictionary must have loaded its dynamic rules')
            (self.inTheVocabulary, self.outOfVocabulary) = asr_filter_sentence(self.original, self.model, self.dictionary,
                                        split_in_sections_with_markups=split_in_sections_with_markups,
                                        dealWithOOV=dealWithOOV,justCleanAndStopwords=justCleanAndStopwords)
            if suggestCorrections:
                self.SUGGEST_OOV_CORRECTIONS()
            self.wasFiltered = True
            return self.wasFiltered

    def PREPARE_TO_MIGRATE(self,filterSectionsMarkups=True,dealWithOOV=True):
        self.hasMigrated = False
        if self.dictionary.commonUsesRules_loaded==False:
            raise NameError('Dictionary must have loaded its common uses rules to migrate sentences')
        if self.wasFiltered==False:
            self.FILTER(filterSectionsMarkups=filterSectionsMarkups,dealWithOOV=dealWithOOV)
        self.withDeclinaisons=asr_migrateSentencePreparation(self.inTheVocabulary,self.dictionary,self.model)
        if len(self.withDeclinaisons)!=0:
            self.wasPreparedToMigrate=True
        else:
            self.wasPreparedToMigrate=False

        return self.wasPreparedToMigrate

    def MIGRATE_TO(self,other_sentence, fast_and_approximate_migration=False):
        if not self.hasMigrated:
            if other_sentence.wasFiltered==False:
                raise NameError('Request to migrate to other sentence that was NOT filtered ')
            if not self.wasPreparedToMigrate:
                self.PREPARE_TO_MIGRATE()
            self.lastMigration = asr_migrateSentence(self, other_sentence, self.dictionary,
                                                         self.model,fast_and_approximate_migration=fast_and_approximate_migration)
            if len(self.lastMigration)!=0:
                self.hasMigrated=True
            else:
                self.hasMigrated = True

            return self.hasMigrated

    def SUGGEST_OOV_CORRECTIONS(self, filter_set:set=None):
        self.OOV_suggestCorrections = dict()
        for oov_word in self.outOfVocabulary:
            if filter_set is None:
                self.OOV_suggestCorrections[oov_word]= self.dictionary.FIND_NEIGHBOURHOOD(oov_word)
            else:
                self.OOV_suggestCorrections[oov_word]= \
                    [ word for word in self.dictionary.FIND_NEIGHBOURHOOD(oov_word) if word in filter_set ]

    def BUILD_TOPICS(self, score_limit_aggregation=asr_similarityLimit_forAggregation, avoidSingles=False,
                     topic_min_size=3, topic_min_number=1, use_tf_idf=True, min_tf_idf=1,useSimilaritySequence=True,integersAsTitles=True, useParentTopics=None, dispatchTopics=False):
        #avoidSingles définit si les groupes peuvent etre constitués d'un seul mot ex {'gestion','gestion','gestion'}
        #mettre topic_min_size à 2 est trop ouvert sur les bigrams: ['hiérarchiquement', 'rattaché'], ['interlocuteur', 'privilégié']...
        if not self.wasFiltered:
            self.FILTER()
        if self.tf_idf is None:
            self.COMPUTE_TF_IDF()

        words_list = self.inTheVocabulary.copy()
        if useParentTopics:
            if isinstance(useParentTopics,asr_sentence):
                step = set(self.inTheVocabulary)
                parentTopics=useParentTopics.EXTRACT_TOPICS_AS_LIST()
                groupes = [[word for word in parentGroup if word in step] for parentGroup in parentTopics]
                groupes = [groupe for groupe in groupes if len(groupe) > 0]
            else:
                raise NameError('useParentTopics must be MPearl asr_sentence objet')
                return False

        else:
            if useSimilaritySequence and not self.dictionary.similarity_sequence_isLoaded:
                print_log("Erreur: la branche similarity sequence n'est pas chargée")
                raise "Erreur: la branche similarity sequence n'est pas chargée"
            if useSimilaritySequence:
                #met dans l'ordre du tableau similarity_sequence
                step = [word for word in self.dictionary.similarity_sequence if word in set(words_list) ]
                step = [[word]*self.inTheVocabulary.count(word) for word in step ]
                words_list=[]
                for t in step:
                    words_list.extend(t)
            else:
                words_list = [word for word in self.inTheVocabulary if self.dictionary.tokens[word].count > 1 ]

            if len(words_list) <= 1:
                self.topics= []
                return

            first_word = words_list[0]
            words_list.remove(first_word)

            groupes = []
            groupe = [first_word]
            word = first_word

            while len(words_list) > 0:
                # réordonne la liste par similarité un-à-un
                if useSimilaritySequence:
                    next_word=words_list[0]
                else:
                    next_word = self.model.wv.most_similar_to_given(word, words_list)
                words_list.remove(next_word)
                next_similarity = self.model.wv.n_similarity(groupe, [next_word])
                if next_similarity < score_limit_aggregation:
                    # loin de son prédecesseur, ferme et enregisitre le groupe précédent, créé un nouveau groupe
                    if len(groupe)>=topic_min_size:
                        #taille suffisante => garde le groupe
                        groupes.append(groupe)
                    else:
                        #taille insuffisante => si un mot à bon tfIdf garde qd meme
                        if use_tf_idf:
                            for word in groupe:
                                if self.tf_idf[word] > min_tf_idf:
                                    groupes.append(groupe)
                                    break
                    groupe = [next_word]
                else:
                    groupe.append(next_word)

                word = next_word

            if len(groupe)>=topic_min_size:
                groupes.append(groupe)
            else:
                if use_tf_idf:
                    for word in groupe:
                        if self.tf_idf[word]>min_tf_idf:
                            groupes.append(groupe)
                            break

        self.topics=[]
        if len(groupes) == 0:
            return False

        # trouve une étiquette aux groupes
        global_length=0
        global_weight=0
        for index,groupe in enumerate(groupes):
            if avoidSingles and (len(set(groupe))==1):
                continue
            # if len(groupe)<topic_min_size:
            #     continue

            if integersAsTitles:
                titre="Auto"+str(index)
            else:
                #prend le centre du groupe
                centre = self.model.wv.most_similar_cosmul(positive=groupe)[0][0]
                #retire l'élément du groupe le plus proche
                titre = self.model.wv.most_similar_to_given(centre,groupe)
                titre = titre.capitalize()
            topic = asr_topic(sorted(groupe))
            topic.title = titre
            if use_tf_idf:
                topic.weight = sum([self.tf_idf[word] for word in groupe]) #* topic.length
            else:
                topic.weight = topic.length

            global_weight += topic.weight
            global_length += len(groupe)
            self.topics.append(topic)

        if len(self.topics) < topic_min_number:
            self.topics=[]
            return False

        if global_weight>0:
            for topic in self.topics:
                topic.weight = topic.weight / global_weight
            # topic.weight = topic.length / global_length

        self.topics_globalLength=global_length


        self.topics.sort(key=attrgetter('length'),reverse=True)

        return True

    def TRANSFORM(self,filter_with_threshold=True,suggestCorrections=False,replaceWithCorrections=False):
        local_suggestCorrections=suggestCorrections or replaceWithCorrections
        self.FILTER(suggestCorrections=local_suggestCorrections)
        if replaceWithCorrections and len(self.OOV_suggestCorrections.keys())>0:
            original=" ".join(self.original)
            for word in self.OOV_suggestCorrections.keys():
                original=original.replace(word,self.OOV_suggestCorrections[word][0])
            self.original=original.split()
            self.wasFiltered=False
            self.wasPreparedToMigrate=False
            self.FILTER()
        self.BUILD_TOPICS(avoidSingles=False,integersAsTitles=True)
        if filter_with_threshold and (self.inTheVocabulary.__len__() >= SENTENCE_FILTER_THRESHOLD):
            self.COMPUTE_TOPICS_CONVERGENCE(filtering=True, replaceITV=True)
        else:
            self.COMPUTE_TOPICS_CONVERGENCE()
        self.BUILD_SUMUPWORD()
        self.PREPARE_TO_MIGRATE()

def asr_dealWithOOV(filtered_sentence:list,oov_sentence:list,final_gensim_model, dictionary,filter_section_markups=True):
    """
    :param filtered_sentence: récupère une phrase ne contenant plus que les mots dans le modèle
    :param oov_sentence: récupère les mots OOV de la phrase précédente
    :param filter_section_markups: booleen supprime les markups de sections
    :return: reprend chaque mot composé de la liste OOV, le split et  applique les règles statics et dynamiques
    """
    oov_sentence_list=oov_sentence
    oov_corrections=[]
    oov_to_remove=[]
    for oov_word in oov_sentence_list:
        # le '/' est remplacé par '-' dans cleanTokenize
        if "-" not in oov_word and "&" not in oov_word:
            continue
        if len(oov_word)<=MIN_WORD_LENGTH:  #si la taille avec un "-" ou un "&" égale la taille limite =>OUT
            continue
        new_word = oov_word.replace('&', '-')
        new_word = asr_trackRuleTarget(dictionary.static_rules,new_word)
        new_word = asr_trackRuleTarget(dictionary.dynamic_rules,new_word)

        #step 1 on vérifie qu'en remplaçant le & par le - on trouve pas un mot deja connu
        if new_word in final_gensim_model.wv:
            oov_to_remove.append(oov_word)
            oov_corrections.append([oov_word, new_word])
        #sinon, step2 on split le mot et on regarde si chacun est connu
        else:
            new_word = new_word.replace('-', ' ')  # le '/' est remplacé par '-' dans cleanTokenize
            splitted_new_word=new_word.split()
            if len(splitted_new_word)==0:
                continue

            splitted_new_word = [asr_trackRuleTarget(dictionary.static_rules, word) for word in splitted_new_word]
            splitted_new_word = [asr_trackRuleTarget(dictionary.dynamic_rules,word) for word in splitted_new_word]

            areKnown=[word in final_gensim_model.wv for word in splitted_new_word]
            if all(areKnown):
                oov_to_remove.append(oov_word)
                oov_corrections.append([oov_word," ".join(splitted_new_word)])

    filtered_sentence=" ".join(filtered_sentence)
    for word,new_word in oov_corrections:
        filtered_sentence=filtered_sentence.replace(word,new_word)

    filtered_sentence=filtered_sentence.split()

    missing_words_oovmodel = [word for word in filtered_sentence
                              if word not in final_gensim_model.wv
                              if word not in oov_to_remove
                              and word not in FRENCH_STOPWORDS_LIST_W_MARKUPS]
    missing_words_oovmodel = list(set(missing_words_oovmodel))

    if filter_section_markups:
        new_sentence = [word for word in filtered_sentence if word in final_gensim_model.wv]
    else:
        new_sentence = [word for word in filtered_sentence if
                        ((word in final_gensim_model.wv) or (word in RESUME_SECTIONS_MARKUPS))]

    # new_sentence = " ".join(new_sentence)
    return (new_sentence,missing_words_oovmodel)

def asr_classeUsage(target,fmodel,dictionary,score_limit_aggregation=asr_similarityLimit_forAggregation,min_group_size=3,similarity_window_width=0.2, break_wo_polysemy=False, logging=False, max_words_scan=200):
    words_list=[]
    mots=target
    if not isinstance(mots,list):
        mots=mots.split()   #trasnforme en tableau
    for mot in mots:
        lscore = 1
        minwords = 40
        sim_array = fmodel.wv.most_similar(mot,topn=1)
        score_limit_stopwords = sim_array[0][1] - similarity_window_width #part du plus proche et sur une fenêtre de similarité
        while lscore > score_limit_stopwords and minwords<max_words_scan: #rentre des mots tant qu'on est dans la fenêtre de similarité
            sim_array = fmodel.wv.most_similar(mot, topn=minwords)
            lword, lscore = sim_array[-1]
            minwords += 10

        words_list += [word for word, score in sim_array if score >= score_limit_stopwords and word not in words_list] #supprime ceux qui sont en dehors de la fenêtre de similarité

    #LOG
    if logging:
        print("STEP 1 - Extraction des mots les plus similaires")
        print(len(words_list),words_list)
    #a créé la liste des most_similaires
    if len(words_list)==0:
        return [], target

    #prend le mot le plus similaire à l'entrée
    if len(mots)==1:
        first_word=words_list[0]
    else:
        #cette étape a n interet possible nul car les groupe sont agrégés ensuite, peu importe le premier pris
        sims=[ [word, fmodel.wv.n_similarity([word], mots)] for word in words_list]
        sims.sort(key=itemgetter(1),reverse=True)
        first_word=sims[0][0]

    words_list.remove(first_word)
    groupes=[]
    groupe=[first_word]
    word=first_word
    #ici trie de la liste en cherchant le plus proche suivant, selon la valeur de la sim, agrège ou crée un nouveau groupe
    while len(words_list)>0:
        #reordonne la liste par similarité un-à-un
        next_word=fmodel.wv.most_similar_to_given(word,words_list)
        if dictionary.FIND(word) is None:
            print(word)
        if dictionary.FIND(word).count>1:
            next_similarity = fmodel.wv.n_similarity(groupe, [next_word])
            if next_similarity<score_limit_aggregation:
                #loin de son prédecesseur, ferme et enregisitre le groupe précédent, créé un nouveau groupe
                groupes.append(groupe)
                groupe=[next_word]
            else:
                #proche de son prédécesseur: agrège dans le groupe en cours
                # groupe.append(next_word)
                if len(groupe)==2:
                    groupe[1]=next_word
                else:
                    groupe.append(next_word)
        word=next_word
        words_list.remove(next_word)
    groupes.append(groupe)
    #LOG
    if logging:
        print("STEP 2 - Réagencement des mots par proximité successive avec scission en groupes")
        for groupe in groupes:
            print(len(groupe), groupe)
    #evalue les similarités entre les groupes, selon le score de sim, fusionne les groupes
    new_groupes=[]
    if len(groupes)==0:
        return [], target
    # #ETUDIE L'AGGREGATION DES GROUPES ENTRE EUX
    # while len(groupes)>0:
    #     groupe_repere = groupes[0]
    #     groupes.remove(groupes[0])
    #     groups_to_remove=[]
    #     #COMPARE LE GROUPE A TOUS SES SUCCESSEURS
    #     for groupe in groupes:
    #         sim_score = fmodel.wv.n_similarity(groupe_repere, groupe)
    #         if sim_score >=score_limit_aggregation:
    #             groupe_repere.extend(groupe)
    #             groups_to_remove.append(groupe)
    #     for groupe in groups_to_remove:
    #         groupes.remove(groupe)
    #     new_groupes.append(groupe_repere)
    #
    # groupes=new_groupes.copy()
    # del new_groupes


    # #LOG
    # if logging:
    #     print("STEP 3 - Agrégation de groupes similaires")
    #     for groupe in groupes:
    #         print(len(groupe),groupe)
    #
    # if len(groupes)==0:
    #     return []
    #
    # new_groupes=[]
    # for groupe in groupes:
    #     #reconstitue des groupes non exclusifs
    #     words_list_to_analyze= [ word for word in initial_words_list
    #                              if word not in groupe and dictionary.FIND(word).count > 1]
    #     for word in initial_words_list:
    #         if word not in set(groupe) and dictionary.FIND(word).count > 1:
    #             next_similarity = fmodel.wv.n_similarity(groupe, [word])
    #             if next_similarity > score_limit_aggregation:
    #                 groupe.append(word)
    #     new_groupes.append(groupe)
    # groupes=new_groupes.copy()
    # del new_groupes


    groupes = [groupe for groupe in groupes if len(groupe) >= min_group_size]  # PERTES

    score_min=None
    if break_wo_polysemy:
        #DETECTION DE CONTEXTES ANTONYMES
        groupes_test=groupes.copy()
        polysemy=False
        groupe=groupes_test.pop()
        # groupes_test.remove(groupe)
        score_min=1
        while (len(groupes_test)>0):
            for groupe_to_compare in groupes_test:
                score=fmodel.wv.n_similarity(groupe,groupe_to_compare)
                if score<(1-score_limit_aggregation):
                    polysemy=True
                    if score<score_min:
                        score_min=score
            groupe=groupes_test.pop()
            # groupes_test.remove(groupe)
        if not polysemy:
            return [], target

    #trouve une étiquette aux groupes
    # polysemy_groups=[]
    # for groupe in groupes:
    #     #prend le centre du groupe
    #     centre = fmodel.wv.most_similar(positive=groupe)[0][0]
    #     #retire l'élément du groupe le plus proche
    #     titre = fmodel.wv.most_similar_to_given(centre,groupe)
    #     polysemy_groups.append([titre,groupe])

    return groupes, target

def asr_migrateSentencePreparation(sentence_to_change: list, dictionary: asr_dictionary, model: gensim.models.Word2Vec):
    window_length_step1 = 2
    window_length_step2 = 4
    window_length_step3 = 6
    new_sentence = []
    min_score_to_permit=0.5
    new_words_list = ''
    if dictionary.commonUsesRules_loaded == False:
        print("ERROR: sentence migration request without commonUses loaded !!!")
        return (sentence_to_change)
    for index in range(len(sentence_to_change)):
        word = sentence_to_change[index]
        window = asr_extractBagOfWords(sentence_to_change, index, window_length_step2)
        if len(window) < 2:
            new_sentence.append(word)
            continue
        if word in dictionary.commonUsesRules_map.keys():
            possibilities = dictionary.commonUsesRules_map[word]    #remonte le groupe des alternatives possibles
            declinaisons=[]
            for possibility in possibilities:
                relevantClasses=dictionary.commonUsesRules_classes[possibility]
                for classe in relevantClasses:
                    # window_sumUp=model.wv.most_similar(positive=window,topn=1)[0][0]    #meme res avec _cosmul
                    # second_word_classe=model.wv.most_similar_to_given(window_sumUp,classe)
                    # first_word_window=model.wv.most_similar_to_given(second_word_classe,window)
                    # if model.wv.similarity(first_word_window, second_word_classe)>=min_score_to_permit:
                    #     declinaisons.append(possibility)
                    #     break
                    """
                    étape critique: prendre tout dans les deux groupes pour éviter les doubles ambiguités ex serveur bar peut
                    devenir serveur bare et entrer en similarité avec serveur mysql alors que bar et bare ont une mauvaise sim
                    mais si on extrait le plus similaire de la classe et de la fenetre, il se retrouve avec serveur
                    prendre tout le groupe interdit à bare de remplacer bar
                    """
                    if model.wv.n_similarity(window, classe)>=min_score_to_permit:
                        declinaisons.append(possibility)
                        break



            declinaisons.append(word)
            if len(declinaisons) == 1:
                new_sentence.append(word)
            else:
                new_sentence.append(declinaisons)
        else:
            new_sentence.append(word)
    return new_sentence

def asr_migrateSentence(sentence_to_change: asr_sentence, reference_sentence: asr_sentence, dictionary: asr_dictionary, model: gensim.models.Word2Vec,
                       fast_and_approximate_migration=False):
    """
    :param sentence_to_change: Sentence qui va migrer vers la reference_sentence
    :param reference_sentence: Sentence qui ne migre pas
    :param fast_and_approximate_migration: si ce mode est activé la phrase de référence est résumée à un mot
    et les migrations sont calculées par rapport à ce mot
    :return:
    """
    new_sentence = []
    if fast_and_approximate_migration:
        suw_reference = model.wv.most_similar(positive=reference_sentence.inTheVocabulary)[0][0]
    # if dictionary.commonUsesRules_loaded == False:
    #     print_log("ERROR: sentence migration request without commonUses loaded !!!")
    #     return ''
    if len(sentence_to_change.inTheVocabulary)==0 or len(reference_sentence.inTheVocabulary)==0:
        empty_sentence='sentence_to_change' if len(sentence_to_change.inTheVocabulary)==0 else 'reference_sentence'
        print_log("**********************************************")
        print_log('ERROR | asr_ANALYSE | asr_migrateSentence')
        print_log("Request for empty length sentence migration for "+empty_sentence)
        print_log("**********************************************")
        return []

    if reference_sentence.hasMigrated:
        groupeDeReference = reference_sentence.lastMigration
    # elif reference_sentence.wasPreparedToMigrate:
    #     groupeDeReference = reference_sentence.SERIALIZE_DECLINAISONS()
    else:
        groupeDeReference = reference_sentence.inTheVocabulary

    for groupeDeclinaisons in sentence_to_change.withDeclinaisons:
        # on prend un élément de withDeclinaisons à la fois
        if isinstance(groupeDeclinaisons, list):
            # l'élément est une liste sinon c'est un mot simple à prendre comme tel
            if fast_and_approximate_migration:
                new_word = model.wv.most_similar_to_given(suw_reference, groupeDeclinaisons)
                new_sentence.append(new_word)
            else:
                #ETAPE 1 : recherche de mots en communs sans calcul de similarité
                intersection={}
                if reference_sentence.hasMigrated:
                    #la référence a déja migré: on y recherche un mot en commun en priorité
                    intersection = set(groupeDeclinaisons).intersection(set(reference_sentence.lastMigration))
                if len(intersection)==0:
                    # choux blancs => on recherche dans les déclinaisons ou, à défaut, la phrase filtrée
                    if reference_sentence.wasPreparedToMigrate:
                        intersection = set(groupeDeclinaisons).intersection(set(reference_sentence.SERIALIZE_DECLINAISONS()))
                    else:
                        intersection = set(groupeDeclinaisons).intersection(set(reference_sentence.inTheVocabulary))
                #ensuite soit on a trouvé au moins un mot en commun et on le retient sinon
                if len(intersection)>0:
                    new_word=intersection.pop()
                else:
                    #1 on créé les déclinaisons
                    #2 on migre l'une vers le inTheVocabulary de l'autre => cela produit le lastMigration de l'une
                    #3 on prend l'autre pour la faire migrer vers le lastMigration de l'une
                    #4 on refait le lastMigration de l'une à l'aide du lastMigration de l'autre

                    try:
                        scores_declinaisons = [
                            [ declinaison, model.wv.n_similarity([declinaison], groupeDeReference)]
                            for declinaison in groupeDeclinaisons]
                    except (RuntimeError, TypeError, NameError):
                        print_log("**********************************************")
                        print_log(('ERROR | asr_ANALYSE | asr_migrateSentence'))
                        print_log(NameError)
                        print_log(groupeDeclinaisons.__repr__())
                        print_log(str(groupeDeReference))
                        print_log(str(sentence_to_change.inTheVocabulary))
                        print_log("**********************************************")
                        return []
                    scores_declinaisons.sort(key=itemgetter(1), reverse=True)
                    new_word = scores_declinaisons[0][0]  # ici prend le plus proche dans tous les candidats retenus
                new_sentence.append(new_word)
        else:
            new_sentence.append(groupeDeclinaisons)
    return new_sentence

def asr_extractBagOfWords(sentence_list, center, window_length):
    start = max(0, (center - int(window_length / 2)))
    stop = min(len(sentence_list) - 1, center + int(window_length / 2))
    while ((stop - start) < window_length) and (stop < (len(sentence_list) - 1)):
        stop += 1
    while ((stop - start) < window_length) and (start > 0):
        start -= 1
    new_sentence = sentence_list.copy()
    new_sentence.pop(center)
    return new_sentence[start:stop]

def asr_buildPossibilitiesFromPTM(endOfSentence:list):
    if not isinstance(endOfSentence,list) or len(endOfSentence)==0:
        return None
    next=endOfSentence[0]
    if len(endOfSentence)>1:
        next_expand = asr_buildPossibilitiesFromPTM(endOfSentence[1:])
        result = []
        if isinstance(next, list):
            for word in next:
                for line in next_expand:
                    t = [word]
                    t.extend(line)
                    result.append(t)
        else:
            for line in next_expand:
                t = [next]
                t.extend(line)
                result.append(t)
    else:
        if isinstance(next, list):
            result = [ [word] for word in next ]
        else:
            result = [ [next] ]
    return result

def asr_addCommonUsesRule(initial,target,dictionary,model):
    classes_usage = asr_classeUsage(target, model, dictionary, min_group_size=3, score_limit_aggregation=0.5, similarity_window_width=0.2,logging=False)
    if len(classes_usage)>0:
        if initial not in dictionary.commonUsesRules_map.keys():
            dictionary.commonUsesRules_map[initial] = set()
        dictionary.commonUsesRules_map[initial].add(target)
        dictionary.commonUsesRules_classes[target]=classes_usage
        print(target,classes_usage)
    classes_usage = asr_classeUsage(initial, model, dictionary, min_group_size=3, score_limit_aggregation=0.5, similarity_window_width=0.2,logging=False)
    if len(classes_usage)>0:
        if target not in dictionary.commonUsesRules_map.keys():
            dictionary.commonUsesRules_map[initial] = set()
        dictionary.commonUsesRules_map[target].add(initial)
        dictionary.commonUsesRules_classes[initial]=classes_usage
        print(initial,classes_usage)


def asr_extractThemesFromSentence(sentence:asr_sentence,themesVirtualModel:gensim.models.Word2Vec):
    if sentence.topics.__len__()==0:
        sentence.BUILD_TOPICS()
    results=[]
    for topic in sentence.topics:
        MV=numpy.array([sentence.model.wv.get_vector(word) for word in topic.content]).mean(axis=0)
        # MV=numpy.array([sentence.model.wv.get_vector(word) for word in topic.content_set]).mean(axis=0)
        res=themesVirtualModel.wv.most_similar(positive=[MV])
        results.append([res[0][0],res[0][1],topic.weight,topic.content.__len__()])
        print(res[0][0],res[0][1],topic.content)
        # results.append([res[0][0],res[0][1],topic.weight,topic.content_set.__len__()])
    df=pandas.DataFrame(results,columns=['libelle','score','weight','effectif'])
    df=df[df['score']>0.5]

    df = df.drop(['score'], axis=1)
    df = df.groupby("libelle").sum()[["weight", "effectif"]]
    df=df[df['effectif']>=2]
    df = df.drop(['effectif'], axis=1)
    df = df.sort_values(by='weight',ascending=False).reset_index()
    return df['libelle'].to_list()

def asr_extractThemesFromWeightedITVWordsLists(wordsLists,themesVirtualModel:gensim.models.Word2Vec,gensim_model:gensim.models.Word2Vec,minWeight=0.05):
    results=[]
    for topic,weight in wordsLists:
        MV=numpy.array([gensim_model.wv.get_vector(word) for word in topic]).mean(axis=0)
        # MV=numpy.array([sentence.model.wv.get_vector(word) for word in topic.content_set]).mean(axis=0)
        res=themesVirtualModel.wv.most_similar(positive=[MV])
        results.append([res[0][0],res[0][1],weight])
        # results.append([res[0][0],res[0][1],topic.weight,topic.content_set.__len__()])
    df=pandas.DataFrame(results,columns=['libelle','score','weight'])
    df=df[df['score']>0.5]
    df = df.drop(['score'], axis=1)
    df = df.groupby("libelle").sum()[["weight"]]
    df=df[df['weight']>=minWeight]
    df = df.sort_values(by='weight',ascending=False).reset_index()
    libelles=df['libelle'].to_list()
    weights=df['weight'].to_list()
    return [ [libelle, weight] for libelle, weight in zip(libelles,weights)]

def asr_similar_strings_score(a, b):
    return SequenceMatcher(None, a, b).ratio()

if __name__=='__main__':
    from mpearl_lib.asr_initServer import *
    phrases=[]
    phrases.append("""conception cao de carte électronique analogique et numérique""")
    phrases.append("""achats industriels sourcing négociation de contrats suivi des commandes""")
    phrases.append("""Veiller au respect des règles de sécurité pendant les phases de travaux
                Etre responsable du suivi budgétaire, de la trésorerie et de la rentabilité des affaires""")
    phrases.append("""Gestion d’un marché de travaux CVC:
                - Chiffrage de travaux CVC.
                - Maîtrise des outils informatiques (Autocad, SAP, Quick Devis, G.T.C, G.M.A.O.).
                - Piloter et assurer le suivi des chantiers: équipes de techniciens et sous traitants.
                - garant des aspects techniques: électrotechnique, électricité bâtiment, courant faible, électronique industrielle.
                - Chauffage, climatisation, froid industriel et commercial toutes puissances, automatisme, régulation.
                Veiller au respect des règles de sécurité pendant les phases de travaux
                Etre responsable du suivi budgétaire, de la trésorerie et de la rentabilité des affaires""")

    phrases.append("""Proposer et promouvoir une sélection de maisons et d’appartements à vendre et à louer.""")
    phrases.append("""Proposer et promouvoir une sélection de maisons et d’appartements à vendre et à louer.
                Visiter les logements et terrains pour  recueillir les données de superficie, coût des charges et des impôts, travaux budgétés ou à prévoir
                Évaluer la valeur d’un bien immobilier et conseiller le client sur les améliorations et les obligations règlementaires.""")
    for phrase in phrases:
        sentence=asr_sentence(phrase,dictionary,gensimGlobalModel)
        sentence.FILTER()
        print(" ".join(sentence.inTheVocabulary))
        sentence.COMPLETE(new_words=5)
        print(" ".join(sentence.inTheVocabulary))

