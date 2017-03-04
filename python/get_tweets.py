import tweepy
import json
import pandas as pd
import time

def get_keys(codefile):
    """
    Function to import codes for accessing twitter api
    
    Keyword arguments:
    codefile -- file containing the various keys
    """
    codes = open(codefile, 'r').read().splitlines()
    consumer_key, consumer_secret = codes[0], codes[1]
    access_key, access_secret = codes[2], codes[3]
    return consumer_key, consumer_secret, access_key, access_secret

def get_all_tweets(screen_name):
    """
    Function to get all (or most recent 3240) tweets of a user and store tweets and metadata in jsonl file
    
    Keyword arguments:
    screen_name -- file twitter handle of user

    Returns:
    str(screen_name)+".jsonl" containing tweet text and metadata
    """
    #Twitter only allows access to a users most recent 3240 tweets with this method
    
    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    
    #initialize a list to hold all the tweepy Tweets
    alltweets = []    
    
    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name, count=200, include_rts = True)
    
    #only do this for users that have actually tweeted
    if len(new_tweets) > 0:
        #save most recent tweets
        alltweets.extend(new_tweets)
    
        #save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
    
        #keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
        
            #all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = api.user_timeline(screen_name = screen_name,count=200, max_id=oldest, include_rts = True)
        
            #save most recent tweets
            alltweets.extend(new_tweets)
        
            #update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1
        
            print "...%s tweets downloaded so far" % (len(alltweets))
        
        # Save tweets for user in a json file
        fname = "tweets/"+str(screen_name)+".jsonl"
        with open(fname, 'w') as f:
            for status in alltweets:
                f.write(json.dumps(status._json)+"\n")
    
        #close the file
        print "Done with " + str(screen_name)
        time.sleep(60)
        print "Sleeping for one minute"
    
# Import codes
consumer_key, consumer_secret, access_key, access_secret = get_keys('data/codes.txt')

# Import twitter handles for TDs that served in the Dail between 2011 and 2016
df = pd.read_csv('data/twitter_handles.csv')
# Get usernames for those with accounts
handles = df['Twitter'].tolist()
handles = [user for user in handles if str(user) != 'nan']
# Get tweets for all users
for user in handles:
    get_all_tweets(user)