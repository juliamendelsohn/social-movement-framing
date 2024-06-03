import os
import pandas as pd 
import numpy as np
import glob
import pathlib
import json
from ast import literal_eval

def process_augmented_data(filename):
    df = pd.read_csv(filename,sep='\t',dtype=str)
    df.columns = [x.replace(' ','') for x in df.columns]
    df = df[[x for x in df.columns if not x.startswith('Unnamed')]]
    if 'Notes' in df.columns:
        df = df.drop(columns=['Notes'])
    return df


def replace_stance_labels(df):
    tasks = [x for x in df.columns if x.startswith('Task') and x != 'Task2:stance']
    other_cols = [x for x in df.columns if not x.startswith('Task')]
    tasks = tasks[:1] + ['Task2:stance-pro','Task2:stance-neutral','Task2:stance-anti'] + tasks[1:]

    stance_col = df['Task2:stance']
    df['Task2:stance-pro'] = stance_col.replace(['anti','neutral/unclear','pro'],['no','no','yes'])
    df['Task2:stance-neutral'] = stance_col.replace(['anti','neutral/unclear','pro'],['no','yes','no'])
    df['Task2:stance-anti'] = stance_col.replace(['anti','neutral/unclear','pro'],['yes','no','no'])
    return df[other_cols+tasks]



def convert_to_binary(df):
    tasks = [x for x in df.columns if x.startswith('Task')]
    print(tasks)
    ix_to_task = {i:task for i,task in enumerate(tasks)}
    print(ix_to_task)
    other_cols = [x for x in df.columns if not x.startswith('Task')]
    df = df.replace(['no','yes'],[0,1])
    #replace non-numeric values in df with 0
    for col in tasks:
        df[col] = pd.to_numeric(df[col],errors='coerce').fillna(0).astype(int)

    df = df.replace()
    df['labels'] = df[tasks].values.tolist()
    return df[other_cols + ['labels']], ix_to_task


def load_training_data(filename):
    df = pd.read_csv(filename,sep='\t',converters={"labels": literal_eval})
    return df



def main():
    date = '04-12-2023'
    train_frac = 0.8
    dev_frac = 0
    test_frac = 0.2
    base_dir = '/home/juliame/social-movements/annotated_data'
    consensus_dir = os.path.join(base_dir,'consensus')
    data_split_dir = os.path.join(base_dir,f'data_frac_splits/{date}_{train_frac}train_{dev_frac}dev_{test_frac}test/')

    train_dir = '/home/juliame/social-movements/annotated_data/data_frac_splits/04-12-2023_0.8train_0dev_0.2test/'
    train_file = os.path.join(train_dir,'train.tsv')
    augment_file = '/home/juliame/social-movements/augmented_data/chatgpt_labels_04-12-2023.tsv'
    out_file = os.path.join(train_dir,'train_augmented.tsv')

    df_augment = process_augmented_data(augment_file)
    df_augment = replace_stance_labels(df_augment)
    df_augment,ix_to_task = convert_to_binary(df_augment)
    df_train = load_training_data(train_file)
    df = pd.concat([df_train,df_augment]).sample(frac=1)
    df.to_csv(out_file,sep='\t',index=False)



if __name__ == "__main__":
    main()