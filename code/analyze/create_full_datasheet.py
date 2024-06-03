import pandas as pd
import os
import glob 
from ast import literal_eval
import functools as ft

categories = {}
categories['relevance'] = ['Task1:relevance']
categories['stance'] = ['Task2:stance']
categories['macro-frames'] = ['Task3:diagnostic','Task3:prognostic','Task5:motivational-macro']
categories['frame-elements'] = ['Task3:identify','Task3:blame','Task4:solution',
                                'Task4:tactics','Task4:solidarity','Task4:counter','Task5:motivational-elements']



def load_preds(preds_dir):
    files = glob.glob(os.path.join(preds_dir,'*'))
    dfs = []
    for filename in files:
        df = pd.read_csv(filename,sep='\t',dtype=str)
        dfs.append(df)
    df = pd.concat(dfs)
    return df

def convert_preds_to_columns(df,classifier):
    label_names = categories[classifier]
    df['preds'] = df['preds'].apply(lambda x: literal_eval(x))
    # explode preds and name new columns with label_names
    if len(label_names) == 1:
        df[label_names[0]] = df['preds'].apply(lambda x: int(x))
        return df[['tweet_id','text',label_names[0]]]
    else:
        for i,label_name in enumerate(label_names):
            df[label_name] = df['preds'].apply(lambda x: x[i])
        return df[['tweet_id','text']+label_names]
    
def combine_preds(modelname,classifiers,date):
    all_dfs = []
    for classifier in classifiers:
        preds_dir = f"/nfs/turbo/si-juliame/social-movements/full_predictions/{modelname}/{classifier}_{date}"
        df = load_preds(preds_dir)
        df = convert_preds_to_columns(df,classifier)
        all_dfs.append(df)
    df = ft.reduce(lambda left, right: pd.merge(left, right, on=['tweet_id','text']), all_dfs)
    #drop duplicates
    df = df.drop_duplicates()
    return df


def load_metadata(metadata_file):
    df = pd.read_csv(metadata_file,sep='\t')
    df = df.drop(columns=['text'])
    df = df.drop_duplicates()
    print(df)

def load_protest_actors(actor_file):
    df = pd.read_csv(actor_file,sep='\t')
    print(df)

def main():

    metadata_file="/nfs/turbo/si-juliame/social-movements/full_corpus_08-02-2023.tsv"
    actor_file = "home/juliame/social-movements/accounts_protest_actors_2017-2019.csv"
    out_file = "/nfs/turbo/si-juliame/social-movements/full_corpus_with_preds_08-02-2023.tsv"
    modelname = 'roberta-ft-st'
    date='06-21-2023'
    classifiers = ['relevance','stance','macro-frames','frame-elements']
    df = combine_preds(modelname,classifiers,date)
    df_metadata = pd.read_csv(metadata_file,sep='\t',dtype=str)
    print(df_metadata)
    print(df)
    df = pd.merge(df,df_metadata,on=['tweet_id'])
    print(df)
    df.to_csv(out_file,sep='\t',index=False)
    
    # print(df)
    #load_metadata(metadata_file)
    #load_protest_actors(actor_file)
    

    


if __name__ == '__main__':
    main()
