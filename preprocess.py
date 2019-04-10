import settings
import numpy as np
import nltk
from nltk.stem import PorterStemmer
from collections import OrderedDict
import pickle


def export_page_rank(page_rank):
    with open('./data/page_rank.p', 'wb') as fp:
        pickle.dump(page_rank, fp, protocol=pickle.HIGHEST_PROTOCOL)


def import_page_rank():
    with open('./data/page_rank.p', 'rb') as fp:
        page_rank = pickle.load(fp)
    return page_rank


def import_crawled_data(threshold):
    for index in range(1, threshold+1):
        try:
            with open('./data/' + str(index), 'r',  encoding="utf-8") as fp:
                data = fp.read().splitlines()
                settings.web_dict[data[0]] = tokenizeData(data[1])
        except:
            settings.web_dict[data[0]] = []


def export_web_graph(data):
    with open('./data/web_graph.p', 'wb') as fp:
        pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)

def import_web_graph():
    with open('./data/web_graph.p', 'rb') as fp:
        data = pickle.load(fp)
    return data


def export_url_list(url_list):
    with open("./data/all_url" 'w', encoding="utf-8") as fobj:
        for link in url_list:
            fobj.write(link)
            fobj.write("\n")

def export_spider():
    count = 1
    for key in settings.web_dict:
        with open("./data/"+str(count)+"", 'w', encoding="utf-8") as fobj:
            fobj.write(key)
            fobj.write("\n")
            fobj.write(" ".join(str(x) for x in settings.web_dict[key]))
        count += 1


def export_spider_sequential(link, tokens, count):
    with open("./data/"+str(count)+"", 'w', encoding="utf-8") as fobj:
        fobj.write(link)
        fobj.write("\n")
        fobj.write(" ".join(str(x) for x in tokens))


def removePunctuation(data):
    import string
    table = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    return data.translate(table)


def removeDigits(data):
    from string import digits
    table = str.maketrans(digits, ' '*len(digits))
    return data.translate(table)


def tokenizeData(data):
    return nltk.word_tokenize(data)


def removeStopWords(tokens):
    temp = []
    for word in tokens:
        if word not in settings.stop_words and len(word) > 2:
            temp.append(word)
    return temp[:]


def performStemming(tokens):
    ps = PorterStemmer()
    temp = []
    for word in tokens:
        temp.append(ps.stem(word))
    return temp[:]
