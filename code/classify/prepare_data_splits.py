import os
import pandas as pd 
import numpy as np
import glob
import pathlib
import json
import csv
from sklearn.model_selection import KFold


def contains_diagnostic(s):
    if s['Task3:identify'] == 'yes' or s['Task3:blame'] == 'yes':
        return 'yes'
    else:
        return 'no'


def contains_prognostic(s):
    if s['Task4:solution']=='yes':
        return 'yes'
    elif s['Task4:tactics']=='yes':
        return 'yes'
    elif s['Task4:solidarity']=='yes':
        return 'yes'
    elif s['Task4:counter']=='yes':
        return 'yes'
    return 'no'


def aggregate_annotated_data(annotated_data_dir):
    annotated_data_files = glob.glob(os.path.join(annotated_data_dir, '*.tsv'))
    dfs = []
    for filename in annotated_data_files:
        df = pd.read_csv(filename,sep='\t',dtype=str,quoting=csv.QUOTE_NONE)
        df.columns = [x.replace(' ','') for x in df.columns]
        df = df[[x for x in df.columns if not x.startswith('Unnamed')]]
        if 'Notes' in df.columns:
            df = df.drop(columns=['Notes'])
        dfs.append(df)
    df = pd.concat(dfs)
    df['Task3:diagnostic'] = df.apply(contains_diagnostic,axis=1)
    df['Task4:prognostic'] = df.apply(contains_prognostic,axis=1)
    df = df.sample(frac=1,random_state=42)
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



def add_labels_as_list(df):
    tasks = [x for x in df.columns if x.startswith('Task')]
    df['labels'] = df[tasks].values.tolist()
    return df

def convert_to_binary(df):
    tasks = [x for x in df.columns if x.startswith('Task')]
    ix_to_task = {i:task for i,task in enumerate(tasks)}
    label_to_class = {'no':0,'yes':1,'anti':0,'neutral/unclear':1,'pro':2}
    df= df.replace(label_to_class)
    return df, ix_to_task, label_to_class

def make_data_splits(df,out_dir,train_frac,test_frac,num_folds=5):
    df = df.sample(frac=1).reset_index(drop=True)
    num_train = int(len(df)*train_frac)
    kf = KFold(n_splits=num_folds, random_state=42, shuffle=True)
    train_data = df[:num_train]
    test_data = df[num_train:]
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    train_data.to_csv(os.path.join(out_dir,'train_full.tsv'),sep='\t',index=False)
    test_data.to_csv(os.path.join(out_dir,'test_full.tsv'),sep='\t',index=False)
    print(len(train_data),len(test_data))
    for i,fold in enumerate(kf.split(train_data)):
        train_index, val_index = fold
        train_df = train_data.iloc[train_index]
        val_df = train_data.iloc[val_index]
        pathlib.Path(os.path.join(out_dir,'fold_{}'.format(i))).mkdir(parents=True, exist_ok=True)
        train_df.to_csv(os.path.join(out_dir,'fold_{}'.format(i),'train_full.tsv'),sep='\t',index=False)
        val_df.to_csv(os.path.join(out_dir,'fold_{}'.format(i),'dev_full.tsv'),sep='\t',index=False)
        print(i,len(train_df),len(val_df))


#Subset full data to only include relevant data
def add_relevant_data_subsets(data_split_dir):
    data_split_files = glob.glob(os.path.join(data_split_dir, '*_full.tsv')) + glob.glob(os.path.join(data_split_dir, '*','*_full.tsv'))
    for filename in data_split_files:
        df = pd.read_csv(filename,sep='\t',quoting=csv.QUOTE_NONE)
        df_relevant = df[df['Task1:relevance'] == 1]
        df_relevant = df_relevant.drop(columns=['Task1:relevance'])
        new_filename = filename.replace('_full.tsv','_relevant.tsv')
        df_relevant.to_csv(new_filename,sep='\t',index=False)
        print(new_filename,len(df_relevant))

