import sys
from bottle import route, run, template, view, request, response, static_file
from os import path
import pickle

# adding main project path
sys.path.append(path.join(path.dirname(__file__), "../"))

import twitter
import articles
from algorithm_test import Topic, Document

# getting current twitter trends and caching
trend_topics = twitter.get_trends()

# getting dev and eval sets
topics = pickle.load(open("../dev_set.p", "rb"))
print topics

@route('/')
@view('topic')
def index():
    ret = dict()
    ret['trend_topics'] = trend_topics
    return ret

@route('/topic/<name>')
@route('/topic')
@view('topic')
def topic(name=None):
    if not name:
        if 'q' in request.query:
            name = request.query['q']
        else:
            name = "starbucks"  # example query

    # TODO: query our system and receive result

    topic = None
    for top in topics:
        if top.topic == name:
            topic = top

    if topic:
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
