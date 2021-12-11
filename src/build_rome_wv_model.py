from asr_framework.asr_gensimCustom import *

if __name__=='__main__':
    #Chargement du modèle ROME en open-data
    model=asr_load_light_model(model_filename='../open-data/asr_global_wv')
    vectors = np.asarray(model.wv.vectors)
    #export en CSV
    df = pd.DataFrame(vectors)
    df.to_csv('full_dim.csv', sep='\t', header=False, encoding='ansi', index=False)
