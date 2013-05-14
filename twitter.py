#!/usr/bin/env python
# -*- coding: utf-8 -*-
import settings
import extractor
from util import unshorten, is_url_allowed

import sys
import tweepy
import sqlite3 as lite

# Athenticates with Twitter API using OAuth (API keys are in settings.py)
auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)

# Instantiate the API
api = tweepy.API(auth)


class CustomStreamListener(tweepy.StreamListener):
    """ Stream Listener used to collect data (tweets)
    from the Twitter API stream on specific topics """
    con = None
    cur = None

    def __init__():
        """ Inits a Custom Stream Listener """
        try:
            con = lite.connect('twitter_data.db')
            cur = con.cursor()
            cur.execute('SELECT SQLITE_VERSION()')
            data = cur.fetchone()
        except lite.Error, e:
            print "Error %s" % e.args[0]

    def on_status(self, status):
        """ Event callback for every new status (tweet) on the Stream """

        # check to see if the status has links on ot
        if status.entities['urls']:

            # if it has links, loop through all links within the status
            for url in status.entities['urls']:

                # check we can crawl such URL 
                if is_url_allowed(unshorten(url['expanded_url'])):

                    from pprint import pprint
                    print unshorten(url['expanded_url'])

                    
                    try:
                        pprint(extractor.build_extractor(unshorten(url['expanded_url'])).article())
                    except:
                        print 'not parsable'
                    print '----'

    def on_error(self, status_code):
        """ Event callback for every error on the Stream """
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True  # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True  # Don't kill the stream


def start_trends_stream():
    """ Start Stream Listener on current Trends """
    sapi = tweepy.Stream(auth, CustomStreamListener())
    sapi.filter(track=get_trends, languages=['en'])


def get_trends(WOEID=2450022):
    """ Gets Twitter Trends (by default gets U.S. trends) """
    # get the trends
    us_trends = api.trends_place(WOEID)
    trends = [trend['name'].encode('utf-8') for trend in us_trends[0]['trends']]
    return trends