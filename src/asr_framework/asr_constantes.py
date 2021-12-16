"""
    Copyright 2021 SEIDO CONSEILS S.A.S.
    This file is part of Framework Assistance Sémantique au Recrutement (ASR).

    Framework Assistance Sémantique au Recrutement (ASR) is free software:
    you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Framework Assistance Sémantique au Recrutement (ASR) is distributed
    in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Framework Assistance Sémantique au Recrutement (ASR).
    If not, see <https://www.gnu.org/licenses/>.
"""

log_file_name="asr_log"
CTE_VIRTUAL_WORD= "virtualWord"
from os import cpu_count as os_cpu_count
"""
RULES DICTS
"""
CTE_FILENAME_STATIC_RULES   =   "static_rules.csv"
CTE_FILENAME_DYNAMIC_RULES  =   "dynamic_rules.csv"
# CTE_FILENAME_STATIC_RULES   =   "asr_static_rules.csv"
# CTE_FILENAME_DYNAMIC_RULES  =   "asr_dynamic_rules.csv"
"""
LOGGING
"""
from logging import getLogger as logging_getLogger, basicConfig as logging_basicConfig
logging_basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
asr_logger = logging_getLogger('ASR_LOG')
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
"""
Définit le seuil de logging: DEBUG, INFO, WARNING, ERROR ou CRITICAL
Le mode de logging est défini en même temps que le mode de fonctionnement du framework
En mode debug, le logging est verbeux et l'appli crash sur les erreurs non critiques
En mode production, le logging est aligné par la valeur de ASR_MODE_PRODUCTION selon INFO, WARNING, ERROR ou CRITICAL
et les erreurs non critiques ne cessent pas l'exécution de l'appli
"""
ASR_MODE_DEBUG      =   DEBUG
ASR_MODE_PRODUCTION =   INFO
"""
MODE DEBUG || PRODUCTION
"""
#ASR_MODE doit être défini par le module appelant, à défaut fixe le mode
ASR_MODE=ASR_MODE_DEBUG
asr_logger.setLevel(ASR_MODE)




"""
SECTION PARAMETRES GENSIM
"""
intermediate_min_tf_word = 3  # min term freq for plural,accents and gensim
intermediate_min_df_word = 2  # min doc freq for plural and accents
final_min_tf_word = 3
similarity_limit_for_replacement = 0.6  # 0.7 baissé à 0.6
gensim_model_itermediate_iterations = 7  # default is 5 but can give up to 20% similarity variations
gensim_model_final_iterations = 10
"""
Sur 5 itérations les scores de similarité ont de fortes variations d'un modèle à un autre, jusqu'à 20%...
Passer à 10 stabilise les variations à l'ordre du 1%
Passer de 10 à 15 réduit les scores de quelques pourcents (4% constatés)
"""
gensim_model_dimension = 300  # (100-1000) 300 is known as a good value, cf standford
gensim_model_window = 10  # Maximum distance between the current and predicted word within a sentence
"""
The size of the context window determines how many words before and after a given word would be included as context
words of the given word. According to the authors' note, the recommended value is 10 for skip-gram and 5 for CBOW.
=> Faut il tester avec moins que 10 en supposant que les descriptions professionnelles sont plus condensées et moins rédigées ?
"""
gensim_training_algo_skipgram = 1
gensim_training_algo_cbow = 0
gensim_training_algo = gensim_training_algo_skipgram  # Training algorithm: 1 for skip-gram; otherwise CBOW
"""  
The CBOW architecture predicts the current word based on the context.
The order of context words does not influence prediction (bag-of-words assumption). 
In the continuous skip-gram architecture, the model uses the current word to predict the surrounding window of context 
words. The skip-gram architecture weighs nearby context words more heavily than more distant context words.
Finally, the Skip-gram architecture works slightly worse on the syntactic task than the CBOW model, and much better on
the semantic part of the test than all the other models. 
CBOW éffondre les scores de similarité
CBOW is faster while skip-gram is slower but does a better job for infrequent words.
"""

learning_mode_kwargs = {'vector_size': gensim_model_dimension, 'sg': gensim_training_algo,
                        'window': gensim_model_window,
                        'min_count': intermediate_min_tf_word, 'workers': os_cpu_count(), 'trim_rule': None,
                        'epochs': gensim_model_itermediate_iterations}
final_mode_kwargs = {'vector_size': gensim_model_dimension, 'sg': gensim_training_algo,
                     'window': gensim_model_window,
                     'min_count': final_min_tf_word, 'workers': os_cpu_count(), 'trim_rule': None,
                     'epochs': gensim_model_final_iterations}

