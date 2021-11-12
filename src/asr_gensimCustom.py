import gensim

def mp_createEmptyGensimModel():
    virtualCorpus=[[ CTE_VIRTUAL_WORD ]]*final_min_tf_word
    model = gensim.models.Word2Vec(virtualCorpus, vector_size=gensim_model_dimension,
                                   sg=gensim_training_algo, window=gensim_model_window,
                                   min_count=final_min_tf_word, workers=os.cpu_count(), trim_rule=None,
                                   epochs=gensim_model_final_iterations)
    return model


def mp_addVectorToModel(labels, vectors,model: gensim.models.word2vec):
    if len(labels)!=len(vectors):
        raise NameError ("Lists have different sizes")
    else:
        model.wv.add_vectors(keys=labels,weights=vectors)
        try:
            del model.wv.vectors_norm
        except:
            pass
    return