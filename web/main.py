import sys
from bottle import route, run, template, view, request, response, static_file
from os import path

# adding main project path
sys.path.append(path.join(path.dirname(__file__), "../"))

import twitter
import articles
from algorithm_test import Topic

# getting current twitter trends and caching
trend_topics = twitter.get_trends()


@route('/')
@view('topic')
def index():
    ret = dict()
    ret['trend_topics'] = trend_topics
    return ret


# TEMP: fake result
result = {
    'topic': 'Starbucks Poisoning',
    'sentences': [
                    {
                    'sentence': 'A woman has been arrested after she allegedly tried to sneak tainted bottles of orange juice into a refrigerator at a Starbucks coffee shop in San Jose.',
                    'from_article': 'http://www.latimes.com/local/lanow/la-me-ln-woman-tainted-juice-starbucks-20130430,0,362185.story'
                    },
                    { 
                    'sentence': 'Behbehanian could make her first appearance in court as soon as Thursday, authorities said.',
                    'from_article': 'http://www.usatoday.com/story/money/business/2013/04/30/tainted-orange-juice/2125579/'
                    }
                ],
    'articles':
          ['http://www.usatoday.com/story/money/business/2013/04/30/tainted-orange-juice/2125579/',
          'http://www.cnn.com/2013/04/30/justice/california-starbucks-tainted-juice/index.html',
          'http://www.cbsnews.com/8301-504083_162-57582174-504083/poisoned-o.j-placed-in-calif-starbucks-woman-arrested-police-say/',
          'http://abcnews.go.com/blogs/headlines/2013/04/poisoned-oj-slipped-into-starbucks-cold-case/',
          'http://www.latimes.com/local/lanow/la-me-ln-woman-tainted-juice-starbucks-20130430,0,362185.story']
}


@route('/topic/<name>')
@route('/topic')
@view('topic')
def topic(name=None):
    if not name:
        if 'q' in request.query:
            name = request.query['q']
        else:
            name = "starbucks"  # example query

    print name
    #print articles.total
    # TODO: query our system and receive result
    if name in articles.total:
        topic = Topic(name)
        for url in articles.total[name]:
            topic.add_document(url=url)
        topic.summarize()
        result = {
            'topic': topic.topic,
            'sentences': topic.summary,
            'articles': topic.urls
        }
    else:
        result = {}
        pass  # not found

    ret = dict()
    ret.update(result)
    ret['trend_topics'] = trend_topics
    return ret


# serving static files
@route('/<path:re:(img|css|js)(/vendor)?>/<filename>')
def send_image(path, filename):
    return static_file(filename, root=path)


# runnning
run(host='localhost', port=8080)
