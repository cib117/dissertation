# -*- coding: utf-8 -*-

## import required packages
import pandas as pd
import numpy as np
import nltk
import preprocessor
import re
import unicodedata

## function to clean text of tweets
def clean_tweet_text(t):
    """Clean up text for analysis

    Keyword arguments:
    t -- text string to clean
    
    Returns:
    day -- cleaned text string
    """
    try:
        t = t.replace('http://t.co/9TP7UUrMtU(alteration-of-cri/index.xml', ' ') # improper link causes preprocessor to fail
        t = preprocessor.clean(t)
        t = unicodedata.normalize('NFD', t).encode('ascii', 'ignore') # normalize unicode accents etc
        t = re.sub('[^a-zA-Z \']', ' ', t) # only keep letters, ', and - characterst = t.lower()
        t = t.lower() # lower case everything
        t = ' '.join(t.split())
    except (AttributeError, TypeError):
        t = ' '
    return t

# Subset data
df  = pd.read_csv('data/json_tweets.txt', header=None, quoting=3)
df.columns = ['handle', 'name', 'date', 'reply', 'retweet', 'rtwts', 'favs', 'text']

# Subset dataframe by relevant date and exclude retweets and replies
df = df[(df['retweet'] == False) & (df['reply'] == False) & (df['date'] < 20160204) & (df['date'] > 20110307)]

# Get and clean text of tweets
names = df['name'].tolist()
dates = df['date'].tolist()
text = df['text'].tolist()
cleantxt = [clean_tweet_text(twt) for twt in text]

    
# Write tweets
out = open('data/tweetstext.txt', 'w')
for item in cleantxt:
  out.write("%s\n" % item)
# Write tweet details
out = open('data/tweetsdetails.txt', 'w')
for n,d in zip(names, dates):
    out.write(str(n)+','+str(d)+'\n')