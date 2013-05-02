NLPClass
========

Required External Libraries
--------

- [nltk](http://nltk.org/)
- [tweepy](https://github.com/tweepy/tweepy)
- [BeatifulSoup](http://www.crummy.com/software/BeautifulSoup/)
    - [html5lib](https://pypi.python.org/pypi/html5lib)
    - [lxml](https://pypi.python.org/pypi/lxml)
- [M2Crypto](http://chandlerproject.org/Projects/MeTooCrypto)

Settings
--------

Settings are present in settings.py. The current customizable settings are:

* CONSUMER_KEY = ""
* CONSUMER_SECRET = ""
* ACCESS_KEY = ""
* ACCESS_SECRET = ""

You can get all four settings above from <http://api.twitter.com>.


Scratch
--------

Tokenizer:
Before using the Tokenizer, both NLTK and the Punkt dataset must be
installed. After installing NLTK call nltk.download() and then navigate
and download the correct corpora. I already had it downloaded but 
because it was out of date it was causing errors.

Punkt Tokenizer in NLTK. Algorithm citation below.
Kiss, Tibor and Strunk, Jan (2006): Unsupervised Multilingual Sentence
  Boundary Detection.  Computational Linguistics 32: 485-525.