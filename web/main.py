import sys
import bottle
from bottle import route, run, template, view, request, response, static_file
from os import path
import pickle

# adding main project path
sys.path.append(path.join(path.dirname(__file__), "../"))

import twitter
import articles
from algorithm_test import Topic, Document

__dir = path.dirname(path.realpath(__file__))

# setting right template path
bottle.TEMPLATE_PATH.insert(0, __dir)

# getting current twitter trends and caching
trend_topics = twitter.get_trends()

# getting dev and eval sets
topics_dev = pickle.load(open(path.join(__dir, "../dev_set.p"), "rb"))
topics_eval = pickle.load(open(path.join(__dir, "../eval_set.p"), "rb"))
topics = topics_dev + topics_eval

@route('/')
@view('topic')
def index():
    """ Index page handler """
    # get and return trend topics
    ret = dict()
    ret['trend_topics'] = trend_topics
    return ret

@route('/topic/<name>')
@route('/topic')
@view('topic')
def topic(name=None):
    """ Topic page handler 

    Queries a specific query within our dataset and
    summarize the content.
    """
    if not name:
        if 'q' in request.query:
            name = request.query['q']
        else:
            name = "poison"  # example query

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
@route('/<pathname:re:(img|css|js)(/vendor)?>/<filename>')
def send_image(pathname, filename):
    """ Used to serve static files """
    return static_file(filename, root=path.join(__dir, pathname))


# runs the script
run(host='localhost', port=8080)
