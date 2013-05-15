import networkx as nx
import numpy as np
from nltk.tokenize.punkt import PunktSentenceTokenizer
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.metrics.pairwise import pairwise_distances, pairwise_kernels
from collections import namedtuple
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import nltk

sw = stopwords.words('english')
porter_stemmer = nltk.PorterStemmer()
lemtzr = WordNetLemmatizer()

# TextRank Tuple type used to return sentences of TextRank algorithm
TextRank = namedtuple('TextRank', ['score', 'sentence', 'document'])


def textrank(document):
    """ Performs the whole process of sentence comparison by similarity
    and scores sentence according to their importance within the document.

    We first vectorize documents with a bag-of-words (Count Vectorizer), then
    normalize the sentence vectors with tf-idf. Then, we construct graph adjacency
    matrix where edge weights are similarity values using one of our similarity 
    functions. With that graph where vertices are sentences, we use networkx' 
    built-in PageRank algorithm to score the sentences and return a list
    of tuples (sentence, score, document) ordered by score.
    """ 
    if isinstance(document, basestring):      # if the document is not tokenized
        sentences = sent_tokenize_func(document)
    else:                                     # if the sentences are already tokenized
        sentences = document

    # vectorizer
    vectorizer = CountVectorizer()

    # vectorize individual sentences counting up the word occurences
    matrix = vectorizer.fit_transform(sentences)

    # normalize counts
    normalized = normalize_func(matrix)

    # creates a similarity graph matrix
    similarity_graph = similarity_func(normalized)

    # converts matrix to a networkx' graph struct
    nx_graph = nx.to_networkx_graph(similarity_graph)

    # use PageRank to score vertices in the graph
    scores = nx.pagerank(nx_graph)

    # return vertices ordered by score
    return sorted((TextRank(score=scores[i], sentence=sentence, document=i)
                  for i, sentence in enumerate(sentences)),
                  reverse=True)

# Word Tokenizer functions
def word_tokenizer(text):
    """ Regular Word Tokenizer """
    return nltk.word_tokenize(text)

def word_tokenizer_lemmatize(text):
    """ Word Tokenizer followed by WordNet lemmatizer """
    tokenized = word_tokenizer(text)
    lematized = [lemtzr.lemmatize(w) for w in tokenized]
    return lematized

def word_tokenizer_stemmer(text):
    """ Word Tokenizer followed by Porter stemming """
    tokenized = word_tokenizer(text)
    lematized = [stemmer.stem(w) for w in tokenized]
    return lematized

# Sentence Tokenizer functions
def punktokenizer(document):
    """ Tokenize functions using NLTK's default tokenizer 

    Based on unsupervised algorithm for sentence boundary detection"""
    sentence_tokenizer = PunktSentenceTokenizer()
    return sentence_tokenizer.tokenize(document)


# Normalization functions

def tfidf(matrix):
    """ Performs TF-IDF normalization in a term-frequency vector space model """
    return TfidfTransformer().fit_transform(matrix)


# Similarity functions

def cosine(matrix):
    """ Performs vector pairwise comparison using cosine similarity as kernel function 

    Returns a similarity matrix """
    return pairwise_kernels(matrix, metric='cosine')


def linear(matrix):
    """ Performs vector pairwise comparison using dot product as kernel function

    Returns a similarity matrix """
    return pairwise_kernels(matrix)


# SETTINGS
# Those settings can be easily changed to point to the correct fuctions to be tested
sent_tokenize_func = punktokenizer
normalize_func = tfidf
similarity_func = cosine
stemmer = porter_stemmer