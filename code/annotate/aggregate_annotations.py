import os
import sys
import argparse
import pandas as pd
import glob
import numpy as np
from collections import defaultdict


def get_stance_from_label(label):
    if 'gun-control' in label:
        return 'pro'
    if 'gun-right' in label:
        return 'anti'
    if 'pro-immigration' in label:
        return 'pro'
    if 'anti-immigration' in label:
        return 'anti'
    if 'supports-lgbtq' in label:
        return 'pro'
    if 'opposes' in label:
        return 'anti'
    if 'neutral' in label:
        return 'neutral/unclear'

def load_annotations(annotations_dir,filename):
    df = pd.read_csv(os.path.join(annotations_dir,filename))
    df['Empty Id'] = None
    input_id_options = ['Input.id','Input.tweet_id','Input.tweetid']
    input_text_options = ['Input.tweet','Input.tweet_text','Input.text','Input.comment']
    input_id_list = list(set(input_id_options).intersection(set(df.columns)))
    input_text = list(set(input_text_options).intersection(set(df.columns)))[0]
    df['Input.tweet_text'] = df[input_text]
    if len(input_id_list) > 0:
        input_id = input_id_list[0]
        df['Input.id'] = df[input_id].astype(str)
    else:
        df['Input.id'] = 'No Id Provided'
    
    input_cols = ['Input.id','Input.tweet_text','WorkerId','WorkTimeInSeconds']
    output_cols = [x for x in df.columns if x.startswith('Answer') and not x.startswith('Answer.target')][:3]
    df['response'] = df[output_cols].idxmax(axis=1) 
    df['movement_stance'] = df['response'].apply(lambda x: get_stance_from_label(x))
    df_sub = df[input_cols+['response','movement_stance']]
    return df_sub

def write_all_annotations(annotations_dir,files,issues,out_dir):
    for issue in issues:
        all_issue_dfs = []
        for f in files:
            if f.startswith(issue):
                df = load_annotations(annotations_dir,f)
                all_issue_dfs.append(df)
        df_issue = pd.concat(all_issue_dfs)
        df_issue.to_csv(os.path.join(out_dir,issue+'.csv'),index=False)


def main():
    annotations_dir = '../stance_annotations_mturk/mturk_results/per_team/'
    out_dir = '../stance_annotations_mturk/mturk_results/aggregated/'
    if os.path.exists(out_dir) == False:
        os.mkdir(out_dir)
    files = [f for f in os.listdir(annotations_dir) if f.endswith('.csv')]
    issues = ['guns','immigration','lgbtq']
    write_all_annotations(annotations_dir,files,issues,out_dir)
    


if __name__ == '__main__':
    main()





