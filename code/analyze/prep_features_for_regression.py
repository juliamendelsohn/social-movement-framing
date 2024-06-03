import pandas as pd
import ujson as json 
import os
from collections import Counter
from pathlib import Path
from multiprocessing import Pool
from ast import literal_eval
import sys
import time 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


corpus_file = '/nfs/turbo/si-juliame/social-movements/full_corpus_with_preds_and_stakeholders_08-02-2023.tsv'
feature_file = '/nfs/turbo/si-juliame/social-movements/ling_features_sm_full_corpus_with_preds_and_stakeholders_08-16-2023.jsonl'
out_dir = '/nfs/turbo/si-juliame/social-movements/datasheets_for_regression_08-20-2023/'


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



df_cols_to_keep = ['tweet_id', 'movement','stance','protest_activity','stakeholder_group',
       'diagnostic', 'prognostic', 'identify', 'blame', 'solution', 'tactics',
       'solidarity', 'counter', 'motivational']

linguistic_features = ['verb_tense', 'pronoun_number', 'pronoun_person']



def load_data(corpus_file,feature_file):
    df = pd.read_csv(corpus_file, sep='\t',dtype={'tweet_id': str})
    features = pd.read_json(feature_file, lines=True,dtype={'tweet_id': str})
    features = features[['tweet_id']+linguistic_features]

    df = df[df['Task1:relevance']==1]
    df['stance'] = df['Task2:stance'].apply(lambda x: 'anti' if x==0 else 'neutral' if x==1 else 'pro' if x==2 else None)
    df = df.rename(columns={k:v for k,v in frame_map.items()})
    df = df[df_cols_to_keep]

    df  = df.merge(features, on='tweet_id')
    df.drop_duplicates(subset=['tweet_id'],inplace=True)
    
    return df


def reformat_dv_tense(df):
    new_rows = []
    for i,row in df.iterrows():
        tenses = row['verb_tense']
        if 'Pres' in tenses:
            num_present = tenses['Pres']
            for j in range(num_present):
                new_row = row[df_cols_to_keep]
                new_row['is_present'] = 1
                new_rows.append(new_row)
        if 'Past' in tenses:
            num_past = tenses['Past']
            for k in range(num_past):
                new_row = row[df_cols_to_keep]
                new_row['is_present'] = 0
                new_rows.append(new_row)   
    new_df = pd.concat(new_rows,axis=1).transpose()
    print(sys.getsizeof(new_df) / (1024**2))
    new_df.to_csv(os.path.join(out_dir,'verb_tense.tsv'),sep='\t',index=False)

def reformat_dv_pronoun_number(df):
    new_rows = []
    for i,row in df.iterrows():
        pronoun_numbers = row['pronoun_number']
        if 'Plur' in pronoun_numbers:
            num_present = pronoun_numbers['Plur']
            for j in range(num_present):
                new_row = row[df_cols_to_keep]
                new_row['is_plural'] = 1
                new_rows.append(new_row)
        if 'Sing' in pronoun_numbers:
            num_past = pronoun_numbers['Sing']
            for k in range(num_past):
                new_row = row[df_cols_to_keep]
                new_row['is_plural'] = 0
                new_rows.append(new_row)   
    new_df = pd.concat(new_rows,axis=1).transpose()
    print(sys.getsizeof(new_df) / (1024**2))
    new_df.to_csv(os.path.join(out_dir,'pronoun_number.tsv'),sep='\t',index=False)

def reformat_dv(df,feature):
    new_df = df[df_cols_to_keep+[feature]]
    new_df = pd.concat([new_df.drop([feature],axis=1),new_df[feature].apply(pd.Series)],axis=1)
    new_df.fillna(0,inplace=True)
    new_df = pd.melt(new_df,id_vars=df_cols_to_keep)
    new_df = new_df.loc[new_df.index.repeat(new_df['value'])]
    return new_df

def fast_reformat_tense(df):
    new_df = reformat_dv(df,'verb_tense')
    new_df['is_present'] = new_df['variable'].apply(lambda x: 1 if x=='Pres' else 0)
    new_df.drop(['variable','value'],axis=1,inplace=True)
    print(new_df)
    new_df.to_csv(os.path.join(out_dir,'verb_tense.tsv'),sep='\t',index=False)

def fast_reformat_pronoun_number(df):
    new_df = reformat_dv(df,'pronoun_number')
    new_df['is_plural'] = new_df['variable'].apply(lambda x: 1 if x=='Plur' else 0)
    new_df.drop(['variable','value'],axis=1,inplace=True)
    print(new_df)
    new_df.to_csv(os.path.join(out_dir,'pronoun_number.tsv'),sep='\t',index=False)

def fast_reformat_pronoun_person(df):
    new_df = reformat_dv(df,'pronoun_person')
    new_df['is_first'] = new_df['variable'].apply(lambda x: 1 if x=='1' else 0)
    new_df['is_second'] = new_df['variable'].apply(lambda x: 1 if x=='2' else 0)
    new_df['is_third'] = new_df['variable'].apply(lambda x: 1 if x=='3' else 0)
    new_df.drop(['variable','value'],axis=1,inplace=True)
    print(new_df)
    new_df.to_csv(os.path.join(out_dir,'pronoun_person.tsv'),sep='\t',index=False)


def reformat_dv_pronoun_person(df):
    new_rows = []
    for i,row in df.iterrows():
        persons = row['pronoun_person']
        if '1' in persons:
            num_first = persons['1']
            for j in range(num_first):
                new_row = row[df_cols_to_keep]
                new_row['is_first'] = 1
                new_row['is_second'] = 0
                new_row['is_third'] = 0
                new_rows.append(new_row)
        if '2' in persons:
            num_second = persons['2']
            for k in range(num_second):
                new_row = row[df_cols_to_keep]
                new_row['is_first'] = 0
                new_row['is_second'] = 1
                new_row['is_third'] = 0
                new_rows.append(new_row)
        if '3' in persons:
            num_third = persons['3']
            for k in range(num_third):
                new_row = row[df_cols_to_keep]
                new_row['is_first'] = 0
                new_row['is_second'] = 0
                new_row['is_third'] = 1
                new_rows.append(new_row)
    new_df = pd.concat(new_rows,axis=1).transpose()
    print(sys.getsizeof(new_df) / (1024**2))
    new_df.to_csv(os.path.join(out_dir,'pronoun_person.tsv'),sep='\t',index=False)
    


def main():
    df = load_data(corpus_file,feature_file)
    print("Size: ",sys.getsizeof(df) / (1024**2))
    print(df)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    # reformat_dv_tense(df)
    # reformat_dv_pronoun_number(df)
    # reformat_dv_pronoun_person(df)

    with Pool(3) as p:
        p.map_async(fast_reformat_tense, [df])
        p.map_async(fast_reformat_pronoun_number, [df])
        p.map_async(fast_reformat_pronoun_person, [df])
        p.close()
        p.join()

    # fast_reformat_tense(df)
    # fast_reformat_pronoun_number(df)
    # fast_reformat_pronoun_person(df)


    


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
