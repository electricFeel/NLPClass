from process_results import Results
from nltk.corpus import stopwords
import nltk
from nltk import tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from extractor import *
import pickle
from similarity import textrank
import numpy as np


class Topic:
    """ A topic is a single \"trending\" topic. Each topic
        is made of multiple documents. """
    def __init__(self, topic):
        self.topic = topic
        self.documents = []
        self.urls = []
        self.summary = dict()

    def add_document(self, url, answers=[]):
        """ Adds a document to the topic list"""
        article = build_extractor(url).article()
        doc = Document(article, url, answers)
        self.documents.append(doc)
        self.urls.append(url)

    def summarize(self):
        firsts = []
        middles = []
        ends = []
        for doc in self.documents:
            cur = doc.get_most_important_sentences()
            #get the first, middle and end best sentences
            firsts.append(cur[1][0])
            middles.append(cur[2][0])
            ends.append(cur[3][0])

        #find the best of each section in total
        best_first = textrank(firsts)[0]
        best_middle = textrank(middles)[0]
        best_end = textrank(ends)[0]

        self.summary = [
            # first section
            {
                'sentence': best_first.sentence,
                'from_article': self.urls[best_first.document]
            },
            # middle section
            {
                'sentence': best_middle.sentence,
                'from_article': self.urls[best_middle.document]
            },
            # end section
            {
                'sentence': best_end.sentence,
                'from_article': self.urls[best_end.document]
            }
        ]

        return best_first, best_middle, best_end


class Document:
    """ Represents a single document (a single extracted page split into
        sections. A first begining, middle, end.
    """
    stopwords = nltk.corpus.stopwords.words('english')
    lemtzr = WordNetLemmatizer()

    def __init__(self, document, url, answers=[]):
        self.paragraphs = document['paragraphs']
        self.title = document['title']
        self.text = ' '.join(self.paragraphs)
        self.split_sections()
        self.answers = answers
        self.url = url

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

    def get_most_important_sentences(self):
        #find the single most important sentence in the first
        #paragraph
        ranked_sentences = textrank(self.text)
        best_first = self.get_best_sentence_in_set(self.begining, ranked_sentences)
        best_middle = self.get_best_sentence_in_set(self.middle, ranked_sentences)
        best_last = self.get_best_sentence_in_set(self.end, ranked_sentences)
        return ranked_sentences, best_first, best_middle, best_last

    def get_best_sentence_in_set(self, sentence_set, ranked_sentences):
        best = ''
        indexof = -1
        for sentence in ranked_sentences:
            if sentence.sentence in sentence_set:
                best = sentence.sentence
                indexof = sentence_set.index(best)
                break
        return best, indexof

    def eval_best_sentence(self):
        __mat = []
        for vec in self.answers:
            __mat.append(map(int, vec))

        mat = np.matrix(__mat)

        mean_mat = np.mean(mat, axis=0)

        occurences = np.where(mean_mat == mean_mat.max())
        return occurences

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
        #note we're not using this just yet
        tagged = nltk.pos_tag(tokenized_text)
        #convert all of the tags to wordnet standard
        tagged = [get_wordnet_pos(tag) for tag in tagged]
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
        first.extend(tokenized)
        return first
    else:
        #well append the whole next paragraph and continue
        tokenized = tokenize.sent_tokenize(listOfParagraphs[0])
        first.extend(tokenized)
        para = get_first_paragraph(listOfParagraphs[1:len(listOfParagraphs)-1],
                                   first)
        return para

if __name__ == "__main__":
    tester = Tester()
    tester.load_data()

    # evalute arguments

    import argparse

    parser = argparse.ArgumentParser(description='Test algorithm.')

    parser.add_argument('--build', action='store_true',
                        help='build eval and dev sets')

    parser.add_argument('--count', action='store_true',
                        help='count number of articles')

    parser.add_argument('--test', action='store_true',
                        help='called to test')

    args = parser.parse_args()

    # count argument
    if args.count:
        print 'Total count: %d' % len(tester.total_data)
        print 'Dev set count: %d' % len(tester.dev_set.keys())
        print 'Eval set count: %d' % len(tester.eval_set.keys())

    # build argument
    elif args.build:
        def build_topics(name, topicset):
            # load the eval topics
            topics = []
            for key in topicset.keys():
                topic = Topic(key)
                for url in topicset[key].keys():
                    print url
                    print topicset[key][url]
                    try:
                        answers = topicset[key][url]
                        topic.add_document(url, answers)
                    except:
                        print 'url couln\'t be found ', url
                topics.append(topic)

            pickle.dump(topics, open(name + ".p", "wb"))

        build_topics("eval_set", tester.eval_set)
        build_topics("dev_set", tester.dev_set)

    # test argument
    elif args.test:
        topics = pickle.load(open("dev_set.p", "rb"))
        doc = topics[0].documents[0]
        # print '#################'
        # print doc.get_most_important_sentences()[1], doc.get_most_important_sentences()[2], doc.get_most_important_sentences()[3]
        # print np.array(doc.eval_best_sentence())[0][0][0]
        # print '#################'
        total_correct = 0
        total = 0
        for topic in topics:
            for doc in topic.documents:
                total += 1
                for best_sent in np.array(doc.eval_best_sentence())[0][0]:
                    if doc.get_most_important_sentences()[1][1] == best_sent + 1:
                        total_correct += 1
                        break
            print topic.topic
            print topic.summarize()
        print 'Total Correct: %d or %.2f%%' % (total_correct, float(total_correct)/total * 100)
        print 'Total Incorrect %d or %.2f%%' % ((total-total_correct), float(total-total_correct)/total * 100)

    else:
        parser.print_help()