example_mode_kwargs = {'vector_size': 100, 'sg': gensim_training_algo,
                       'window': gensim_model_window,
                       'min_count': final_min_tf_word, 'workers': os_cpu_count(), 'trim_rule': None,
                       'epochs': gensim_model_final_iterations }

#39% de stopwords estimés
BLOCKS_MIN_AUTH_WORDS=8
SENTENCE_MIN_AUTH_WORDS=5
SENTENCE_MAX_AUTH_WORDS=500 #300
SENTENCE_MIN_RECOM_WORDS=15
SENTENCE_MAX_RECOM_WORDS=150
SENTENCE_FILTER_THRESHOLD = 2* SENTENCE_MIN_RECOM_WORDS


CTE_numberMetiersToScan = 10
CTE_numberMetiersToDisplay = 15
CTE_frequenceSkillsRate = 0.33   #le baisser augmente le nombre de compétences inclus dans le score, donc baisse les scores plus vite et distancie les métiers différents
CTE_addMetiersTopnSkills = 3
CTE_maxMetiersToAddSkills = CTE_numberMetiersToScan

CTE_numberCandidatesToDisplay=30
CTE_numberCandidatesToScan=3*CTE_numberCandidatesToDisplay

RIASEC_EMPTY_DICT=dict({'R':0,'I':0,'A':0,'S':0,'E':0,'C':0})
METIER_SCORE_MIN = 0.6
# METIER_INTERM_SCORE_MIN_TO_ADD_NODES = 0.50
#Attention le mode de caclul change entre les deux
METIER_SCORE_MIN_TO_ADD_SKILL = 0.5     #passé de 0.6 à 0.5 tout retester
SKILLS_SCORE_RANGE = 6
CTE_COMPETENCES_TRANSVERSES = "00007"
CTE_COMPETENCES_LANGUES = "00245"
MIN_WORD_LENGTH = 2
MAX_WORD_LENGTH = 26

SEUIL_HAUT_SCORE_TRES_MAUVAIS=20
SEUIL_HAUT_SCORE_MAUVAIS=40
SEUIL_HAUT_SCORE_FAIBLE=50
SEUIL_HAUT_SCORE_MOYEN=60
SEUIL_HAUT_SCORE_BON=70
SEUIL_HAUT_SCORE_TRES_BON=85



"""
SECTION CONSTANTES ANALYSE
"""
#les markups fournissent des clés pour un découpage différents des corpus
#utilisés en tokénisation pour séparer les phrases et les paragrahpes avant un apprentissage
#il existe trois markups:
# un pour la fin de le phrase, pour les algos de fenêtre glissante
# un pour la fin de ligne pour les algos de splitting sémantique des phrases
# un pour la fin du fichier pour les algos de batch learning
ASR_MARKUP_LAYOUT = "#ASR_EO{}#"
MARKUP_EOP  = ASR_MARKUP_LAYOUT.format('P') #fin de phrase, peut remplacer un point (.)
MARKUP_EOL  = ASR_MARKUP_LAYOUT.format('L') #fin de ligne, peut remplacer un \n
MARKUP_EOF  = ASR_MARKUP_LAYOUT.format('F') #fin de fichier, peut remplacer une ligne vierge; non utilisé

RESUME_SECTIONS_MARKUPS = { MARKUP_EOP, MARKUP_EOL, MARKUP_EOF }

