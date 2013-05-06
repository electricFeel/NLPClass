import networkx as nx
import numpy as np
from nltk.tokenize.punkt import PunktSentenceTokenizer
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer

# SETTINGS
sent_tokenize_func = punktokenizer
normalize_func = tfidf
similarity_func = dotproduct


#http://joshbohde.com/blog/document-summarization

def textrank(document):
    sentences = sent_tokenize_func(document)

    matrix = CountVectorizer().fit_transform(sentences)

    # normalize counts
    normalized = normalize_func(matrix)

    # creates a similarity graph matrix
    similarity_graph = similarity_func(normalized)

    nx_graph = nx.from_scipy_sparse_matrix(similarity_graph)

    # use PageRank to score vertices in the graph
    scores = nx.pagerank(nx_graph)

    # return vertices ordered by score
    return sorted(((scores[i], s) for i, s in enumerate(sentences)),
                  reverse=True)


# Sentence Tokenizer functions
def punktokenizer(document):
    sentence_tokenizer = PunktSentenceTokenizer()
    return sentence_tokenizer.tokenize(document)


# Normalization functions

def tfidf(matrix):
    return TfidfTransformer().fit_transform(matrix)


# Similarity functions

def dotproduct(matrix):
    return matrix * matrix.T
