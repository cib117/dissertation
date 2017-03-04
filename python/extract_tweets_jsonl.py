import json
import time
import glob
import pandas as pd

def normalize_name(text):
    """
    Function to pull out handle from file name
    
    Keyword argument:
    text -- text of jsonl filename
    """
    name = text.replace('.jsonl', '')
    name = name.replace('tweets/', '')
    return name
    
def clean_text(text):
    """
    Function to do basic cleaning on text of tweet
    
    Keyword argument:
    text -- text of tweet
    
    Returns:
    text -- text of tweet with commas, extra white space removed
    """
    text = str(text.encode('utf8'))
    text = text.replace(',', '')
    return " ".join(text.split())

def check_reply(tweet):
    """
    Function to determine whether a tweet is a reply or not
    
    Keyword argument:
    tweet -- tweet dictionary as returned by api
    
    Returns:
    reply -- indicator denoting whether tweet is a reply or not
    """
    if str(tweet['in_reply_to_status_id']) == 'None':
        reply = 'false'
    else:
        reply = 'true'
    return reply

def check_retweet(tweet):
    """
    Function to determine whether a tweet is a reply or not
    
    Keyword argument:
    tweet -- tweet dictionary as returned by api
    
    Returns:
    reply -- indicator denoting whether tweet is a retweet or not
    """
    if 'retweeted_status' in str(tweet):
        retweet = 'true'
    else:
        retweet = 'false'
    return retweet

def get_time(tweet):
    """
    Function to extract the date of tweet in Ymd format
    
    Keyword argument:
    tweet -- tweet dictionary as returned by api
    """
    ts = time.strftime('%Y%m%d', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
    return ts
   
def extract_info(jsonl):
    """
    Function to return tweets and selected metadata from a jsonl file of tweets obtained from the Twitter API
    
    Keyword argument:
    jsonl -- jsonl file containing tweets got from api
    
    Returns:
    info -- list of comma separated items that consist of text and metadata
    """
    info = []
    with open(jsonl, 'r') as f:
        for line in f:
            tweet = json.loads(line)
            handle = str((tweet['user'])['screen_name'])
            date = get_time(tweet)
            reply = check_reply(tweet)
            retweet = check_retweet(tweet)
            name = str((tweet['user'])['name'].encode('utf8'))
            rtws = str(tweet['retweet_count'])
            favs = str(tweet['favorite_count'])
            text = clean_text(tweet['text'])
            out = handle+','+name+','+date+','+reply+','+retweet+','+rtws+','+favs+','+text
            info.append(out)
    return info   

extracted = []
for doc in glob.glob('tweets/*.jsonl'):
    print normalize_name(doc)
    extracted.extend(extract_info(doc))
            
print len(extracted)
out = open('data/json_tweets.txt', 'w')
for item in extracted:
  out.write("%s\n" % item)