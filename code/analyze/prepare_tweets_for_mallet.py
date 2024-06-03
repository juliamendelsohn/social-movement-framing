import pandas as pd
import os
from pathlib import Path
from multiprocessing import Pool
from ast import literal_eval
import sys
import time

start_time = time.time()


corpus_file = '/nfs/turbo/si-juliame/social-movements/full_corpus_with_preds_and_stakeholders_08-02-2023.tsv'
feature_file = '/nfs/turbo/si-juliame/social-movements/ling_features_sm_full_corpus_with_preds_and_stakeholders_08-16-2023.jsonl'
base_out_dir = '/nfs/turbo/si-juliame/social-movements/topic_model_data_08-19-2023/'

frame_map = {}
frame_map['Task3:diagnostic'] = 'diagnostic'
frame_map['Task3:prognostic'] = 'prognostic'
frame_map['Task3:identify'] = 'identify'
frame_map['Task3:blame'] = 'blame'
frame_map['Task4:solution'] = 'solution'
frame_map['Task4:tactics'] = 'tactics'
frame_map['Task4:solidarity'] = 'solidarity'
frame_map['Task4:counter'] = 'counter'
frame_map['Task5:motivational-elements'] = 'motivational'
frame_map['all_frames'] = 'all_frames'


df_cols_to_keep = ['tweet_id', 'movement','diagnostic', 'prognostic', 'identify', 
                   'blame', 'solution', 'tactics','solidarity', 'motivational']

def convert_dict_to_string(d):
    res = []
    for key in d.keys():
        res+=[key]*d[key]
    return ' '.join(res)


def load_data(corpus_file,feature_file):
    features = pd.read_json(feature_file, lines=True,dtype={'tweet_id': str})[['tweet_id','tokens']]
    features['tokens'] = features['tokens'].apply(convert_dict_to_string)
    df = pd.read_csv(corpus_file, sep='\t',dtype={'tweet_id': str})
    df = df[df['Task1:relevance']==1]
    df = df.rename(columns={k:v for k,v in frame_map.items()})
    df = df[df_cols_to_keep]
    df = df.merge(features, on='tweet_id')
    df = df.drop_duplicates(subset=['tweet_id'])
    return df


def write_files(frame,movement=None):
    if movement:
        out_dir = os.path.join(base_out_dir,f"{frame}_{movement}")
        df_sub = df[(df[frame]==1) & (df['movement']==movement)]
    else:
        out_dir = os.path.join(base_out_dir,frame)
        df_sub = df[df[frame]==1]
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    df_sub[['tweet_id']].to_csv(os.path.join(out_dir,'tweet_ids.txt'),index=False,header=False)
    df_sub[['tokens']].to_csv(os.path.join(out_dir,'tokens.txt'),index=False,header=False)


df = load_data(corpus_file,feature_file)


def main():
    macro_frames = ['diagnostic','prognostic','motivational']
    frame_elements = ['identify','blame','solution','tactics','solidarity']
    movements = ['guns','immigration','lgbtq']
    func_tuples = []

    for frame in macro_frames+frame_elements:
        func_tuples.append((frame,None))
    for frame in macro_frames:
        for movement in movements:
            func_tuples.append((frame,movement))
    
    with Pool(4) as p:
        p.starmap(write_files,func_tuples)
    


if __name__ == '__main__':
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
