import gensim

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

class asr_virtual_model():
    def __init__(self,gensim_model: gensim.models.Word2Vec =None,gensim_wv: gensim.models.KeyedVectors =None):
        if gensim_model:
            self.wv=gensim_model.wv
        elif gensim_wv:
            self.wv=gensim_wv

# class asr_virtual_wv_model():
#     def __init__(self,gensim_model_wv: gensim.models.KeyedVectors):
#         self.wv=gensim_model.wv

def asr_createEmptyGensimModel():
    virtualCorpus=[[ CTE_VIRTUAL_WORD ]]*final_min_tf_word
    model = gensim.models.Word2Vec(virtualCorpus, vector_size=gensim_model_dimension,
                                   sg=gensim_training_algo, window=gensim_model_window,
                                   min_count=final_min_tf_word, workers=os.cpu_count(), trim_rule=None,
                                   epochs=gensim_model_final_iterations)
    return model


def asr_addVectorToModel(labels, vectors,model: gensim.models.word2vec):
    if len(labels)!=len(vectors):
        raise NameError ("Lists have different sizes")
    else:
        model.wv.add_vectors(keys=labels,weights=vectors)
        try:
            del model.wv.vectors_norm
        except:
            pass
    return

def asr_load_model(model_filename,*args,**kwargs):
    return gensim.models.Word2Vec.load(fname=model_filename,*args,**kwargs)

def asr_save_light_model(*,model_name:gensim.models.Word2Vec,model_filename:str):
    wv=model_name.wv
    wv.save(model_filename)

def asr_load_light_model(*, model_filename: str):
    wv = gensim.models.KeyedVectors.load(fname=model_filename,mmap='r')
    return asr_virtual_model(gensim_wv=wv)

def asr_gensim_word2vec(corpus, size=gensim_model_dimension, sg=gensim_training_algo, window=gensim_model_window,
                                       min_count=intermediate_min_tf_word, iter=gensim_model_itermediate_iterations):
    gensim.models.Word2Vec(corpus, size=size, sg=sg, window=window, min_count=min_count,iter=iter,
                           workers=os.cpu_count(), trim_rule=None)