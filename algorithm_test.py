from process_results import Results
from sklearn.cluster import DBSCAN
from nltk.corpus import stopwords
import nltk
from nltk import tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from extractor import *
import pprint
import pickle

pp = pprint.PrettyPrinter(indent=4)

class Topic:
    """ A topic is a single \"trending\" topic. Each topic
        is made of multiple documents. """
    def __init__(self, topic):
        self.topic = topic
        self.documents = []

    def add_document(self, url):
        """ Adds a document to the topic list"""
        article = build_extractor(url).article()
        doc = Document(article)
        self.documents.append(doc)

    def summarize(self):
        pass



class Document:
    """ Represents a single document (a single extracted page split into 
        sections. A first begining, middle, end.
    """
    stopwords = nltk.corpus.stopwords.words('english')
    lemtzr = WordNetLemmatizer()

    def __init__(self, document):
        self.paragraphs = document['paragraphs']
        self.title = document['title']
        self.split_sections()

    def split_sections(self):
        self.begining = get_first_paragraph(self.paragraphs[1:len(self.paragraphs)-1],
                                           [tokenize.sent_tokenize(self.paragraphs[0])])

        self.end = self.paragraphs[-1]

        start_index = 1
        end_index = -1

        if len(nltk.tokenize.sent_tokenize(self.paragraphs[-1])) < 3:
            self.end = self.paragraphs[-2] + ' ' + self.paragraphs[-1]
            end_index = -2

        if len(self.begining) > len(nltk.tokenize.sent_tokenize(self.paragraphs[0])):
            #the first paragraph was too small -- multiple paragraphs were used
            #for now just assume the first 2 were used
            start_index = 2

        self.middle = ''
        for x in range(start_index + 1, len(self.paragraphs)+end_index):
            self.middle += ' '
            self.middle += self.paragraphs[x]

        self.middle = nltk.tokenize.sent_tokenize(self.middle)
        self.end = nltk.tokenize.sent_tokenize(self.end)

    def tokenize_and_clean(text):
        """Tokenizes and removes stopwords"""
        tokenized = nltk.word_tokenize(text)
        cleaned_sentence = [w for w in tokenized if w.lower() not in stopwords]
        return cleaned_sentence

    def lemmatizer(tokenized):
        """ Uses the built in wordnet lemmatizer to generate a summary"""
        lematized = [lmtzr.lemmatize(w) for w in tokenized]
        return lematized

    def pos_tagging(tokenized_text):
        """ Apparently there are multiple ways to do POS tagging in
            NLTK. Unfortunetly, the standard wordnet tagger has some
            internal problems, so instead we'll use the (already trained)
            treebank tagger
        """
        tagged = nltk.pos_tag(tokenized_text)
        #convert all of the tags to wordnet standard
        tagged [get_wordnet_pos(tag) for tag in tagged]
        pass

    def get_wordnet_pos(treebank_tag):
        """
            Converts the treebank tag to the standard wordnet tag.
            Shamelessly taken from:
            http://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
        """
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return ''



class Tester:
    def __init__(self):
        self.results = Results()

    def load_data(self):
        self.results.build_article_dataset()
        topic_count = len(self.results.get_data())
        min_set = topic_count/4
        self.total_data = self.results.get_data()

        dev_keys = self.total_data.keys()[0:min_set*3]
        eval_keys = self.total_data.keys()[min_set*3:len(self.total_data)]

        self.dev_set = dict((k,v) for k, v in self.total_data.iteritems() if k in dev_keys)
        self.eval_set = dict((k,v) for k, v in self.total_data.iteritems() if k in eval_keys)

#util functions
def get_first_paragraph(listOfParagraphs, first):
    """We want at least 3 sentences to compare"""
    #print listOfParagraphs

    if len(first) >= 3:
        return_value = first
        return return_value

    if len(listOfParagraphs) is 0:
        #nothing left...
        return first
    #alright, append the next paragraph
    if len(tokenize.sent_tokenize(listOfParagraphs[0])) >= 3:
        #append string to first
        tokenized = tokenize.sent_tokenize(listOfParagraphs[0])
        first.append(tokenized)
        return first
    else:
        #well append the whole next paragraph and continue
        tokenized = tokenize.sent_tokenize(listOfParagraphs[0])
        first.append(tokenized)
        para = get_first_paragraph(listOfParagraphs[1:len(listOfParagraphs)-1],
                                   first)
        return para

if __name__=="__main__":
    tester = Tester()
    tester.load_data()

    print len(tester.total_data)
    print (tester.dev_set.keys())
    print (tester.eval_set.keys())

    #load the dev topics
    topics = []
    for key in tester.dev_set.keys():
        topic = Topic(key)
        for url in tester.dev_set[key].keys():
            print url
            print tester.dev_set[key][url]
            topic.add_document(url)
        break
        topics.append(topic)

    #pickle.dump(topics, open("dev_set.p", "wb"))

