from gc import collect
import os
import glob
import gzip
import bz2
import json
import re
from itertools import product
from multiprocessing import Pool
import pandas as pd
from collections import defaultdict
from tweet_utils import collect_tweets_from_file


def get_files(directory,pattern):
	filenames = glob.glob(os.path.join(directory,pattern))
	return filenames

def get_keywords_racial_movement():
	keywords = []
	keywords.append("(black|white|all|blue).?lives.?matter")
	keywords.append("blm")
	keywords.append("sayhername")
	keywords.append("critical.?race.?theory")
	keywords.append("crt")
	keywords.append("it.?s.?oka?y?.?to.?be.?white")
	keywords.append("white.?genocide")
	return keywords

def get_keywords_from_file(keywords_filename):
	df = pd.read_csv(keywords_filename,sep='\t')
	keyword_dict = defaultdict(list)
	for movement in set(df['movement']):
		df_sub = df[df['movement']==movement]
		keywords = list(df_sub['keywords'])
		keyword_dict[movement] = keywords
	return keyword_dict 

def compile_query(keywords):
	query_list = []
	for keyword in keywords:
		new_keyword_list = keyword.split('+')
		new_keyword_list = ['#?' + k for k in new_keyword_list]
		new_keyword = '.?'.join(new_keyword_list)
		new_keyword = '\\b' +  new_keyword + '\\b'
		query_list.append(new_keyword)
	query = '|'.join(query_list)
	return query

def select_files_by_month(decahose_dir,year,month):
	filenames = glob.glob(os.path.join(decahose_dir,str(year),f'decahose.{year}-{str(month).zfill(2)}*.bz2'))
	filenames = sorted(filenames)
	return filenames

def main():
	decahose_dir = '/nfs/locker/twitter-decahose-locker/'
	base_out_dir = '/shared/2/projects/racial-movements/bozarth-keyword-tweets/'
	keywords_file = 'keywords_final.csv'
	keyword_dict = get_keywords_from_file(keywords_file)
	
	data_collection_tuples = []
	data_collection_tuples.append(('immigration',2018,6))
	data_collection_tuples.append(('guns',2018,6))
	data_collection_tuples.append(('lgbtq',2018,6))
	data_collection_tuples.append(('guns',2018,3))
	data_collection_tuples.append(('immigration',2018,7))
	data_collection_tuples.append(('lgbtq',2019,4))

	for (movement,year,month) in data_collection_tuples:
		print(movement,year,month)
		keywords = keyword_dict[movement]
		query = compile_query(keywords)
		out_dir = os.path.join(base_out_dir,f'{movement}_{year}_{str(month).zfill(2)}')
		if not os.path.exists(out_dir):
			os.mkdir(out_dir)
		filenames = select_files_by_month(decahose_dir,year,month)
		print(filenames)
		out_prefix = None
		filters = {}
		filters['exclude_retweets'] = True
		filters['lang'] = 'en' 
		debug_mode=False
		func_tuples = [(f,out_dir,out_prefix,query,filters,debug_mode) for f in filenames]
		pool = Pool(12)
		pool.starmap(collect_tweets_from_file,func_tuples)

	



if __name__ == "__main__":
	main()
