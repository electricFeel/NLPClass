from mturk import MTurkSurveyFactory, ACCESS_ID, SECRET_KEY, HOST, https_connection_factory
from boto.mturk.connection import MTurkConnection
from articles import *
from extractor import *


def build_survey_list(listOfLinks=[]):
    tuple_list = []
    for item in listOfLinks:
        article = build_extractor(item).article()
        print article
        #url, title, first paragraph
        tuple_list.append([item, article['title'], article['paragraphs'][0]])
    print tuple_list
    return tuple_list




if __name__=='__main__':
    fact = MTurkSurveyFactory()
    mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                         aws_secret_access_key=SECRET_KEY,
                         host=HOST, is_secure=True,
                         https_connection_factory=(https_connection_factory, ()))
	#loop over every article
    build_survey_list(mississippi)

