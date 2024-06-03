import os
import pandas as pd
from collections import defaultdict,Counter
import pathlib



def get_most_frequent_item(l):
    return Counter(l).most_common(1)[0][0]

def get_label_agreement(l):
    return Counter(l).most_common(1)[0][1]/len(l)

def get_worker_agreement_with_majority(row):
    if row['movement_stance'] == row['most_frequent_label'] and row['label_agreement']>=0.5:
        return "yes"
    elif row['movement_stance'] != row['most_frequent_label'] and row['label_agreement']>=0.5:
        return "no"
    else:
        return "no majority"

def get_majority_label_per_tweet(df):
    df_labels = df.groupby(by=['Input.id','Input.tweet_text'])['movement_stance'].apply(list).reset_index()
    df_labels['most_frequent_label'] = df_labels['movement_stance'].apply(get_most_frequent_item)
    df_labels['label_agreement'] = df_labels['movement_stance'].apply(get_label_agreement)
    df_labels = df_labels.rename(columns={'movement_stance': 'all_annotations'})
    df = df.merge(df_labels,on=['Input.id','Input.tweet_text'])
    df['agrees_with_majority'] = df.apply(lambda row: get_worker_agreement_with_majority(row), axis=1)
    return df



def get_disagreement_by_worker(df):
    #For each worker, get the number of times they disagreed with the majority
    #Get total number of HITs for each worker
    #Get number of times they disagreed with the majority
    df_by_worker = df.groupby(by=['WorkerId'])['agrees_with_majority'].apply(list).reset_index()
    df_by_worker['num_hits'] = df_by_worker['agrees_with_majority'].apply(lambda x: len(x))
    df_by_worker['percent_agreement_with_majority'] = df_by_worker['agrees_with_majority'].apply(
        lambda x: (x.count('yes') + x.count('no majority'))/len(x))
    df = df.merge(df_by_worker[['WorkerId', 'num_hits','percent_agreement_with_majority']],on=['WorkerId'])
    return df


def main():
    issues = ['guns','immigration','lgbtq']
    annotation_dir = '../stance_annotations_mturk/mturk_results/aggregated/'
    out_dir = '../stance_annotations_mturk/mturk_results/aggregated_with_worker_info/'
    pathlib.Path(out_dir).mkdir(parents=True,exist_ok=True)
    
    for issue in issues:
        fname = os.path.join(annotation_dir,issue+'.csv')
        df = pd.read_csv(fname)
        df_with_majority_label = get_majority_label_per_tweet(df)
        df_with_worker_info = get_disagreement_by_worker(df_with_majority_label)
        df_with_worker_info.to_csv(os.path.join(out_dir,issue+'.csv'),index=False)


if __name__ == '__main__':
    main()
