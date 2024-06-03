import pandas as pd
import ujson as json 
import os
from collections import Counter
from pathlib import Path
from multiprocessing import Pool
from ast import literal_eval
import sys
import psutil
import time
from memory_profiler import memory_usage

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



df_cols_to_keep = ['tweet_id', 'movement','stance','protest_activity','stakeholder_group','all_frames',
       'Task3:diagnostic', 'Task3:prognostic', 'Task3:identify', 'Task3:blame', 'Task4:solution', 'Task4:tactics',
       'Task4:solidarity', 'Task4:counter', 'Task5:motivational-elements','hashtags','mentions']

linguistic_features = ['hashtags','mentions','tokens', 'lemmas','verb_lemmas', 'noun_lemmas', 
                       'adjective_lemmas', 'pronouns', 'verb_tense', 
                       'pronoun_number', 'pronoun_person', 'subject_verb', 'verb_object', 'noun_chunks']

subgroups_list = [[],['movement'],['protest_activity'],['stance'],['stakeholder_group'],
                 ['movement','protest_activity'],['movement','stance'],['movement','stakeholder_group'],
                 ['protest_activity','stakeholder_group']]

def convert_dict_to_lists(d):
    if len(d.keys()) == 0:
        return None
    res = []
    for key in d.keys():
        res+=[key]*d[key]
    return res


def load_data(corpus_file,feature_file):
    df = pd.read_csv(corpus_file, sep='\t',dtype={'tweet_id': str})
    features = pd.read_json(feature_file, lines=True,dtype={'tweet_id': str})
    ling_features = [feature for feature in features.columns if feature in linguistic_features]
    features = features[['tweet_id']+ling_features]
    if 'hashtags' in features.columns:
        features = features.drop(columns=['hashtags'])
    if 'mentions' in features.columns:
        features = features.drop(columns=['mentions'])


    df = df[df['Task1:relevance']==1]
    df['stance'] = df['Task2:stance'].apply(lambda x: 'anti' if x==0 else 'neutral' if x==1 else 'pro' if x==2 else None)
    df['all_frames'] = 1
    df = df[df_cols_to_keep]

    df  = df.merge(features, on='tweet_id')
    df = df.drop_duplicates(subset=['tweet_id'])

    # convert each element of linguistic_features columns to a Counter object
    for col in ling_features:
        if col not in ['mentions','hashtags']:
            df[col] = df[col].apply(lambda x: convert_dict_to_lists(x))            
            #df[col] = df[col].apply(lambda x: Counter(x))

    df['mentions'] = df['mentions'].apply(lambda x: literal_eval(x))
    df['hashtags'] = df['hashtags'].apply(lambda x: literal_eval(x))
    # convert hashtags and mentions into feature format
    # df['hashtags'] = df['hashtags'].apply(lambda x: Counter([hashtag.lower() for hashtag in x]))
    # df['mentions'] = df['mentions'].apply(lambda x: Counter([mention['screen_name'] for mention in x]))
    df['hashtags'] = df['hashtags'].apply(lambda x: [hashtag.lower() if len(x)>0 else None for hashtag in x])
    df['mentions'] = df['mentions'].apply(lambda x: [mention['screen_name'] if len(x)>0 else None for mention in x])



    return df


corpus_file = '/nfs/turbo/si-juliame/social-movements/full_corpus_with_preds_and_stakeholders_08-02-2023.tsv'
feature_file = '/nfs/turbo/si-juliame/social-movements/ling_features_sm_full_corpus_with_preds_and_stakeholders_08-16-2023.jsonl'
base_out_dir = '/nfs/turbo/si-juliame/social-movements/feature_counts_08-16-2023/'
df = load_data(corpus_file,feature_file)
print(df)
print("Size: ",sys.getsizeof(df))

def sum_counters(counter_col):
    res = []
    for l in counter_col:
        res+=l
    return Counter(res)


def count_features(feature,frame,subgroups):
    elems = [feature,frame]+subgroups
    print(f'Counting features for {feature}, {frame} and {subgroups}')
    df_sub = df[elems][(df[elems][frame]==1) & (df[elems][feature].notnull())]
    df_sub = df_sub.drop(columns=[frame])

    if len(subgroups) == 0:
        df_sub = df_sub.apply(sum_counters)
        out_dir = os.path.join(base_out_dir,feature,frame_map[frame])
        out_file = os.path.join(out_dir,'full.json')
        p = Path(out_dir)
        p.mkdir(parents=True, exist_ok=True)
        with open(out_file,'w') as f:
            json.dump(df_sub[feature],f)

    else:
        df_sub = df_sub.groupby(by=subgroups).agg(sum_counters).reset_index()
        df_sub['specific_subgroups'] = df_sub[subgroups].apply(lambda x: '_'.join(x),axis=1)
        out_dir = os.path.join(base_out_dir,feature,frame_map[frame],'_'.join(subgroups))
        p = Path(out_dir)
        p.mkdir(parents=True, exist_ok=True)
        for spec_group in df_sub['specific_subgroups'].unique():
            res = df_sub[df_sub['specific_subgroups']==spec_group][feature].tolist()[0]
            out_file = os.path.join(out_dir,f'{spec_group}.json')                
            with open(out_file,'w') as f:
                json.dump(res,f)  




    


def main():
    func_tuples = []
    for feature in linguistic_features:
        for subgroups in subgroups_list:
            for frame in frame_map.keys():
                func_tuples.append((feature,frame,subgroups))

    num_processes = 4
    print(f'Running {num_processes} processes')
    print(func_tuples)
    with Pool(num_processes) as p:
        p.starmap(count_features,func_tuples)
    


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
