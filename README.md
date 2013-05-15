NLPClass
========

Required External Libraries
--------

*"Standing on the shoulders of giants"*

- [nltk](http://nltk.org/)
- [scipy](http://www.scipy.org/)
- [scikit-learn](http://scikit-learn.org/)
- [networkx](http://networkx.github.io/)
- [tweepy](https://github.com/tweepy/tweepy)
- [BeatifulSoup](http://www.crummy.com/software/BeautifulSoup/)
    - [html5lib](https://pypi.python.org/pypi/html5lib)
    - [lxml](https://pypi.python.org/pypi/lxml)
- [M2Crypto](http://chandlerproject.org/Projects/MeTooCrypto)
- [Divisi2](http://csc.media.mit.edu/docs/divisi2/install.html)

Files
--------

	+
	|   .gitignore  				Files to be ignored in git version control
	|   algorithm_test.py 			Script used to evaluate our algorithm
	|   articles.py 				Module with the list of articles used to build our dataset
	|   dev_set.p 					Serialized Pickle file with Development data set
	|   eval_set.p 					Serialized Pickle file with Evaluation data set
	|   extractor.py 				Script/Module used to extract title and text from article web pages
	|   mturk.py 					Script to connect to MTurk and generate survey for our gold data set
	|   process_results.py 			Script to process the results from MTurk surveys result/ directory
	|   question_builder.py 		Script used to build a question for Amazon MTurk
	|   README.md 					This file
	|   settings.py  				Module with basic settings for our algorithm
	|   similarity.py 				Module for computing similarity measures, normalization, PageRank
	|   twitter.py 					Script/Module to listens and process Twitter data stream
	|   util.py 					Module with util functions
	|   
	+---results 					Results directory (first dataset)
	|       *.csv  					CSV files with results downloaded from Amazon Mturk
	|       ...
	|       
	+---results2 					Results directory (second dataset)
	|       *.csv  					CSV files with results downloaded from Amazon Mturk
	|       ...
	|       
	\---web 						Web interface directory
	    |   bottle.py 				Bottle.py Micro Web Framework used to create our webinterface
	    |   main.py 				Script to initiate web interface application
	    |   topic.tpl 				Template file in HTML / Python to render the data computed in main.py
	    |   
	    +---css 					Cascading Style Sheets directory to stylize HTML
	    |       main.css  			Custom CSS for our web interface (also used Twitter's Bootstrap)
	    |       ...
	    |       
	    +---img 					Images directory used in the web interface
	    |       bg.gif
	    |       ...    
	    |       
	    \---js 						Javascript directory used in the web interface
	        |   
	        \---vendor				JavaScript libraries used (jQuery and Boostrap)
	                ...


Settings
--------

Settings are present in settings.py. The current customizable settings are:

* CONSUMER_KEY = ""
* CONSUMER_SECRET = ""
* ACCESS_KEY = ""
* ACCESS_SECRET = ""

You can get all four settings above from <https://dev.twitter.com/>.


Usage
--------
Our project implemented a pipelined approach. Usage for the different scripts 
of the pipelined are described below. In a production application implementing
our proposed algorithm, the parts of the project used for collecting Twitter data stream
and processing it (extracting articles from the web and building appropriate data structs)
should run in a back-end process.

Therefore, any user-interface (this is the case of the web interface presented) should work
with pre-processed data only. For that reason, our interface located at web/main.py works for
the topics present in our dataset only, which have been processed in serialized in [Pickle](http://docs.python.org/2/library/pickle.html)
files.

### Web Interface

This is the main interface of the system. The machine running this script should have the ability to open sockets, in order to connect to Twitter Stream API.
	
	python web/main.py 

After that, the web interface should be running at <http://localhost:8080>

As mentioned above, our search field is limited to pre-processed topics, which are the following in our dataset:
	
	american_held_nk, poison, syria, mississippi, boston_miranda, sunil_tripathi, pills 
	sherpa_fight, michigan, faa_furloughs, jason_collins, bagram, jackson, virgin_galactic, bangladesh

### Twitter Stream

	python twitter.py [--listen [topic]] [--trends]

#### Examples of usage:

	python twitter.py --listen Boston
prints all stream of tweets about the topic "Boston"

	python twitter.py --trends
prints current trending topics for United States

### Article Extractor

	python extractor.py [URL] [-f]

#### Examples of usage:

	python extractor.py http://www.cnn.com/2013/04/27/justice/ricin-investigation/index.html
prints the title and first paragraph of the article <http://www.cnn.com/2013/04/27/justice/ricin-investigation/index.html>. If you add -f, it will print the full text of the article.

### Data Set Builder

	python algorithm_test.py --build

This command will build new [Pickle](http://docs.python.org/2/library/pickle.html) files called dev_set.p and eval_set.p at the root directory. By default, those files were already pre-processed; so there should be no need to re-run them, unless you change the articles used for dataset in the articles.py file. 

### Algorithm Test

	python algorithm_test.py --test

This command will compute accuracy of the sentence selection of our algorithm against the gold standard generated using Amazon Machine Turk.
The current settings in similarity.py will test accuracy of the algorithm with TF-IDF normalization, Cosine Simlarity Measure, no Stop words, and no Stemmer. The complete results of all alternatives can be found in our project report.
