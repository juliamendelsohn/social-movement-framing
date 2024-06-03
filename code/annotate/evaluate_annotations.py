import os
import pandas as pd
from collections import defaultdict,Counter
import pathlib
import simpledorff



def load_annotations(annotations_dir,issues):
    dfs = []
    for issue in issues:
        df = pd.read_csv(os.path.join(annotations_dir,issue+'.csv'))
        df['Issue'] = issue
        dfs.append(df)
    return pd.concat(dfs)

def get_issue_subsets(df,issue='all'):
    if issue == 'all':
        return df
    else:
        return df[df['Issue'] == issue]

def get_unique_annotation_counts(df,issues,results_dir):
    stats = {}
    stats['num_tweets'] = {}
    stats['num_annotations'] = {}
    stats['max_annotations_per_tweet'] = {}
    stats['min_annotations_per_tweet'] = {}
    stats['average_annotations_per_tweet'] = {}
    for issue in issues+['all']:
        df_issue = get_issue_subsets(df,issue)
        df_counts = df_issue.groupby(by='Input.tweet_text').agg('count').reset_index()
        stats['num_tweets'][issue] = len(df_counts)
        stats['num_annotations'][issue] = df_counts['Issue'].sum()
        stats['max_annotations_per_tweet'][issue] = df_counts['Issue'].max()
        stats['min_annotations_per_tweet'][issue] = df_counts['Issue'].min()
        stats['average_annotations_per_tweet'][issue] = df_counts['Issue'].mean()
    pd.DataFrame(stats).to_csv(os.path.join(results_dir,'annotation_stats.csv'))

def get_most_frequent_item(l):
    return Counter(l).most_common(1)[0][0]

def get_label_agreement(l):
    return Counter(l).most_common(1)[0][1]/len(l)

def get_annotation_distributions(df,issues,results_dir):
    all_agreement_stats = {}
    for issue in issues+['all']:
        df_issue = get_issue_subsets(df,issue)
        df_issue_labels = df_issue.groupby(by='Input.tweet_text')['movement_stance'].apply(list).reset_index()
        df_issue_labels['most_frequent_label'] = df_issue_labels['movement_stance'].apply(get_most_frequent_item)
        df_issue_labels['label_agreement'] = df_issue_labels['movement_stance'].apply(get_label_agreement)
        agreement_stats = {}
        agreement_stats['num_perfect_agreement'] = len(df_issue_labels[df_issue_labels['label_agreement'] == 1])
        agreement_stats['num_majority_agreement'] = len(df_issue_labels[df_issue_labels['label_agreement'] >= 0.5])
        agreement_stats['num_minority_agreement'] = len(df_issue_labels[df_issue_labels['label_agreement'] < 0.5])
        agreement_stats['percent_perfect_agreement'] = agreement_stats['num_perfect_agreement'] / len(df_issue_labels)
        agreement_stats['percent_majority_agreement'] = agreement_stats['num_majority_agreement'] / len(df_issue_labels)
        agreement_stats['percent_minority_agreement'] = agreement_stats['num_minority_agreement'] / len(df_issue_labels)
        all_agreement_stats[issue] = agreement_stats
    pd.DataFrame(all_agreement_stats).to_csv(os.path.join(results_dir,'agreement_percentages.csv'))

def write_text_and_labels(df,issues,majority_threshold,data_dir):
    for issue in issues:
        df_issue = get_issue_subsets(df,issue)
        df_issue_labels = df_issue.groupby(by=['Input.id','Input.tweet_text'])['movement_stance'].apply(list).reset_index()
        df_issue_labels['most_frequent_label'] = df_issue_labels['movement_stance'].apply(get_most_frequent_item)
        df_issue_labels['label_agreement'] = df_issue_labels['movement_stance'].apply(get_label_agreement)
        df_issue_labels_perfect = df_issue_labels[df_issue_labels['label_agreement'] == 1]
        df_issue_labels_majority = df_issue_labels[df_issue_labels['label_agreement'] >= majority_threshold]
        pathlib.Path(os.path.join(data_dir,'perfect_agreement')).mkdir(parents=True,exist_ok=True)
        pathlib.Path(os.path.join(data_dir,'majority_agreement')).mkdir(parents=True,exist_ok=True)
        df_issue_labels_perfect.to_csv(os.path.join(data_dir,'perfect_agreement',issue+'.csv'))
        thresh_percent = int(majority_threshold*100)
        pathlib.Path(os.path.join(data_dir,f'majority_agreement_{thresh_percent}')).mkdir(parents=True,exist_ok=True)
        df_issue_labels_majority.to_csv(os.path.join(data_dir,f'majority_agreement_{thresh_percent}',issue+'.csv'))
    
def get_subset_with_majority_labels(df,threshold):
    df_labels = df.groupby(by='Input.tweet_text')['movement_stance'].apply(list).reset_index()
    df_labels['most_frequent_label'] = df_labels['movement_stance'].apply(get_most_frequent_item)
    df_labels['label_agreement'] = df_labels['movement_stance'].apply(get_label_agreement)
    df_labels_majority = df_labels[df_labels['label_agreement'] >= threshold]
    return df[df['Input.tweet_text'].isin(df_labels_majority['Input.tweet_text'])]


def calculate_krippendorff(df,issues,results_dir):
    alphas = defaultdict(lambda: defaultdict(float))
    for issue in issues+['all']:
        df_issue = get_issue_subsets(df,issue)
        alphas[issue]['full'] = simpledorff.calculate_krippendorffs_alpha_for_df(df_issue,experiment_col='Input.tweet_text',
                                                 annotator_col='WorkerId',class_col='movement_stance')
        for threshold in [0.5,0.6,0.7,0.8,0.9,1.0]:
            df_issue_majority = get_subset_with_majority_labels(df_issue,threshold)
            alphas[issue][threshold] = simpledorff.calculate_krippendorffs_alpha_for_df(df_issue_majority,
                                    experiment_col='Input.tweet_text', annotator_col='WorkerId',class_col='movement_stance')
    pd.DataFrame(alphas).to_csv(os.path.join(results_dir,'krippendorff_alphas.csv'))




def main():
    annotations_dir = '../stance_annotations_mturk/mturk_results/aggregated/'
    results_dir = '../stance_annotations_mturk/mturk_results/annotation_eval/'
    data_dir = '../stance_annotations_mturk/annotated_data/'
    pathlib.Path(results_dir).mkdir(parents=True, exist_ok=True) 
    pathlib.Path(data_dir).mkdir(parents=True,exist_ok=True)
    issues = ['guns','immigration','lgbtq']
    df = load_annotations(annotations_dir,issues)
    # get_unique_annotation_counts(df,issues,results_dir)
    # get_annotation_distributions(df,issues,results_dir)
    for threshold in [0.5,0.6,0.7,0.8,0.9,1.0]:
        print(threshold)
        write_text_and_labels(df,issues,threshold,data_dir)
    #write_text_and_labels(df,issues,data_dir)
    #calculate_krippendorff(df,issues,results_dir)
    



if __name__ == "__main__":
    main()