FRENCH_STOPWORDS_LIST_WO_MARKUPS = {'a', 'abord', 'absolument', 'afin', 'ah', 'ai', 'aie', 'ailleurs', 'ainsi', 'ait',
                                    'allaient', 'allo', 'allons', 'allô', 'alors', 'ans', 'anterieur', 'anterieure',
                                    'anterieures', 'aout', 'août', 'apres', 'après', 'as', 'assez', 'attendu', 'au',
                                    'aucun', 'aucune', 'aujourd', "aujourd'hui", 'aupres', 'auquel', 'aura', 'auraient',
                                    'aurait', 'aurez', 'auront', 'aussi', 'autre', 'autrefois', 'autrement', 'autres',
                                    'autrui', 'aux', 'auxquelles', 'auxquels', 'avaient', 'avais', 'avait', 'avant',
                                    'avec', 'avoir', 'avons', 'avr.', 'avril', 'ayant', 'bah', 'bas', 'basee', 'bat',
                                    'beau', 'beaucoup', 'bien', 'bigre', 'boulevard', 'boum', 'bravo', 'brrr', "c'",
                                    'car', 'ce', 'ceci', 'cela', 'celle', 'celle-ci', 'celle-là', 'celles', 'celles-ci',
                                    'celles-là', 'celui', 'celui-ci', 'celui-là', 'cent', 'cependant', 'certain',
                                    'certaine', 'certaines', 'certains', 'certes', 'ces', 'cet', 'cette', 'ceux',
                                    'ceux-ci', 'ceux-là', 'chacun', 'chacune', 'chaque', 'cher', 'chers', 'chez',
                                    'chiche', 'chut', 'chère', 'chères', 'ci', 'cinq', 'cinquantaine', 'cinquante',
                                    'cinquantième', 'cinquième', 'clac', 'clic', 'combien', 'comme', 'comment',
                                    'comparable', 'comparables', 'compris', 'concernant', 'contre', 'couic', 'crac',
                                    'c’', "d'", 'da', 'dans', 'de', 'debout', 'dec', 'dec.', 'decembre', 'dedans',
                                    'dehors', 'deja', 'delà', 'depuis', 'dernier', 'derniere', 'dernieres', 'derniers',
                                    'dernière', 'dernières', 'derriere', 'derrière', 'des', 'desormais', 'desquelles',
                                    'desquels', 'dessous', 'dessus', 'deux', 'deuxième', 'deuxièmement', 'devant',
                                    'devers', 'devra', 'different', 'differentes', 'differents', 'différent',
                                    'différente', 'différentes', 'différents', 'dimanche', 'dimanches', 'dire',
                                    'directe', 'directement', 'dit', 'dite', 'dits', 'divers', 'diverse', 'diverses',
                                    'dix', 'dix-huit', 'dix-neuf', 'dix-sept', 'dixième', 'doit', 'doivent', 'donc',
                                    'dont', 'douze', 'douzième', 'dring', 'du', 'duquel', 'durant', 'dès', 'déc',
                                    'déc.', 'décembre', 'désormais', 'd’', 'effet', 'egale', 'egalement', 'egales',
                                    'eh', 'elle', 'elle-même', 'elles', 'elles-mêmes', 'en', 'encore', 'enfin', 'entre',
                                    'envers', 'environ', 'es', 'est', 'et', 'etaient', 'etais', 'etait', 'etant', 'etc',
                                    'etre', 'eu', 'euh', 'eux', 'eux-mêmes', 'exactement', 'excepté', 'extenso',
                                    'exterieur', 'fais', 'faisaient', 'faisant', 'fait', 'façon', 'feront', 'fev',
                                    'fev.', 'fevr', 'fevr.', 'fevrier', 'fi', 'flac', 'floc', 'font', 'fév', 'fév.',
                                    'févr', 'févr.', 'février', 'gens', 'ha', 'hein', 'hem', 'hep', 'hi', 'ho', 'holà',
                                    'hop', 'hormis', 'hors', 'hou', 'houp', 'hue', 'hui', 'huit', 'huitième', 'hum',
                                    'hurrah', 'hé', 'hélas', 'i', 'il', 'ils', 'importe', "j'", 'jan', 'janv',
                                    'janvier', 'je', 'jeudi', 'jeudis', 'jours', 'juil.', 'juillet', 'juin', 'jusqu',
                                    "jusqu'", 'jusque', 'juste', 'j’', "l'", 'la', 'laisser', 'laquelle', 'las', 'le',
                                    'lequel', 'les', 'lesquelles', 'lesquels', 'leur', 'leurs', 'longtemps', 'lors',
                                    "lorsqu'", 'lorsque', 'lui', 'lui-meme', 'lui-même', 'lundi', 'lundis', 'là', 'lès',
                                    'l’', "m'", 'ma', 'mai', 'maint', 'maintenant', 'mais', 'malgre', 'malgré', 'mardi',
                                    'mardis', 'mars', 'maximale', 'me', 'meme', 'memes', 'merci', 'mercredi',
                                    'mercredis', 'mes', 'mien', 'mienne', 'miennes', 'miens', 'mille', 'mince',
                                    'minimale', 'moi', 'moi-meme', 'moi-même', 'moindres', 'moins', 'mois', 'mon',
                                    'moyennant', 'même', 'mêmes', 'm’', "n'", 'na', 'naturel', 'naturelle',
                                    'naturelles', 'ne', 'neanmoins', 'necessaire', 'necessairement', 'neuf', 'neuvième',
                                    'ni', 'nombreuses', 'nombreux', 'non', 'nos', 'notamment', 'notre', 'nous',
                                    'nous-mêmes', 'nouveau', 'nov', 'nov.', 'novembre', 'nul', 'néanmoins', 'nôtre',
                                    'nôtres', 'n’', 'o', 'oct', 'oct.', 'octobre', 'oh', 'ohé', 'ollé', 'olé', 'on',
                                    'ont', 'onze', 'onzième', 'ore', 'ou', 'ouf', 'oui', 'ouias', 'oust', 'ouste', 'outre',
                                    'ouvert', 'ouverte', 'ouverts', 'où', 'paf', 'pan', 'par', 'parce', 'parfois',
                                    'parle', 'parlent', 'parler', 'parmi', 'parseme', 'partant', 'particulier',
                                    'particulière', 'particulièrement', 'pas', 'passé', 'pendant', 'pense', 'permet',
                                    'personne', 'peu', 'peut', 'peut-être', 'peuvent', 'peux', 'pff', 'pfft', 'pfut',
                                    'pif', 'pire', 'plein', 'plouf', 'plus', 'plusieurs', 'plutôt', 'possessif',
                                    'possessifs', 'possible', 'possibles', 'pouah', 'pour', 'pourquoi', 'pourrais',
                                    'pourrait', 'pourtant', 'pouvait', 'prealable', 'precisement', 'premier', 'première',
                                    'premièrement', 'pres', 'probable', 'probante', 'procedant', 'proche', 'près',
                                    'psitt', 'pu', 'puis', 'puisque', 'pur', 'pure', "qu'", 'quand', 'quant',
                                    'quant-à-soi', 'quanta', 'quarante', 'quatorze', 'quatre', 'quatre-vingt',
                                    'quatrième', 'quatrièmement', 'que', 'quel', 'quelconque', 'quelle', 'quelles',
                                    "quelqu'un", 'quelque', 'quelques', 'quels', 'qui', 'quiconque', 'quinze', 'quoi',
                                    'quoique', 'qu’', 'rare', 'rarement', 'rares', 'relative', 'relativement',
                                    'remarquable', 'rend', 'rendre', 'restant', 'reste', 'restent', 'restrictif',
                                    'retour', 'revoici', 'revoilà', 'rien', 'rue', "s'", 'sa', 'sacrebleu', 'sait',
                                    'samedi', 'samedis', 'sans', 'sapristi', 'sauf', 'se', 'sein', 'seize', 'selon',
                                    'semblable', 'semblaient', 'semble', 'semblent', 'sent', 'sept', 'sept.',
                                    'septembre', 'septième', 'sera', 'seraient', 'serait', 'serez', 'seront', 'ses',
                                    'seul', 'seule', 'seulement', 'si', 'sien', 'sienne', 'siennes', 'siens', 'sinon',
                                    'six', 'sixième', 'soi', 'soi-même', 'soit', 'soixante', 'son', 'sont', 'sous',
                                    'souvent', 'specifique', 'specifiques', 'speculatif', 'stop', 'strictement',
                                    'subtiles', 'suffisant', 'suffisante', 'suffit', 'suis', 'suit', 'suivant',
                                    'suivante', 'suivantes', 'suivants', 'suivre', 'superpose', 'sur', 'surtout', 's’',
                                    "t'", 'ta', 'tac', 'tant', 'tardive', 'te', 'tel', 'telle', 'tellement', 'telles',
                                    'tels', 'tenant', 'tend', 'tenir', 'tente', 'tes', 'tic', 'tien', 'tienne',
                                    'tiennes', 'tiens', 'toc', 'toi', 'toi-même', 'ton', 'touchant', 'toujours', 'tous',
                                    'tout', 'toute', 'toutefois', 'toutes', 'treize', 'trente', 'tres', 'trois',
                                    'troisième', 'troisièmement', 'trop', 'très', 'tsoin', 'tsouin', 'tu', 'té', 't’',
                                    'un', 'une', 'unes', 'uniformement', 'unique', 'uniques', 'uns', 'va', 'vais',
                                    'vas', 'vendredi', 'vendredis', 'vers', 'via', 'vif', 'vifs', 'vingt', 'vivat',
                                    'vive', 'vives', 'vlan', 'voici', 'voilà', 'vont', 'vos', 'votre', 'vous',
                                    'vous-mêmes', 'vu', 'vé', 'vôtre', 'vôtres', 'zut', 'à', 'â', 'ça', 'ès', 'étaient',
                                    'étais', 'était', 'étant', 'été', 'être', 'ô'}

FRENCH_STOPWORDS_LIST_W_MARKUPS = RESUME_SECTIONS_MARKUPS.union(FRENCH_STOPWORDS_LIST_WO_MARKUPS)
