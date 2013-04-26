#!/usr/bin/env python
# -*- coding: utf-8 -*-
import settings
from util import unshorten, clean_html

import urllib
import urllib2
import cookielib
import urlparse
from bs4 import BeautifulSoup


def build_extractor(url):
    parsed = urlparse.urlparse(url)
    extractor_cls = ALLOWED_HOSTNAMES.get(parsed.hostname, ArticleExtractor(url))
    return extractor_cls(url)


class ArticleExtractor():
    """ Base Class for Article Text Extraction """

    def __init__(self, url):
        self.cj = cookielib.CookieJar()
        self.url = url

        # opener
        self.opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                                           urllib2.HTTPHandler(debuglevel=0),
                                           urllib2.HTTPSHandler(debuglevel=0),
                                           urllib2.HTTPCookieProcessor(self.cj),
                                           urllib2.HTTPErrorProcessor())

        # Fake a regular browser to get right content
        self.opener.addheaders = [
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language', 'en-US,en;q=0.8')
        ]

        self._get_raw()

    def _get_raw(self):
        resp = self.opener.open(self.url)

        # 200, OK
        if resp.getcode() == 200:
            self.raw_text = resp.read()
        else:
            raise Exception('Error: Fetching %s failed.' % url)

    def article(self):
        """ Returns a dictionary with the title and paragraphs of the article """
        raise NotImplementedError()


class NYTArticleExtractor(ArticleExtractor):
    """ nytimes.com Article Extractor """
    def __init__(self, url):
        # tweaking url to get full text
        # parsed[4] = query
        parsed = list(urlparse.urlparse(url))
        qs_params = urlparse.parse_qs(parsed[4])
        qs_params['pagewanted'] = 'all'
        parsed[4] = urllib.urlencode(qs_params)
        url = urlparse.urlunparse(parsed)

        ArticleExtractor.__init__(self, url)

    def article(self):
        soup = BeautifulSoup(self.raw_text)

        title = soup.find_all(itemprop="headline")
        paragraphs = soup.find_all(itemprop="articleBody")

        if len(title) == 0 or len(paragraphs) == 0:
            raise ArticleNotParsable()

        article = dict()

        article['title'] = clean_html(title[0])
        article['paragraphs'] = map(clean_html, paragraphs)

        return article


class WashingtonPostArticleExtractor(ArticleExtractor):
    """ washingtonpost.com Article Extractor """
    def article(self):
        soup = BeautifulSoup(self.raw_text)

        title = soup.select("h1[property=dc.title]")
        paragraphs = soup.select(".article_body p")

        if len(title) == 0 or len(paragraphs) == 0:
            raise ArticleNotParsable()

        article = dict()

        article['title'] = clean_html(title[0])
        article['paragraphs'] = map(clean_html, paragraphs)

        return article


class CNNArticleExtractor(ArticleExtractor):
    """ washingtonpost.com Article Extractor """
    def article(self):
        soup = BeautifulSoup(self.raw_text)

        title = soup.select("h1")
        paragraphs = soup.select(".cnn_strycntntlft > p:not(.cnn_strycbftrtxt)")

        if len(title) == 0 or len(paragraphs) == 0:
            raise ArticleNotParsable()

        article = dict()

        article['title'] = clean_html(title[0])
        article['paragraphs'] = map(clean_html, paragraphs)

        return article

class LATimesArticleExtractor(ArticleExtractor):
    """ LATimes.com article extractor"""
    def article(self):
        soup = BeautifulSoup(self.raw_text)

        title = soup.select("title")
        paragraphs = soup.find("div", {"id": "story-body-text"}).select('p')

        if len(title) == 0 or len(paragraphs) == 0:
            raise ArticleNotParsable()

        article = dict()

        article['title'] = clean_html(title[0])
        article['paragraphs'] = map(clean_html, paragraphs)

        print len(paragraphs)

        return article

class MiamiHeraldExtractor(ArticleExtractor):
    """ MiamiHerald.com extractor"""
    def article(self):
        soup = BeautifulSoup(self.raw_text)

        title = soup.select("title")
        paragraphs = soup.select(".entry-content p")

        if len(title) == 0 or len(paragraphs) == 0:
            raise ArticleNotParsable()

        article = dict()

        article['title'] = clean_html(title[0])
        article['paragraphs'] = map(clean_html, paragraphs)

        return article

class FoxNewsExtractor(ArticleExtractor):
    """FoxNews.com Extractor"""
    def article(self):
        soup = BeautifulSoup(self.raw_text)

        title = soup.select("title")
        paragraphs = soup.select(".article-text p")

        if len(title) == 0 or len(paragraphs) == 0:
            raise ArticleNotParsable()

        article = dict()

        article['title'] = clean_html(title[0])
        article['paragraphs'] = map(clean_html, paragraphs)

        return article

class ArticleNotParsable(Exception):
    """ Exception for when Article Parsing fails """
    pass


ALLOWED_HOSTNAMES = {'www.nytimes.com': NYTArticleExtractor,
                     'www.cnn.com': CNNArticleExtractor,
                     'www.washingtonpost.com': WashingtonPostArticleExtractor,
                     'www.latimes.com': LATimesArticleExtractor,
                     'www.miamiherald.com': MiamiHeraldExtractor,
                     'www.foxnews.com': FoxNewsExtractor,

                     }
                     # 'abcnews.go.com',
                     # 'hosted.ap.org',
                     # 'www.reuters.com',
                     # 'www.usatoday.com'}


class ArticleNotParsable(Exception):
    """ Exception for when Article Parsing fails """
    pass


ALLOWED_HOSTNAMES = {'www.nytimes.com': NYTArticleExtractor,
                     'www.cnn.com': CNNArticleExtractor,
                     'www.washingtonpost.com': WashingtonPostArticleExtractor
                     }
                     # 'www.foxnews.com',
                     # 'abcnews.go.com',
                     # 'hosted.ap.org',
                     # 'www.reuters.com',
                     # 'www.usatoday.com',
                     # 'www.latimes.com',
                     # 'www.miamiherald.com'}
