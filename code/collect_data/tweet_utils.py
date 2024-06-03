import os 
import gzip
import bz2
import json
import csv
import re
import glob
from itertools import product
import random 
import sys
from datetime import datetime


def collect_tweets_from_file(filename,out_dir,out_prefix,query,filters):
    (file_basename,file_extension) = os.path.splitext(os.path.basename(filename)) #from twitter-turbo, extension is .bz2
    
    if out_prefix is None or out_prefix == '':
        out_file = os.path.join(out_dir,f'{file_basename}.gz')
    else:
        out_file = os.path.join(out_dir,f'{out_prefix}_{file_basename}.gz')

    if not os.path.exists(filename):
        print(f"Input file does not exist: {filename}")
        return
    
    if os.path.exists(out_file):
        print(f"Output file already exists: {out_file}")
        return
    
    try:
        if file_extension == ".gz":
            print(f"Opening file: {filename}")
            f_in = gzip.open(filename)
        elif file_extension == ".bz2":
            print(f"Opening file: {filename}")
            f_in = bz2.open(filename)
        else: 
            print(f"File extension not supported: {file_extension}")
            return 
        with gzip.open(out_file,'w') as f_out:
            for i,line in enumerate(f_in):
                if i%100000 == 0:
                    print(file_basename,i)
                tweet_obj = load_tweet_obj(line)
                tweet_text = get_tweet_text(tweet_obj)
                if satisfies_filters(tweet_obj,tweet_text,filters):
                    if contains_query(tweet_text,query):
                        print(tweet_text)
                        tweet_string = convert_tweet_object_to_string(tweet_obj)
                        f_out.write(tweet_string)

        bz2.close(filename)
    except:
        print(f"Error in processing file: {filename}")


def contains_query(tweet_text,query):
    return (re.search(query,tweet_text,re.IGNORECASE) != None)


# Can add more filters here (e.g. follower counts, verified status, new users)
def satisfies_filters(tweet_obj,tweet_text,filters):
    if tweet_text is None or len(tweet_text) < 2:
        return False
    if 'exclude_retweets' in filters and filters['exclude_retweets']==True:
        if ('retweeted_status' in tweet_obj) or (tweet_text[:2] == 'RT'):
            return False
    if 'lang' in filters:
        if ('lang' in tweet_obj and tweet_obj['lang']!=filters['lang']):
            return False
    return True




def load_tweet_obj(line):
	return json.loads(line.decode('utf-8').strip())



def get_tweet_text(obj):
	if 'text' not in obj and 'extended_tweet' not in obj:
		return None
	if 'extended_tweet' in obj:
		tweet_text = obj['extended_tweet']['full_text']
	else:
		tweet_text = obj['text']
	return tweet_text.replace('\t',' ').replace('\n',' ').replace('\r',' ') 


