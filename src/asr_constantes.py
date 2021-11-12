
CTE_VIRTUAL_WORD= "virtualWord"

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
SECTION PARAMETRES GENSIM
"""
intermediate_min_tf_word = 2  # min term freq for plural,accents and gensim
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
