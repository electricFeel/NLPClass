import settings
import extractor

import urllib
import urllib2
import cookielib
import urlparse
import nltk.util
import HTMLParser

class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    """ Handles redirects to cache redirects """
    def __init__(self, urlsyn):
        self.urlsyn = urlsyn

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.urlsyn.append(newurl)
        return urllib2.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)


def unshorten(url):
    """ Unshortens URLs like in bit.ly, t.co, etc """
    # check if caching dict is available
    if not hasattr(unshorten, "urlsyn_dict"):
        unshorten.urlsyn_dict = dict()
    # return cached value if in cache
    elif url in unshorten.urlsyn_dict:
        return unshorten.urlsyn_dict[url]

    urlsyn = [url]
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(HTTPRedirectHandler(urlsyn),
                                  urllib2.HTTPHandler(debuglevel=0),
                                  urllib2.HTTPSHandler(debuglevel=0),
                                  urllib2.HTTPCookieProcessor(cj),
                                  urllib2.HTTPErrorProcessor())

    # Fake a regular browser to get right content
    opener.addheaders = [
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
        ('Accept-Language', 'en-US,en;q=0.8')
    ]

    request = urllib2.Request(url)

    # hack to avoid getting full page contents
    # request.get_method = lambda: 'HEAD'

    opener.open(request)

    # caching redirects
    final_url = urlsyn.pop()
    for syn in urlsyn:
        unshorten.urlsyn_dict[syn] = final_url

    return final_url


def is_url_allowed(url):
    parsed = urlparse.urlparse(url)
    return (parsed.hostname in extractor.ALLOWED_HOSTNAMES)


def clean_html(text):
    """ Sanitizes text to remove any html content / entities """
    html_parser = HTMLParser.HTMLParser()
    return html_parser.unescape(nltk.util.clean_html(str(text)))