def get_metadata(obj):
    metadata = {}
    user_info = obj['user']
    metadata['tweet_id'] = obj['id_str']
    metadata['user_id'] = user_info['id_str']
    metadata['is_verified'] = 1 if user_info['verified']==True else 0
    metadata['followers_count'] = user_info['followers_count']
    metadata['friends_count'] = user_info['friends_count']
    metadata['tweet_count'] = user_info['statuses_count']
    account_creation_date = datetime.strptime(user_info['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
    tweet_creation_date = datetime.strptime(obj['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
    metadata['account_age'] = (tweet_creation_date - account_creation_date).days + 1
    metadata['post_rate'] = metadata['tweet_count'] / metadata['account_age']
    metadata['created_at'] = obj['created_at']
    metadata['is_reply'] = 1 if obj['in_reply_to_status_id_str'] != None else 0
    metadata['is_quote'] = 1 if obj['is_quote_status']==True else 0
    metadata['contains_url'] = 1 if len(get_urls(obj)) > 0 else 0
    metadata['contains_hashtag'] = 1 if len(get_hashtags(obj)) > 0 else 0
    metadata['contains_media'] = 1 if len(get_media(obj)) > 0 else 0
    return metadata


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


def get_media(tweet_obj):
    media_urls = []
    if 'entities' in tweet_obj and 'media' in tweet_obj['entities']:
        for m in tweet_obj['entities']['media']:
            media_urls.append(m['media_url'])
    if 'extended_tweet' in tweet_obj and 'entities' in tweet_obj['extended_tweet']:
        if 'media' in tweet_obj['extended_tweet']['entities']:
            for m in tweet_obj['extended_tweet']['entities']['media']:
                media_urls.append(m['media_url'])
    if 'extended_entities' in tweet_obj and 'media' in tweet_obj['extended_entities']:
        for m in tweet_obj['extended_entities']['media']:
            media_urls.append(m['media_url'])
    return list(set(media_urls))

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


# obj['entities']
# obj['extended_tweet']['entities']
# obj['extended_entities']['']

#entities - media - media_url 
#entities - hashtags - text
#entities - urls - expanded_orl


def convert_tweet_object_to_string(tweet_obj):
	obj_str = json.dumps(tweet_obj) + '\n'
	obj_bytes = obj_str.encode('utf-8')
	return obj_bytes 


def write_tweets(outfile,tweets):
	with gzip.open(outfile,'w') as f:
		for tweet_obj in tweets:
			tweet_string = convert_tweet_object_to_string(tweet_obj)
			f.write(tweet_string)

def write_tweets_text(outfile,tweets):
	with open(outfile,'w') as tsvout:
		writer = csv.writer(tsvout,delimiter='\t')
		for tweet in tweets:
			try:
				tweet_text = get_tweet_text(tweet)
				username = tweet['user']['screen_name']
				id_str = tweet['id_str']
				writer.writerow([username,id_str,tweet_text])
			except:
				continue



#get all usernames from a gz file containing tweet objects
#max_following to restrict to users following fewer than max_following others
def get_usernames(filename,max_following=None):  
	users = []
	with gzip.open(filename) as f:
		for line in enumerate(f):
			obj = load_tweet_obj(line)
			username = obj['user']['screen_name'] 
			if (max_following is None) or (int(obj['user']['friends_count']) <= max_following):
				users.append(username)
	return users

def get_all_usernames(tweet_path,tweet_pattern):
	all_users = set()
	filelist = glob.glob(os.path.join(tweet_path,tweet_pattern))
	for filename in filelist:
		print(filename)
		users = get_usernames(filename)
		all_users = all_users | users
	return list(all_users) 

def write_usernames(users,outfile,shuffle=True):
	if shuffle:
		random.shuffle(users)
	with open(outfile,'w') as f:
		for user in userlist:
			f.write(user + '\n')


FLAGS = re.MULTILINE | re.DOTALL


def remove_stopwords(tokens):
    stopwords_file = '../data/english-stopwords'
    with open(stopwords_file,'r') as f:
        stopwords = set([w.strip('\n') for w in f.readlines()])
        for t in tokens:
            if t not in stopwords:
                new_tokens.append(t)
        return new_tokens



def process_text(tweet_text,keep_hashtag=True,keep_stopwords=True,keep_possessives=True,keep_metatokens=True):
    token_string = tokenize(tweet_text,keep_hashtag) #tokenize
    if keep_possessives == False:
        token_string = re.sub(r"'s\b","",token_string) #removes possessives
    tokens = token_string.split()
    if keep_stopwords == False:
        tokens = remove_stopwords(tokens)

    if keep_metatokens == False:
        tokens = [t for t in tokens if (t[0] !='<' or t[-1] != '>')]  #removes tokens surrounded by brackets

    punctuation = "!\"$%&'()*+, -./:;=?@[\\]^_`{|}~"
    tokens = [t.strip(punctuation) for t in tokens]  #strip punctuation
    tokens = [t for t in tokens if len(t) > 0]
    return tokens


"""
Below this comment is:
Script for tokenizing tweets by Romain Paulus
with small modifications by Jeffrey Pennington
with translation to Python by Motoki Wu
Translation of Ruby script to create features for GloVe vectors for Twitter data.
http://nlp.stanford.edu/projects/glove/preprocess-twitter.rb
"""

def hashtag(text):
    text = text.group()
    hashtag_body = text[1:]
    if hashtag_body.isupper():
        result = " {} ".format(hashtag_body.lower())
    else:
        result = " ".join(["<hashtag>"] + re.split(r"(?=[A-Z])", hashtag_body, flags=FLAGS))
    return result

def allcaps(text):
    text = text.group()
    return text.lower() + " <allcaps>"


def tokenize(text,all_lower=False,remove_hashtag=False):
    # Different regex parts for smiley faces
    #eyes = r"[8:=;]"
    #nose = r"['`\-]?"

    # function so code less repetitive
    def re_sub(pattern, repl):
        return re.sub(pattern, repl, text, flags=FLAGS)

    text = re_sub(r"https?:\/\/\S+\b|www\.(\w+\.)+\S*", "<url>")
    text = re_sub(r"@\w+", "<user>")
    # text = re_sub(r"{}{}[)dD]+|[)dD]+{}{}".format(eyes, nose, nose, eyes), "<smile>")
    # text = re_sub(r"{}{}p+".format(eyes, nose), "<lolface>")
    # text = re_sub(r"{}{}\(+|\)+{}{}".format(eyes, nose, nose, eyes), "<sadface>")
    # text = re_sub(r"{}{}[\/|l*]".format(eyes, nose), "<neutralface>")
    # text = re_sub(r"/"," / ")
    # text = re_sub(r"<3","<heart>")
    #text = re_sub(r"[-+]?[.\d]*[\d]+[:,.\d]*", "<number>")
    #text = re_sub(r"([!?.]){2,}", r"\1 <repeat>")
    #text = re_sub(r"\b(\S*?)(.)\2{2,}\b", r"\1\2 <elong>")

    if remove_hashtag:
        text = re_sub(r"#\S+", hashtag)
    if all_lower:
        text = text.lower()

    return text
    return text.lower()


if __name__ == '__main__':
    _, text = sys.argv
    if text == "test":
        text = "I TEST alllll kinds of #hashtags and #HASHTAGS, @mentions and 3000 (http://t.co/dkfjkdf). w/ <3 :) haha!!!!!"
    tokens = tokenize(text)
    print(tokens)

