import pandas as pd 
import numpy as np
import os
import sys
import little_mallet_wrapper as lmw
from scipy.spatial.distance import jensenshannon


def get_topics(topic_input_dir,topic_output_dir,frame,movement=None):
    if movement is not None:
        doc_dist_file = os.path.join(topic_output_dir,frame+'_'+movement,'mallet.topic_distributions.50')
        tweet_ids_file = os.path.join(topic_input_dir,frame+'_'+movement,'tweet_ids.txt')
    else:
        doc_dist_file = os.path.join(topic_output_dir,frame,'mallet.topic_distributions.50')
        tweet_ids_file = os.path.join(topic_input_dir,frame,'tweet_ids.txt')
    df = pd.read_csv(tweet_ids_file,header=None)
    df.columns = ['tweet_id']
    df['topic_dist']=lmw.load_topic_distributions(doc_dist_file)
    return df
    
def load_corpus(corpus_file):
    df = pd.read_csv(corpus_file,sep='\t')
    df = df[['tweet_id','movement','Task2:stance','tweet_type','protest_activity','stakeholder_group']]
    return df


def main():
    corpus_file = '/nfs/turbo/si-juliame/social-movements/full_corpus_with_preds_and_stakeholders_08-02-2023.tsv'
    topic_input_dir = '/nfs/turbo/si-juliame/social-movements/topic_model_data_08-19-2023/'
    topic_output_dir = '/nfs/turbo/si-juliame/social-movements/topic_model_output_08-20-2023/'
    out_dir =  '/nfs/turbo/si-juliame/social-movements/topic_distributions_08-20-2023/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    corpus = load_corpus(corpus_file)
    # for frame in ['motivational','prognostic','diagnostic']:
    #     for movement in ['guns','immigration','lgbtq']:
    #         print(frame,movement)
    #         df = get_topics(topic_input_dir,topic_output_dir,frame,movement=movement)
    #         df = pd.merge(df,corpus,on='tweet_id')
    #         df.to_csv(os.path.join(out_dir,frame+'_'+movement+'.tsv'),sep='\t',index=False)
    
    for frame in ['motivational','prognostic','diagnostic','identify','blame','solution','tactics','solidarity']:
        df = get_topics(topic_input_dir,topic_output_dir,frame,movement=None)
        df = pd.merge(df,corpus,on='tweet_id')
        df.to_csv(os.path.join(out_dir,frame+'.tsv'),sep='\t',index=False)





if __name__ == '__main__':
    main()