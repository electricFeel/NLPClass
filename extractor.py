import urllib
import urllib2
import cookielib
import urlparse
import logging
import nltk.util 
import HTMLParser
from bs4 import BeautifulSoup


ALLOWED_HOSTNAMES = ['nytimes.com',
                     'cnn.com',
                     'washingtonpost.com']

html_paser = HTMLParser.HTMLParser()


def clean_html(text):
    """ Sanitizes text to remove any html content / entities """
    return html_paser.unescape(nltk.util.clean_html(str(text)))


class ArticleExtractor():
    """ Base Class for Article Text Extraction """
    # static variable
    cj = cookielib.CookieJar()

    def __init__(self, url):
        self.url = url
        self.parsed = urlparse.urlparse(url)

        # if self.parsed.hostname not in ALLOWED_HOSTNAMES:
        #     raise Exception('Error: Domain %s not supported.'
        #                     % self.parsed.hostname)

        # opener
        self.opener = urllib2.build_opener(ArticleHTTPRedirectHandler(),
                                           urllib2.HTTPHandler(debuglevel=1),
                                           urllib2.HTTPSHandler(debuglevel=0),
                                           urllib2.HTTPCookieProcessor(self.cj)
                                           )

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

        article = dict()

        article['title'] = clean_html(soup.find_all(itemprop="headline")[0])
        article['paragraphs'] = map(clean_html,
                                    soup.find_all(itemprop="articleBody"))

        return article


class WashingtonPostArticleExtractor(ArticleExtractor):
    """ washingtonpost.com Article Extractor """
    def article(self):
        soup = BeautifulSoup(self.raw_text)

        article = dict()

        article['title'] = clean_html(soup.select("h1[property=dc.title]")[0])
        article['paragraphs'] = map(clean_html, soup.select(".article_body p"))

        return article


class ArticleHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    """ Handles redirects to cache redirects """
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # TODO: caching
        logging.info('Redirect')
        return urllib2.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)