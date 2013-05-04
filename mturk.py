#!/usr/bin/env python

from boto.mturk.connection import MTurkConnection
from M2Crypto import httpslib, SSL
from boto.mturk.question import *
import settings
import boto.mturk
import os
import datetime

from nltk import tokenize

ACCESS_ID = ''
SECRET_KEY = ''
HOST = 'mechanicalturk.amazonaws.com'

RANKS = [('Most Important', 5),
         ('Very Important', 4),
         ('Somewhat Important', 3),
         ('Not Very Important', 2),
         ('No Value', 1)]


class MTurkSurveyFactory:
    """ Class is responsible for creating a survey on MTurk from
        a set of paragraphs that are passed to it
    """
    def __init__(self):
        pass

    def submitHITs(self, mtc=None, questionForms=[], max_assignments=5,
                   title='Rank the most important sentences',
                   description='Rank the following sentences by importance',
                   keywords='summary, survey',
                   duration=60*5,
                   reward=0.05):
        """ Creates and submits a list of HITTS with the exact same
            title, descriptions, durations and prices from a list of questions.
        """
        if mtc is None:
            mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                                  aws_secret_access_key=SECRET_KEY,
                                  host=HOST)

        for questionForm in questionForms:
            mtc.create_hit(questions=questionForm[1],
                           max_assignments=max_assignments,
                           title=title,
                           description=description,
                           keywords=keywords,
                           duration=60*60*12,
                           approval_delay=1,
                           annotation=questionForm[0],
                           reward=0.05)
        pass

    def buildSurvey(self, paragraphs=[]):
        """ Builds a survey from the tuple list that is passed and Returns
            a list of question forms that can be used to create HITS on
            MTurk

            Keyword arguements:
            paragraphs -- a list of tuples. Each tuple in the list consists of
                          some identifer for the URL it came from and
                          the paragraph that we're going to split via the NLTK.
                          Item 0 in the tuple is the URL
                          Item 1 is the title of the article
                          Item 2 is the raw text that you want to submit for ranking

        """
        title = ("For each of the paragraphs below, please rank the most "
                 "important sentences with 0 being meaning not very important "
                 "to 5 being the most important")

        description = ("We want you to select the sentences in each "
                       "paragraph that, taken alone, would give you the most "
                       "information.")

        keywords = "summary"

        questionForms = []

        #build a question form for each paragraph
        for item in paragraphs:
            item_id = item[0]
            article_title = item[1]
            raw_text = item[2]
            sentences = tokenize.sent_tokenize(raw_text)
            questionForm = QuestionForm()

            overview = Overview()
            overview.append_field('Title', 'Please ranks the sentences in the text by how important they are')
            overview.append_field('Text', raw_text)
            overview.append_field
            questionForm.append(overview)
            #we need to create a seperate ranking question for each
            #sentence
            for sentence in sentences:
                question = QuestionContent()
                question.append_field('Title', sentence)
                sla = SelectionAnswer(min=1, max=1, style='dropdown',
                                      selections=RANKS,
                                      type='text',
                                      other=False)
                
                q1 = Question(identifier=sentence,
                              content=question,
                              answer_spec=AnswerSpecification(sla),
                              is_required=True)
                questionForm.append(q1)
            questionForms.append([item_id, questionForm])
        
        return questionForms


def https_connection_factory(host, port=None, strict=0, **ssl):
    """HTTPS connection factory that creates secure connections
    using M2Crypto."""
    ctx = SSL.Context('tlsv1')
    ctx.set_verify(SSL.verify_peer | SSL.verify_fail_if_no_peer_cert, depth=9)
    ctx.load_client_ca('cacert.pem')
    return httpslib.HTTPSConnection(host, port=port, strict=strict,
                                    ssl_context=ctx)

def test():
    text = ("Two young men with backpacks walked with purpose down "
            "Boylston Street Monday afternoon, weaving through the "
            "crowd on the sidelines of the Boston Marathon. It seemed "
            "like they'd been there before, like they knew where they "
            "were going.")
    title = "From backpacks to 'flash-bangs': Boston's week of terror"
    url = "http://www.cnn.com/2013/04/21/us/boston-week-review/?hpt=hp_t1"
    
    fact = MTurkSurveyFactory()
    questionForms = fact.buildSurvey([[url, title, text]])
    print 'getting account balance'
    
    mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                         aws_secret_access_key=SECRET_KEY,
                         host=HOST, is_secure=True,
                         https_connection_factory=(https_connection_factory, ()))
    fact.submitHITs(mtc=mtc, questionForms=questionForms)
    print mtc.get_account_balance()

if __name__ == "__main__":
  test()