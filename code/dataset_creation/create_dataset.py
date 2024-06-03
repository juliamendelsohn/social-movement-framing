import pandas as pd
import os
import string
import pathlib
import re
from collections import defaultdict


#label_col = 'most_frequent_label' or 'movement_stance'
def combine_original_data_and_annotations(data_file,annotation_file,label_col):
    data_df = pd.read_csv(data_file,sep='\t',dtype=str)
    labels_df = pd.read_csv(annotation_file,dtype=str)

    first_df = data_df.merge(labels_df,how='inner',left_on='id_str',right_on='Input.id')
    missing_df = labels_df[labels_df['Input.id'].isin(first_df['Input.id']) == False].copy()

    second_df = missing_df.merge(data_df,left_on='Input.tweet_text',right_on='text')
    df = pd.concat([first_df,second_df],sort=True)
    missing_df = labels_df[labels_df['Input.tweet_text'].isin(df['Input.tweet_text']) == False].copy()

    missing_df['chars'] =  missing_df['Input.tweet_text'].apply(lambda x:re.sub(r'[^#!a-zA-Z0-9 ]+', '', x).strip())
    data_df['chars'] =  data_df['text'].apply(lambda x:re.sub(r'[^#!a-zA-Z0-9 ]+', '', x).strip())
    third_df = missing_df.merge(data_df,on='chars')

    df = pd.concat([df,third_df],sort=True)[['id_str','text',label_col]]
    df.columns = ['id_str','text','label']
    return df


def split_data(df,train_frac,dev_frac,test_frac):
    dfs = {}
    dfs['full'] = df.sample(frac=1).reset_index(drop=True)
    dfs['train'] = df[:int(len(df)*train_frac)]
    dfs['dev'] = df[int(len(df)*train_frac):int(len(df)*(train_frac+dev_frac))]
    dfs['test'] = df[int(len(df)*(train_frac+dev_frac)):]
    return dfs

def get_id_splits(df,train_frac,dev_frac,test_frac):
    ids = df['id_str'].unique().tolist()
    train_ids = ids[:int(len(ids)*train_frac)]
    dev_ids = ids[int(len(ids)*train_frac):int(len(ids)*(train_frac+dev_frac))]
    test_ids = ids[int(len(ids)*(train_frac+dev_frac)):]
    return train_ids,dev_ids,test_ids

def split_data_based_on_id(df,train_ids,dev_ids,test_ids):
    dfs = {}
    dfs['full'] = df[df['id_str'].isin(train_ids+dev_ids+test_ids)]
    dfs['train'] = df[df['id_str'].isin(train_ids)]
    dfs['dev'] = df[df['id_str'].isin(dev_ids)]
    dfs['test'] = df[df['id_str'].isin(test_ids)]
    return dfs

def make_dataset_majority_labels(data_dir,annotation_dir,model_data_dir,issues,splits):
    all_issues_dfs = defaultdict(lambda:defaultdict(int))
    for issue in issues:
        data_file = os.path.join(data_dir,issue+'.tsv')
        annotation_file = os.path.join(annotation_dir,issue+'.csv')
        df = combine_original_data_and_annotations(data_file,annotation_file,'most_frequent_label')
        dfs = split_data(df,0.8,0.1,0.1)
        for split in splits:
            all_issues_dfs[issue][split]= dfs[split]
            dfs[split].to_csv(os.path.join(model_data_dir,f'{issue}_{split}.tsv'),sep='\t',index=False)
    return all_issues_dfs

   
def make_dataset_individual_labels(data_dir,annotation_dir,model_data_dir,issues,splits):
    all_issues_dfs = defaultdict(lambda:defaultdict(int))
    for issue in issues:
        data_file = os.path.join(data_dir,issue+'.tsv')
        annotation_file = os.path.join(annotation_dir,issue+'.csv')
        df = combine_original_data_and_annotations(data_file,annotation_file,'movement_stance')
        train_ids,dev_ids,test_ids = get_id_splits(df,0.8,0.1,0.1)
        dfs = split_data_based_on_id(df,train_ids,dev_ids,test_ids)
        for split in splits:
            all_issues_dfs[issue][split]= dfs[split]
            dfs[split].to_csv(os.path.join(model_data_dir,f'{issue}_{split}.tsv'),sep='\t',index=False)
    return all_issues_dfs



def make_dataset_individual_labels_from_majority_dataset(data_dir,annotation_dir,model_data_dir,issues,splits,majority_all_issues_dfs):
    all_issues_dfs = defaultdict(lambda:defaultdict(int))
    for issue in issues:
        data_file = os.path.join(data_dir,issue+'.tsv')
        annotation_file = os.path.join(annotation_dir,issue+'.csv')
        df = combine_original_data_and_annotations(data_file,annotation_file,'movement_stance')
        for split in splits:
            ids = majority_all_issues_dfs[issue][split]['id_str'].unique()
            all_issues_dfs[issue][split] = df[df['id_str'].isin(ids)]
            df[df['id_str'].isin(ids)].to_csv(os.path.join(model_data_dir,f'{issue}_{split}.tsv'),sep='\t',index=False)
    return all_issues_dfs

def combine_across_issues(model_data_dir,all_issues_dfs,issues,splits):
    for split in splits:
        df =pd.concat([all_issues_dfs[i][split] for i in issues],sort=True)
        df.to_csv(os.path.join(model_data_dir,f'all_issues_{split}.tsv'),sep='\t',index=False)



def main():
    data_dir = '../bozarth-keyword-tweets-sample-for-mturk-ceren-course'
    base_annotation_dir = '../stance_annotations_mturk/annotated_data/'
    base_model_dir = '../stance_data/'
    majority_data_name = 'majority_agreement_50'
    majority_annotation_dir = os.path.join(base_annotation_dir,majority_data_name)

    splits = ['full','train','dev','test']
    issues = ['guns','immigration','lgbtq']

    majority_model_dir = os.path.join(base_model_dir,majority_data_name)
    pathlib.Path(majority_model_dir).mkdir(parents=True,exist_ok=True)
    majority_all_issues_dfs = make_dataset_majority_labels(data_dir,majority_annotation_dir,majority_model_dir,issues,splits)
    combine_across_issues(majority_model_dir,majority_all_issues_dfs,issues,splits)

    for worker_filter in [0,33,50,67]:
        individual_data_name = f'individual_labels_worker_filter_{worker_filter}'
        ind_from_maj = f'individual_labels_from_majority_50_worker_filter_{worker_filter}'
        individual_labels_annotation_dir = os.path.join(base_annotation_dir,individual_data_name)
        
        ind_model_dir = os.path.join(base_model_dir,individual_data_name)
        pathlib.Path(ind_model_dir).mkdir(parents=True,exist_ok=True)
        ind_all_issues_dfs = make_dataset_individual_labels(data_dir,individual_labels_annotation_dir,ind_model_dir,issues,splits)
        combine_across_issues(ind_model_dir,ind_all_issues_dfs,issues,splits)

        ind_from_maj_model_dir = os.path.join(base_model_dir,ind_from_maj)
        pathlib.Path(ind_from_maj_model_dir).mkdir(parents=True,exist_ok=True)
        ind_from_maj_all_issues_dfs = make_dataset_individual_labels_from_majority_dataset(
            data_dir,individual_labels_annotation_dir,ind_from_maj_model_dir,issues,splits,majority_all_issues_dfs)
        combine_across_issues(ind_from_maj_model_dir,ind_from_maj_all_issues_dfs,issues,splits)



    

   

if __name__ == '__main__':
    main()

