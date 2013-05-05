import os
import csv
import pprint
from articles import *

class Results:
    """Maintains a table of results. The table is made up of categories that 
       are defined as the article topics (for example the mississippi ricin case). each
       category is made of articles identified by their URL's. Each URL has a number
       of results in it.

       topic->url->answers[sent1...sentn] which maps to
       dict->dict->list
    """
    def __init__(self):
        self.result_set = dict()

    def build_article_dataset(self):
        os.chdir('results')
        for f in os.listdir('.'):
            if f.endswith('.csv'):
                self.process_csv(f)
        print len(self.result_set)

    def get_data(self):
        return self.result_set

    def process_csv(self, f):
        """Processes a CSV file and places the data in a table"""
        with open(f, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            #move past the header
            reader.next()
            for row in reader:
                #each row represents one worker
                answers = []
                for x in range(8, len(row)-1):
                    answers.append(row[x])
                if len(answers) <= 2:
                    print f
                #get the topic that his article belongs to
                cat = total_cat[row[2]] 
                #check to see if we have this category already
                if cat not in self.result_set:
                    self.result_set[cat] = dict()
                #now check to see if the URL already exists in the 
                #topic's dictionary
                if row[2] not in self.result_set[cat]:
                    self.result_set[cat][row[2]] = []
                #sentence is in order
                self.result_set[cat][row[2]].append(answers)




                



if __name__ == "__main__":
    result = Results()
    result.build_article_dataset()
    print result.get_data()