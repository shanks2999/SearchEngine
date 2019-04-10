import settings
import preprocess
import urllib.request
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import httplib2


h = httplib2.Http()
myList = []


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def crawl_and_fetch(threshold):
    index = 0
    count = 1
    while count <= threshold or index >= len(myList):
        try:
            page = requests.get(myList[index])
            if int(page.status_code) != 200:
                index += 1
                continue
            soup = BeautifulSoup(page.text, 'html.parser')
        except:
            index += 1
            continue
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
        getAllLinks(myList[index], soup)
        with open("./data/all_url", 'a', encoding="utf-8") as fobj:
            fobj.write(myList[index])
            fobj.write("\n")
        preprocess.export_spider_sequential(myList[index], tokens[:], count)
        index += 1
        count += 1


# def fetch_link_graph(threshold):
#     for index in range(threshold):
#         page = requests.get(myList[index])
#         soup = BeautifulSoup(page.text, 'html.parser')
#         getAllLinks(myList[index], soup)
#         if len(myList) > threshold:
#             break


def getAllLinks(link, soup):
    for l in soup.find_all('a', href=True):
        url = l['href']
        final_url = ""
        if "#" in url:
            url = url[:url.find("#")]
        if url.endswith('/'):
            url = url[:-1]
        if url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.png')) or url.rfind(":") > 6 or "@" in url:
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
                if final_url[final_url.find("//")+2:] not in settings.link_set:
                    settings.link_set.add(final_url[final_url.find("//")+2:])
                    myList.append(final_url)


def is_valid_url(url):
    try:
        # resp = h.request(url, 'HEAD')
        # if int(resp[0]['status']) == 200:
        urlopen(url)
        return True
        # else:
        #     return False

        # r = requests.head(url)
        # if int(r.status_code) == 200:
        #     return True
        # else:
        #     return False
    except:
        return False


def main():
    settings.init()
    link = "https://www.cs.uic.edu"
    with open("./data/all_url", 'w', encoding="utf-8") as fobj: pass
    settings.link_set.add(link[link.find("//")+2:])
    myList.append(link)
    crawl_and_fetch(3000)


if __name__ == '__main__':
    import sys
    main()
