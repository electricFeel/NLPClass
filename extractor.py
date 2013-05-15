#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import clean_html
import urllib
import urllib2
import cookielib
import urlparse
from bs4 import BeautifulSoup


def build_extractor(url):
    """ Builds an extractor object based on the URL passed by argument """
    parsed = urlparse.urlparse(url)
    if parsed.hostname in ALLOWED_HOSTNAMES:
        extractor_cls = ALLOWED_HOSTNAMES.get(parsed.hostname)
        return extractor_cls(url)
    else:
        raise DomainNotAllowed()


class ArticleExtractor():
    """ Base Class for Article Text Extraction 

    Subclasses of this class are able to extract content for specific sites.
    A call to extractor.article() returns a structured dictionary with
    article's title and paragraphs.
    """

    def __init__(self, url):
        self.html_parser = 'html5lib'
        self.cj = cookielib.CookieJar()
        self.url = url.strip()

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
        """ Gets raw content (i.e. HTML content) and stores it """
        resp = self.opener.open(self.url)

        # 200, OK
        if resp.getcode() == 200:
            self.raw_text = resp.read()
        else:
            raise Exception('Error: Fetching %s failed.' % self.url)

    def article(self):
        """ Returns a dictionary with the title and paragraphs of the article """
        self.soup = BeautifulSoup(self.raw_text, self.html_parser)

        self._article()

        if len(self._title) == 0 or len(self._paragraphs) == 0:
            raise ArticleNotParsable()

        article = dict()

        article['title'] = clean_html(self._title[0])

        # clean html and remove blank paragaphs
        article['paragraphs'] = filter(bool, map(clean_html, self._paragraphs))

        return article


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

    def _article(self):
        self._title = self.soup.find_all(itemprop="headline")
        self._paragraphs = self.soup.find_all(itemprop="articleBody")


class WashingtonPostArticleExtractor(ArticleExtractor):
    """ washingtonpost.com Article Extractor """
    def _article(self):
        self._title = self.soup.select("h1[property=dc.title]")
        self._paragraphs = self.soup.select(".article_body p")

        # other case (blogs)
        if len(self._title) == 0 or len(self._paragraphs) == 0:
            self._title = self.soup.select("h1.entry-title")
            self._paragraphs = self.soup.select(".entry-content > p")


class CNNArticleExtractor(ArticleExtractor):
    """ cnn.com Article Extractor """
    def _article(self):
        self._title = self.soup.select("h1")
        self._paragraphs = self.soup.select(".cnn_storypgraphtxt")


class LATimesArticleExtractor(ArticleExtractor):
    """ LATimes.com article extractor"""
    def _article(self):
        self._title = self.soup.select(".story h1")
        self._paragraphs = self.soup.select("#story-body-text p")

        # other case (articles.latimes)
        if len(self._title) == 0 or len(self._paragraphs) == 0:
            self._title = self.soup.select("h1")
            self._paragraphs = self.soup.select("#area-article-first-block p") + self.soup.select("#mod-a-body-after-first-para p")


class MiamiHeraldExtractor(ArticleExtractor):
    """ MiamiHerald.com extractor"""
    def _article(self):
        self._title = self.soup.select("title")
        self._paragraphs = self.soup.select(".entry-content p")


class FoxNewsExtractor(ArticleExtractor):
    """FoxNews.com Extractor"""
    def _article(self):
        self._title = self.soup.select("title")
        self._paragraphs = self.soup.select(".article-text p")


class YahooNewsExtractor(ArticleExtractor):
    """news.yahoo.com extractor"""
    def _article(self):
        self._title = self.soup.select("title")
        self._paragraphs = self.soup.find("div", {"id": "mediaarticlebody"}).select('p')


class MSNNewsExtractor(ArticleExtractor):
    """msnnews.com extractor"""
    def _article(self):
        self._title = self.soup.select(".articlecontent h1")
        self._paragraphs = self.soup.select(".articlecontent p")


