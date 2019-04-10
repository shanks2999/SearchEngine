
import settings
import preprocess
import queue
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request

myList = []
valid_url_set = set()
def plot_web_graph(link, threshold):
    settings.link_set.add(link)
    myList.append(link)
    valid_url_set.add(link)
    with open("./data/all_url" 'a', encoding="utf-8") as fobj:
            fobj.write(link)
            fobj.write("\n")
    fetch_link_graph(threshold)
    # preprocess.export_url_list(myList)

def fetch_link_graph(threshold):
    for index in range(threshold):
        page = requests.get(myList[index])
        soup = BeautifulSoup(page.text, 'html.parser')
        link_list = getAllLinks(myList[index], soup)
        for l in link_list:
            if l not in settings.link_set:
                settings.link_set.add(l)
                myList.append(l)
        if len(myList) > threshold:
            break


#     settings.web_graph[link] = []
#     if final_url in settings.link_set:
#         settings.web_graph[link].append(final_url)
#     try:
#         if count > threshold:
#             return q
#         link = q.get()
#         page = requests.get(link)
#         soup = BeautifulSoup(page.text, 'html.parser')
#
#         # [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
#         # visible_text_A = soup.getText()
#
#         text = filter(tag_visible, soup.findAll(text=True))
#         visible_text_B = u" ".join(t.strip() for t in text)
#
#         data = preprocess.removePunctuation(visible_text_B)
#         data = preprocess.removeDigits(data)
#         tokens = preprocess.tokenizeData(data)
#         tokens = preprocess.removeStopWords(tokens)
#         tokens = preprocess.performStemming(tokens)
#         tokens = preprocess.removeStopWords(tokens)
#         # settings.web_dict[link] = tokens[:]
#         link_list = getAllLinks(link, soup)
#         preprocess.export_spider_sequantial(link, tokens[:], count)
#
#         return scrape(threshold, count + 1)
#
#     except:
#         return scrape(threshold, count)


def web_spider(link, threshold, count):
    q = queue.Queue()
    q.put(link)
    settings.link_set.add(link)
    # page = requests.get(q.get())
    # tree = html.fromstring(page.content)
    # soup = BeautifulSoup(page.text, 'html.parser')
    # name_box = soup.find('p')
    # text = soup.get_text()
    # contents = soup.html.contents
    # [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
    # visible_text = soup.getText()
    #
    # texts = soup.findAll(text=True)
    # visible_texts = filter(tag_visible, texts)
    # gg = u" ".join(t.strip() for t in visible_texts)
    #
    # getAllLinks(link, soup)
    # abc = soup.find_all('a', href=True)
    #
    # print("END")
    scrape(q, threshold, count)
    # print("END")


def scrape(q, threshold, count):
    try:
        if count > threshold:
            return
        link = q.get()
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')

        # [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
        # visible_text_A = soup.getText()

        text = filter(tag_visible, soup.findAll(text=True))
        visible_text_B = u" ".join(t.strip() for t in text)

        data = preprocess.removePunctuation(visible_text_B)
        data = preprocess.removeDigits(data)
        tokens = preprocess.tokenizeData(data)
        tokens = preprocess.removeStopWords(tokens)
        tokens = preprocess.performStemming(tokens)
        tokens = preprocess.removeStopWords(tokens)
        # settings.web_dict[link] = tokens[:]
        link_list = getAllLinks(link, soup)
        for l in link_list:
            if l not in settings.link_set:
                settings.link_set.add(l)
                q.put(l)
        preprocess.export_spider_sequantial(link, tokens[:], count)
        return scrape(q, threshold, count + 1)

    except:
        return scrape(q, threshold, count)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def getAllLinks(link, soup):
    link_list = []
    for l in soup.find_all('a', href=True):
        url = l['href']
        final_url = ""
        if "#" in url:
            url = url[:url.find("#")]
        if url.endswith('/'):
            url = url[:-1]
        if url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.png')):
            continue
        if len(url) > 1:
            if url.startswith('/'):
                final_url = link + url
            elif url.startswith('http'):
                final_url = url
            else:
                final_url = link + "/" + url
        if final_url != "":
            domain = final_url[final_url.find('//') + 2:]
            if domain.find('/') > -1:
                domain = domain[:domain.find('/')]
            if domain.endswith('uic.edu'):
                if final_url in valid_url_set:
                    link_list.append(final_url)
                elif is_valid_url(final_url):
                    link_list.append(final_url)

    return link_list[:]


def is_valid_url(url):
    try:
        if urllib.request.urlopen(url).getcode() == 200:
            valid_url_set.add(url)
            return True
        else:
            return False
    except:
        return False
