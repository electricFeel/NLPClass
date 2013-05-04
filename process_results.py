import os
import csv

class Results:
    """Maintains a table of results"""
    result_set = dict()
    def process_csv(self, f):
        print f
        with open(f, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            header = reader.next()
            for row in reader:
                #each row represents one worker
                answers = []
                for x in range(8, len(row)):
                    answers.append(row[x])
                #need to 

                



if __name__ == "__main__":
    os.chdir('results')
    result = Results()
    for f in os.listdir('.'):
        if f.endswith('.csv'):
            result.process_csv(f)
        break