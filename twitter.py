#!/usr/bin/env python
# -*- coding: utf-8 -*-
import settings
import extractor
from util import unshorten, is_url_allowed, print_table

import sys
import tweepy

# Athenticates with Twitter API using OAuth (API keys are in settings.py)
auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)

# Instantiate the API
api = tweepy.API(auth)


class CustomStreamListener(tweepy.StreamListener):
    """ Stream Listener used to collect data (tweets)
    from the Twitter API stream on specific topics """

    def __init__(self, urls, limit_urls=None, limit_tweets=None, prints=False):
        """ Inits a Custom Stream Listener """
        self.api = api
        self.urls = urls
        self.limit_urls = limit_urls
        self.limit_tweets = limit_tweets
        self.prints = prints

    def on_status(self, status):
        """ Event callback for every new status (tweet) on the Stream """

        # prints status text if configured
        if self.prints:
            print status.text

        # check to see if the status has links on ot
        if status.entities['urls']:
            # if it has links, loop through all links within the status
            for url in status.entities['urls']:
                # unshortens url
                url = unshorten(url['expanded_url'])
                # check we can crawl such URL
                if is_url_allowed(url):
                    # increment url count
                    self.urls[url] = self.urls.get(url, 0) + 1

                    if limit_urls and len(self.urls) >= limit_urls:
                        return False  # stop streaming



    def on_error(self, status_code):
        """ Event callback for every error on the Stream """
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True  # Don't kill the stream

    def on_timeout(self):
        """ Event call back if the listener times out """
        print >> sys.stderr, 'Timeout...'
        return True  # Don't kill the stream


def start_trends_stream(trends, prints=False):
    """ Start Stream Listener on current Trends """
    if not trends:
        trends = get_trends()

    urls = dict()  # dict of url counts
    
    listener = CustomStreamListener(urls=urls, prints=prints)

    # start straming
    sapi = tweepy.Stream(auth, listener)
    sapi.filter(track=trends, languages=['en'])

    return urls


def get_trends(WOEID=2450022):
    """ Gets Twitter Trends (by default gets U.S. trends) """
    # get the trends
    us_trends = api.trends_place(WOEID)
    trends = [trend['name'].encode('utf-8') for trend in us_trends[0]['trends']]
    return trends


if __name__ == "__main__":
    # evalute arguments
    import argparse

    parser = argparse.ArgumentParser(description='Twitter script to extract data.')

    parser.add_argument('topic', metavar='topic', nargs='?',
                        help='a specific topic to query')

    parser.add_argument('--trends', action='store_true',
                        help='prints twitter trending topics')

    parser.add_argument('--listen', action='store_true',
                        help='prints tweets as they arrive')

    parser.add_argument('--top', action='store_true',
                        help='prints top referred urls in topic')

    args = parser.parse_args()


    if args.trends:
        print '### Trending topics:'
        print get_trends()

    elif args.listen:
        if not args.topic:
            print '### Tweets about the trending topics:'
            start_trends_stream(prints=True)
        else:
            print '### Tweets about %s' % args.topic
            start_trends_stream(trends=[args.topic], prints=True)

    elif args.top and args.topic:
        print '### Top URLs about %s' % args.topic
        urls = start_trends_stream(trends=[args.topic], prints=True)
        urls = sorted(urls, key=urls.get)  # ordering urls by counts
        table = [(url, urls[url]) for url in urls]
        print_table(table)

    elif args.top and args.topic:
        print '### Summary of %s' % args.topic


    else:
        parser.print_help()