def add_movement_data_subsets(data_split_dir,starting_subset='relevant'): #starting_subset can be 'relevant' or 'full'
    data_split_files = glob.glob(os.path.join(data_split_dir, f'*_{starting_subset}.tsv')) + glob.glob(os.path.join(data_split_dir, '*',f'*_{starting_subset}.tsv'))
    for filename in data_split_files:
        df = pd.read_csv(filename,sep='\t',quoting=csv.QUOTE_NONE)
        movements = list(df['movement'].unique())
        for movement in movements:
            df_movement = df[df['movement'] == movement]
            new_filename = filename.replace(f'_{starting_subset}.tsv',f'_{starting_subset}_{movement}.tsv')
            df_movement = df_movement.drop(columns=['movement'])
            df_movement.to_csv(new_filename,sep='\t',index=False)
            print(new_filename,len(df_movement))
            
def add_stance_data_subsets(data_split_dir,starting_subset='relevant'): #starting_subset can be 'relevant' or 'full' or 'relevant_<MOVEMENT>'
    data_split_files = glob.glob(os.path.join(data_split_dir, f'*_{starting_subset}.tsv')) + glob.glob(os.path.join(data_split_dir, '*',f'*_{starting_subset}.tsv'))
    for filename in data_split_files:
        df = pd.read_csv(filename,sep='\t',quoting=csv.QUOTE_NONE)
        stances = list(df['Task2:stance'].unique())
        for stance in stances:
            if stance==0:
                s = 'anti'
            elif stance==1:
                s = 'neutral'
            elif stance==2:
                s = 'pro'
            df_stance = df[df['Task2:stance'] == stance]
            new_filename = filename.replace(f'_{starting_subset}.tsv',f'_{starting_subset}_{s}.tsv')
            print(new_filename,len(df_stance))
            df_stance.to_csv(new_filename,sep='\t',index=False)
    



def get_movement_splits(df,out_dir,movement_col,ix_to_task):
    # Create splits for each movement
    # Create splits that leave one movement out
    movements = df[movement_col].unique()
    for movement in movements:
        df_with_movement = df[df[movement_col] == movement].sample(frac=1).reset_index(drop=True)
        df_without_movement = df[df[movement_col] != movement].sample(frac=1).reset_index(drop=True)
        df_with_movement.to_csv(os.path.join(out_dir,f'{movement}.tsv'),sep='\t',index=False)
        df_without_movement.to_csv(os.path.join(out_dir,f'leave_out_{movement}.tsv'),sep='\t',index=False)
    with open(os.path.join(out_dir,'ix_to_task.json'),'w') as f:
        json.dump(ix_to_task,f)
    



def main():
    date = '06-21-2023'
    train_frac = 0.8
    test_frac = 0.2
    base_dir = '/home/juliame/social-movements/annotated_data'
    annotated_data_dir = os.path.join(base_dir,'all_annotated_chunks')
    # data_split_dir = os.path.join(base_dir,f'data_frac_splits/{date}_{train_frac}train_{dev_frac}dev_{test_frac}test/')
    # movement_split_dir = os.path.join(base_dir,f'movement_splits/{date}/')
    # pathlib.Path(data_split_dir).mkdir(parents=True, exist_ok=True)
    # pathlib.Path(movement_split_dir).mkdir(parents=True, exist_ok=True)
    all_data = aggregate_annotated_data(annotated_data_dir)
    all_data,ix_to_task,labels_to_class = convert_to_binary(all_data)
    print(all_data)
    print(ix_to_task)
    print(labels_to_class)
    out_dir = os.path.join(base_dir,f'data_splits_{date}')
    make_data_splits(all_data,out_dir,train_frac,test_frac,num_folds=5)
    add_relevant_data_subsets(out_dir)
    add_movement_data_subsets(out_dir,starting_subset='relevant')
    add_movement_data_subsets(out_dir,starting_subset='full')
    add_stance_data_subsets(out_dir,starting_subset='relevant')
    add_stance_data_subsets(out_dir,starting_subset='relevant_guns')
    add_stance_data_subsets(out_dir,starting_subset='relevant_lgbtq')
    add_stance_data_subsets(out_dir,starting_subset='relevant_immigration')




if __name__ == "__main__":
    main()