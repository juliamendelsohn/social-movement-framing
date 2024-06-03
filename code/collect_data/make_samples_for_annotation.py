import os 
import glob
import csv 
import json
import gzip
import random
from tweet_utils import load_tweet_obj,get_tweet_text


def load_tweets_from_dir(directory):
    all_tweets = []
    files = glob.glob(os.path.join(directory,'*.gz'))
    for fname in files:
        with gzip.open(fname,'r') as f:
            for line in f:
                all_tweets.append(line)
    return all_tweets

def get_sample_tweets(all_tweets,n=20000):
    sample = random.sample(all_tweets,n)
    return sample

def write_sample_to_file(sample_tweets,out_dir,movement):
    with open(os.path.join(out_dir,f'{movement}.tsv'),'w') as f:
        writer = csv.writer(f,delimiter='\t')
        writer.writerow(["created_at","id_str", "text"])
        for tweet in sample_tweets:
            tweet_obj = load_tweet_obj(tweet)
            writer.writerow([tweet_obj['created_at'],tweet_obj['id_str'],get_tweet_text(tweet_obj)])
    # with open(os.path.join(out_dir,f'{movement}.jsonl'),'w') as f:
    #     for tweet in sample_tweets:
    #         f.write(tweet.decode('utf-8'))


def main():
    base_dir = '/nfs/turbo/si-juliame/social-movements/bozarth-keyword-tweets/'
    out_dir = '/nfs/turbo/si-juliame/social-movements/annotation-sample-bozarth-keyword-tweets/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    for movement in ['guns','immigration','lgbtq']:
        movement_dir = os.path.join(base_dir,movement)
        movement_months = [d for d in os.listdir(movement_dir) if d.startswith(movement)]
        for movement_month in movement_months:
            directory = os.path.join(movement_dir,movement_month)
            print(directory, movement, movement_month)
            all_tweets = load_tweets_from_dir(directory)
            print(directory,len(all_tweets))
            sample_tweets = get_sample_tweets(all_tweets,n=20000)
            write_sample_to_file(sample_tweets,out_dir,movement_month)



if __name__ == "__main__":
    main()
