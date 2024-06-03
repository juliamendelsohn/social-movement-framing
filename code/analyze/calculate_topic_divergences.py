import os 
import sys
from ast import literal_eval
import pandas as pd
from scipy.spatial.distance import jensenshannon
import numpy as np
from itertools import combinations

sample_size=100
num_samples = 100 

def average_topic_vector(df):
    vecs = np.array(df['topic_dist'].tolist())
    mean = np.mean(vecs,axis=0)
    return mean

def get_top_topics(df):
    mean_vec = average_topic_vector(df)
    top_topics = np.argsort(mean_vec)[::-1][:5]
    return top_topics

def bootstrap_divergence(df1, df2, num_samples, sample_size):
    divergences = []
    for i in range(num_samples):
        sample1 = df1.sample(sample_size,replace=True)
        sample2 = df2.sample(sample_size,replace=True)
        div = jensenshannon(average_topic_vector(sample1),average_topic_vector(sample2))
        divergences.append(div)
    # Calculate mean, std, and 95% CI
    mean = np.mean(divergences)
    std = np.std(divergences)


def get_movement_divergences(df,num_samples,sample_size):
    movements = df['movement'].unique()
    movement_divergences = []
    for movement_pair in combinations(movements,2):
        movement1 = movement_pair[0]
        movement2 = movement_pair[1]
        df1 = df[df['movement']==movement1]
        df2 = df[df['movement']==movement2]
        divergences = bootstrap_divergence(df1,df2,num_samples,sample_size)




def main():

    topic_dist_dir = '/nfs/turbo/si-juliame/social-movements/topic_distributions_08-20-2023/'
    df = pd.read_csv(os.path.join(topic_dist_dir,'motivational.tsv'),sep='\t')
    df['topic_dist'] = df['topic_dist'].apply(literal_eval)
    #np.mean(a['vec'].tolist(),axis=1)
    smo_vecs = np.array(df[df['stakeholder_group']=='smo']['topic_dist'].tolist())
    smo_mean = np.mean(smo_vecs,axis=0)

    journo_vecs = np.array(df[df['stakeholder_group']=='journalist']['topic_dist'].tolist())
    journo_mean = np.mean(journo_vecs,axis=0)


    print(df)
    print(smo_vecs[:10])
    divergence = jensenshannon(smo_mean,journo_mean)
    print(divergence)


if __name__ == '__main__':
    main()


