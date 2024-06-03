#from simpletransformers.classification import MultiLabelClassificationModel, ClassificationModel
import os
#from ast import literal_eval
import pandas as pd
# import torch
# import argparse
# import logging
# import pathlib
import gzip
import csv
import json
import glob
from iteration_utilities import unique_everseen
from datetime import datetime
# logging.basicConfig(level=logging.INFO)
# transformers_logger = logging.getLogger("transformers")
# transformers_logger.setLevel(logging.WARNING)
# cuda_available = torch.cuda.is_available()

# def load_tweet()


def collect_tweets_from_file(filename):
    all_tweets_from_file = []
    with gzip.open(filename) as f:
        for i,line in enumerate(f):
            info = {}
            tweet_obj = load_tweet_obj(line)
            info['tweet_id'] = tweet_obj['id_str']
            info['text'] = get_tweet_text(tweet_obj)
            info['urls'] = get_urls(tweet_obj)
            info['mentions'] = get_mentions(tweet_obj)
            info['hashtags'] = get_hashtags(tweet_obj)

            user_info = tweet_obj['user']
            info['user_id'] = user_info['id_str']
            info['user_name'] = user_info['name']
            info['screen_name'] = user_info['screen_name']
            info['user_description'] = user_info['description'] 

            info['is_verified'] = 1 if user_info['verified']==True else 0
            info['followers_count'] = user_info['followers_count']
            info['friends_count'] = user_info['friends_count']
            info['tweet_count'] = user_info['statuses_count']

            account_creation_date = datetime.strptime(user_info['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
            tweet_creation_date = datetime.strptime(tweet_obj['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
            info['created_at'] = tweet_creation_date
            info['account_age'] = (tweet_creation_date - account_creation_date).days + 1
            info['post_rate'] = info['tweet_count'] / info['account_age']
            info['is_reply'] = 1 if tweet_obj['in_reply_to_status_id_str'] != None else 0
            info['is_quote'] = 1 if tweet_obj['is_quote_status']==True else 0
            info['num_urls'] = len(info['urls'])
            info['num_mentions'] = len(info['mentions'])
            info['num_hashtags'] = len(info['hashtags'])

            #determine if tweet begins with a mention
            info['begins_with_mention'] = 0
            mention_starts = [m['indices'][0] for m in info['mentions']]
            if len(mention_starts) > 0 and min(mention_starts)==0:
                info['begins_with_mention'] = 1

            info['tweet_type'] = 'broadcast'
            if info['is_quote'] == 1:
                info['tweet_type'] = 'quote'
            elif info['is_reply'] == 1:
                info['tweet_type'] = 'reply'
            elif info['begins_with_mention'] == 1:
                info['tweet_type'] = 'directed'            
            
            for key in info.keys():
                if type(info[key]) == str:
                    info[key] = info[key].replace('\t',' ').replace('\n',' ').replace('\r',' ') 

            all_tweets_from_file.append(info)
    df = pd.DataFrame(all_tweets_from_file)
    return df

def load_tweet_obj(line):
    return json.loads(line.decode('utf-8').strip())



def get_tweet_text(obj):
    if 'text' not in obj and 'extended_tweet' not in obj:
        return None
    if 'extended_tweet' in obj:
        tweet_text = obj['extended_tweet']['full_text']
    else:
        tweet_text = obj['text']
    tweet_text = tweet_text.replace('\t',' ').replace('\n',' ').replace('\r',' ') 
    tweet_text = tweet_text.strip('"')
    return tweet_text

def get_urls(tweet_obj):
    urls = []
    if 'entities' in tweet_obj and 'urls' in tweet_obj['entities']:
        for url in tweet_obj['entities']['urls']:
            urls.append(url['expanded_url'])
    if 'extended_tweet' in tweet_obj and 'entities' in tweet_obj['extended_tweet']:
        if 'urls' in tweet_obj['extended_tweet']['entities']:
            for url in tweet_obj['extended_tweet']['entities']['urls']:
                urls.append(url['expanded_url'])
    if 'extended_entities' in tweet_obj and 'urls' in tweet_obj['extended_entities']:
        for url in tweet_obj['extended_entities']['urls']:
            urls.append(url['expanded_url'])
    return list(set(urls))

def get_mentions(tweet_obj):
    mentions = []
    if 'entities' in tweet_obj and 'user_mentions' in tweet_obj['entities']:
        mentions += tweet_obj['entities']['user_mentions']
    if 'extended_tweet' in tweet_obj and 'entities' in tweet_obj['extended_tweet']:
        if 'user_mentions' in tweet_obj['extended_tweet']['entities']:
            mentions += tweet_obj['extended_tweet']['entities']['user_mentions']
    if 'extended_entities' in tweet_obj and 'user_mentions' in tweet_obj['extended_entities']:
        mentions += tweet_obj['extended_entities']['user_mentions']
    return list(unique_everseen(mentions))


def get_hashtags(tweet_obj):
    hashtags = []
    if 'entities' in tweet_obj and 'hashtags' in tweet_obj['entities']:
        for h in tweet_obj['entities']['hashtags']:
            hashtags.append(h['text'])
    if 'extended_tweet' in tweet_obj and 'entities' in tweet_obj['extended_tweet']:
        if 'hashtags' in tweet_obj['extended_tweet']['entities']:
            for h in tweet_obj['extended_tweet']['entities']['hashtags']:
                hashtags.append(h['text'])
    if 'extended_entities' in tweet_obj and 'hashtags' in tweet_obj['extended_entities']:
        for h in tweet_obj['extended_entities']['hashtags']:
            hashtags.append(h['text'])
    return list(set(hashtags))





def main():
    data_dir = '/nfs/turbo/si-juliame/social-movements/bozarth-keyword-tweets/'
    date = '08-02-2023'
    out_file = f'/nfs/turbo/si-juliame/social-movements/full_corpus_{date}.tsv'
    movements = ['guns','immigration','lgbtq']

    months = {}
    months['guns'] = {}
    months['immigration'] = {}
    months['lgbtq'] = {}
    months['guns']['high'] = '2018_03'
    months['guns']['avg'] = '2018_06'
    months['immigration']['high'] = '2018_06'
    months['immigration']['avg'] = '2018_07'
    months['lgbtq']['high'] = '2018_06'
    months['lgbtq']['avg'] = '2019_04'

    all_dfs = []
    for movement in movements:
        movement_data_dir = os.path.join(data_dir,movement)
        for protest_activity in months[movement]:
            month = months[movement][protest_activity]
            month_data_dir = os.path.join(movement_data_dir,f'{movement}_{month}')
            files = glob.glob(os.path.join(month_data_dir,'*.gz'))
            for filename in files:
                print(movement,month,filename)
                df = collect_tweets_from_file(filename)
                df['movement'] = movement
                df['month'] = month
                df['protest_activity'] = protest_activity
                df['filename'] = filename
                all_dfs.append(df)
                
    df = pd.concat(all_dfs)
    print(df)
    df.to_csv(out_file,sep='\t',index=False)


    
if __name__ == '__main__':
    main()
