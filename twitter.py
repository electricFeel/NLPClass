#!/usr/bin/env python
# -*- coding: utf-8 -*-
import settings
import extractor
from util import unshorten, is_url_allowed

import sys
import tweepy
import sqlite3 as lite

auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
api = tweepy.API(auth)


class CustomStreamListener(tweepy.StreamListener):
    con = None
    cur = None

    def __init__():
        try:
            con = lite.connect('twitter_data.db')
            cur = con.cursor()
            cur.execute('SELECT SQLITE_VERSION()')
            data = cur.fetchone()

            print "SQLITE version: %s" % data
        except lite.Error, e:
            print "Error %s" % e.args[0]

    def on_status(self, status):
        if status.entities['urls']:
            for url in status.entities['urls']:
                if is_url_allowed(unshorten(url['expanded_url'])):
                    from pprint import pprint
                    print unshorten(url['expanded_url'])
                    try:
                        pprint(extractor.build_extractor(unshorten(url['expanded_url'])).article())
                    except:
                        print 'not parsable'
                    print '----'

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True  # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True  # Don't kill the stream


def start_trends_stream():
    """ Start Stream Listener on current Trends """
    sapi = tweepy.Stream(auth, CustomStreamListener())
    sapi.filter(track=get_trends, languages=['en'])


def get_trends():
    """ Gets U.S. Twitter Trends """
    # get the trends
    US_WOEID = 2450022
    us_trends = api.trends_place(US_WOEID)
    trends = [trend['name'].encode('utf-8') for trend in us_trends[0]['trends']]
    return trends