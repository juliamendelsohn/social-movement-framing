# -*- coding: utf-8 -*-

import re
import os 
import pyspark
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext, SparkSession
from pyspark.sql.functions import udf, col, collect_list, lit, array 
from datetime import datetime
import functools
import numpy as np
from pyspark.sql import functions as F 
from itertools import chain
import glob

# conf = SparkConf().setAppName('extractTweets')
# conf.set("spark.sql.files.ignoreCorruptFiles","true")
# conf.set("spark.driver.maxResultSize","0")
# sc = SparkContext(conf=conf)
# sqlContext = SQLContext(sc)
spark = SparkSession.builder.appName('extractTweets').getOrCreate()
#spark.sqlContext.setConf("spark.sql.files.ignoreCorruptFiles", "true")
#spark.set("spark.driver.maxResultSize","0")

jvm = spark._jvm
jsc = spark._jsc
fs = jvm.org.apache.hadoop.fs.FileSystem.get(jsc.hadoopConfiguration())


def fun(texts):
  keywords = []
  keywords.append("(black|white|all|blue).?lives.?matter")
  keywords.append("blm")
  keywords.append("sayhername")
  keywords.append("critical.?race.?theory")
  keywords.append("crt")
  keywords.append("it.?s.?oka?y?.?to.?be.?white")
  keywords.append("white.?genocide")
  query_list = ['\\b' + keyword + '\\b' for keyword in keywords]
  query = '|'.join(query_list)
  for text in texts:
    if text != None and re.search(query,text,re.IGNORECASE):
      return True
  return False

text_udf = udf(fun)


all_files = glob.glob("/hadoop-fuse/user/juliame/raw/*.bz2")


for filename in all_files:
  hdfs_file = '/'.join(filename.split('/')[-2:]) 
  out_dir = os.path.join('relevant_tweets',os.path.splitext(os.path.basename(filename))[0])

  if fs.exists(jvm.org.apache.hadoop.fs.Path(out_dir)):
    print("Path already exists: " + out_dir)
  else:
    try:
      df = spark.read.json(hdfs_file)
      df = df.withColumn('keywords_present', text_udf(array('text','extended_tweet.full_text')))
      df = df.filter(df['keywords_present']==True)
      df = df.filter(df['lang']=='en')
      df = df.filter(df.retweeted_status.isNull())
      df.write.option("compression", "gzip").json(out_dir)
    except:
      continue