class CBSNewsExtractor(ArticleExtractor):
    """nbcnews.com extractor"""
    def _article(self):
        self._title = self.soup.select("#contentBody h1")
        self._paragraphs = self.soup.select(".storyText p")

        # other case (blogs)
        if len(self._paragraphs) == 0:
            self._paragraphs = self.soup.select("#contentBody .postBody > p")


class APExtractor(ArticleExtractor):
    """AP news extractor"""
    def _article(self):
        self._title = self.soup.select(".entry-title")  # title is the first item
        self._paragraphs = self.soup.select(".entry-content p")


class USATodayExtractor(ArticleExtractor):
    """USAToday.com extractor"""
    def _article(self):
        self._title = self.soup.find_all(itemprop="headline")
        self._paragraphs = self.soup.select("[itemprop=articleBody] > p")


class ABCNewsExtractor(ArticleExtractor):
    """abcnews.go.com extractor"""
    def _article(self):
        self._title = self.soup.select("h1.pagetitle")
        self._paragraphs = self.soup.select("#innerbody .font-toggle > p")

        # other case
        if len(self._title) == 0 or len(self._paragraphs) == 0:
            self._title = self.soup.select("h1.headline")
            self._paragraphs = self.soup.select("#storyText > p")


class ReutersExtractor(ArticleExtractor):
    """www.reuters.com extractor"""
    def __init__(self, url):
        """ Reuteurs HTML requires a different parser not to break """
        ArticleExtractor.__init__(self, url)
        self.html_parser = 'html.parser'

    def _article(self):
        self._title = self.soup.select("h1")
        self._paragraphs = self.soup.select("#articleText > p")


class NBCNewsExtractor(ArticleExtractor):
    """www.nbcnews.com extractor"""
    def _article(self):
        self._title = self.soup.select("h1#headline")
        self._paragraphs = self.soup.select(".entry-content div > p")


class ArticleNotParsable(Exception):
    """ Exception for when Article Parsing fails """
    pass


class DomainNotAllowed(Exception):
    """ Exception for when the Domain of the artcile is not parsable """
    pass


ALLOWED_HOSTNAMES = {'www.nytimes.com': NYTArticleExtractor,
                     'www.cnn.com': CNNArticleExtractor,
                     'www.washingtonpost.com': WashingtonPostArticleExtractor,
                     'www.latimes.com': LATimesArticleExtractor,
                     'articles.latimes.com': LATimesArticleExtractor,
                     'www.miamiherald.com': MiamiHeraldExtractor,
                     'www.foxnews.com': FoxNewsExtractor,
                     'news.yahoo.com': YahooNewsExtractor,
                     'www.msn.com': MSNNewsExtractor,
                     'news.msn.com': MSNNewsExtractor,
                     'www.cbsnews.com': CBSNewsExtractor,
                     'bigstory.ap.org': APExtractor,
                     'hosted.ap.org': APExtractor,
                     'www.usatoday.com': USATodayExtractor,
                     'abcnews.go.com': ABCNewsExtractor,
                     'www.reuters.com': ReutersExtractor,
                     'www.nbcnews.com': NBCNewsExtractor
                     }

if __name__ == "__main__":
    # evalute arguments

    import argparse

    parser = argparse.ArgumentParser(description='Extract articles. Prints 1st paragraph by default.')

    parser.add_argument('url', metavar='URL', nargs='?',
                        help='url of the article')

    parser.add_argument('-f', action='store_true',
                        help='prints full text')

    args = parser.parse_args()

    # executes script
    if args.url:
        a = build_extractor(args.url).article()
        if args.f:
            print '# Title: \n\n%s\n\n# Text:\n\n%s' % (a['title'], '\n\n'.join(a['paragraphs']))
        else:
            print '# Title: \n\n%s\n\n# 1st Paragraph:\n\n%s' % (a['title'], a['paragraphs'][0])

    else:
        parser.print_help()
