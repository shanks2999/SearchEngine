import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import preprocess
from operator import itemgetter

myList = []
link_set = set()
removed_links = set()
web_graph = OrderedDict()

pageRank = []


def PAGE_RANK(web_graph_new):
    # web_graph_new = preprocess.import_web_graph()

    out_link_count = dict()
    for node in web_graph_new:
        for connectedNodes in web_graph_new[node]:
            if connectedNodes not in out_link_count:
                out_link_count[connectedNodes] = 0
            out_link_count[connectedNodes] += 1

    N = len(web_graph_new)
    B = 0.15 * (1 / N)
    newScores = OrderedDict()
    oldScores = OrderedDict()

    for node in web_graph_new:
        oldScores[node] = 1/N
        newScores[node] = 1/N
    for iteration in range(10):
        for node in web_graph_new:
                summation = 0
                for connectedNodes in web_graph_new[node]:
                    summation += oldScores[connectedNodes] / out_link_count[connectedNodes]
                newScores[node] = (0.85 * summation) + B
        oldScores = newScores.copy()
        pageRank = oldScores.copy()
    pageRank = OrderedDict(sorted(pageRank.items(), key=itemgetter(1), reverse=True))
    return pageRank


def populate_web_graph(threshold):
    index = 0
    count = 1
    while count <= threshold:
        try:
            page = requests.get(myList[index])
            if int(page.status_code) != 200:
                if myList[index] in web_graph:
                    del web_graph[myList[index]]
                    removed_links.add(myList[index])
                index += 1
                continue
            soup = BeautifulSoup(page.text, 'html.parser')
        except:
            index += 1
            continue

        current_links = getAllLinks(myList[index], soup)
        for link in current_links:
            if link not in removed_links:
                if link not in web_graph:
                    web_graph[link] = set()
                web_graph[link].add(myList[index])

            if link[link.find("//")+2:] not in link_set:
                link_set.add(link[link.find("//") + 2:])
                myList.append(link)
        index += 1
        if count%10 == 0:
            print(count)
        count += 1


def getAllLinks(link, soup):
    current_list = []
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
                current_list.append(final_url)

    return current_list[:]


def main():
    link = "https://www.cs.uic.edu"
    link_set.add(link[link.find("//")+2:])
    myList.append(link)
    populate_web_graph(3000)
    preprocess.export_web_graph(web_graph)
    web_graph_new = preprocess.import_web_graph()
    page_rank = PAGE_RANK(web_graph_new)
    preprocess.export_page_rank(page_rank)
    print("Done")


if __name__ == '__main__':
    main()
