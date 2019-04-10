# settings.py
import queue
from collections import OrderedDict


def init():
    global link_set, stop_words, web_dict, web_graph
    link_set = set()
    stop_words = set()
    web_dict = OrderedDict()
    web_graph = OrderedDict()

    with open("./stopwords.txt") as fobj:
        for line in fobj:
            stop_words.add(line.strip())
