from asr_framework.asr_gensimCustom import *

if __name__=='__main__':
    print('ok')
    # model=asr_load_model('../open-data/final_gensim_model')
    # asr_save_light_model(model_name=model,model_filename='../open-data/asr_global_wv')
    model=asr_load_light_model(model_filename='../open-data/asr_global_wv')
    vectors = np.asarray(model.wv.vectors)
    df = pd.DataFrame(vectors)
    df.to_csv('full_dim.csv', sep='\t', header=False, encoding='ansi', index=False)
