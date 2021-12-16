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

# import gensim
from gensim.models import Word2Vec as asr_semantic_model
from gensim.models import KeyedVectors as asr_semantic_vectors
from .asr_constantes import *
"""
NEXT
Intégrer ANNOY en option
Utiliser time => time.process_time()
Utiliser logging
"""

class asr_virtual_gensim_model():
    def __init__(self,from_wv: asr_semantic_vectors =None, create_empty_virtual=False):
        if from_gensim_wv:
            self.wv=from_wv
        elif create_empty_virtual:
            self.wv=__asr_createEmptyGensimModel()
        else:
            raise 'Créer un vide ou Associer une instance gensim.models.KeyedVectors'

    # def __init__(self,gensim_model: asr_semantic_model =None,gensim_wv: asr_semantic_vectors =None):
    #     if gensim_model:
    #         self.wv=gensim_model.wv
    #     elif gensim_wv:
    #         self.wv=gensim_wv

    def ADD_VECTORS(self,labels, vectors ):
        self.__asr_addVectorToModel(labels=labels, vectors=vectors,model=self.wv)


    def __asr_createEmptyGensimModel():
        virtualCorpus=[[ CTE_VIRTUAL_WORD ]]*final_min_tf_word
        model = asr_semantic_model(virtualCorpus, vector_size=gensim_model_dimension,
                                       sg=gensim_training_algo, window=gensim_model_window,
                                       min_count=final_min_tf_word, workers=os.cpu_count(), trim_rule=None,
                                       epochs=gensim_model_final_iterations)
        return model


    def __asr_addVectorToModel(labels, vectors,model_KeyedVectors: asr_semantic_vectors):
        if len(labels)!=len(vectors):
            raise NameError ("Lists have different sizes")
        else:
            model_KeyedVectors.add_vectors(keys=labels,weights=vectors)
            try:
                del model_KeyedVectors.vectors_norm
            except:
                pass
        return

def asr_load_model(file_name:str,base_dir:str,*args,**kwargs):
    model_filename = base_dir+file_name if base_dir else file_name
    return asr_semantic_model.load(fname=model_filename,*args,**kwargs)

def asr_save_light_model(*,model_name:asr_semantic_model,model_filename:str):
    wv=model_name.wv
    wv.save(model_filename)

def asr_load_light_model(*, model_filename: str):
    wv = asr_semantic_vectors.load(fname=model_filename,mmap='r')
    return asr_virtual_model(gensim_wv=wv)

def asr_gensim_word2vec(corpus, mode_kwargs:dict()=final_mode_kwargs):
    return asr_semantic_model(sentences=corpus, **mode_kwargs)