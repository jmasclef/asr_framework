import gensim

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
