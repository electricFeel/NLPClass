import sys
import tweepy
#yes: two seperate APIs because I could'nt get 
#tweepy to behave
import twitter
import sqlite3 as lite

consumer_key=""
consumer_secret=""
access_key = ""
access_secret = "" 



auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

class CustomStreamListener(tweepy.StreamListener):
    con = None
    cur = None
    
    try:
        con = lite.connect('twitter_data.db')
        cur = con.cursor()
        cur.execute('SELECT SQLITE_VERSION()')
        data = cur.fetchone()

        print "SQLITE version: %s" % data
    except lite.Error, e:
        print "Error %s" % e.args[0]

    def on_status(self, status):
        print status.text

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

sapi = tweepy.streaming.Stream(auth, CustomStreamListener())

#get the trends
twitter_api = twitter.Twitter(domain="api.twitter.com", api_version='1')
WORLD_WOE_ID = 1
world_trends = twitter_api.trends._(WORLD_WOE_ID) 
trends = world_trends()
trends = [trend['name'] for trend in trends[0]['trends']]
print trends
sapi.filter(track=trends)