import pandas as pd 
import os 
import tweepy
import csv
import json

auth = tweepy.OAuth2BearerHandler(os.environ['TWITTER_BEARER_TOKEN'])
api = tweepy.API(auth,wait_on_rate_limit=True)


protest_actor_file = '/home/juliame/social-movements/protest_actors_2017-2019.csv'
out_file = '/home/juliame/social-movements/accounts_protest_actors_2017-2019.csv'
out_file_user_objects = '/home/juliame/social-movements/accounts_protest_actors_2017-2019_user_objects.jsonl'
df_actors = pd.read_csv(protest_actor_file)
df_actors = df_actors.drop(columns='Unnamed: 0')
df_actors = df_actors.sort_values(by='date',ascending=False)


with open(out_file_user_objects,'w') as f_obj:
    with open(out_file,'w') as f:
        writer = csv.writer(f)
        for i,row in df_actors.iterrows():
            query = row['actor_list']
            issue = row['issue_list']
            users = api.search_users(query)
            for rank,user in enumerate(users):
                writer.writerow([query,issue,rank,user.id_str,user.screen_name])
                f_obj.write(json.dumps(user._json)+'\n')
