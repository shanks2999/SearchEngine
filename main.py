import settings
import preprocess
import compute
from collections import OrderedDict
import crawl
from flask import Flask

url_list = []

def TF_IDF(query):
    tokenCollection = []
    count = 0
    for key in settings.web_dict:
        tokenCollection.append(settings.web_dict[key])
        url_list.append(key)

    queries = preprocess.removePunctuation(query.lower())
    queries = preprocess.removeDigits(queries)
    tokenQueries = preprocess.tokenizeData(queries)
    tokenQueries = preprocess.removeStopWords(tokenQueries)
    tokenQueries = preprocess.performStemming(tokenQueries)
    tokenQueries = preprocess.removeStopWords(tokenQueries)

    invertedIndex, vocabulary, docSet = compute.buildInvertedIndex(tokenCollection)
    documentModel = compute.buildVectorSpaceModel(tokenCollection, invertedIndex, vocabulary)
    queryModel = compute.transformIntoVectorSpaceModel(tokenQueries, invertedIndex, vocabulary, len(tokenCollection))

    cosineSimilarity, cosineSimilaritySorted = compute.getCosineSimilarity(documentModel, queryModel, vocabulary,
                                                                           tokenQueries, docSet)
    return cosineSimilarity, cosineSimilaritySorted
    # compute.writeTop500DocumentPairs(cosineSimilarity, cosineSimilaritySorted)
    # compute.writeAveragePrecisionRecall(cosineSimilaritySorted, relevance)



def write_results(cosineSimilarity, cosineSimilaritySorted, page_rank):
    top_200_dict = OrderedDict()
    top_200_ordered = OrderedDict()
    for index in range(len(cosineSimilaritySorted)):
        if cosineSimilarity[cosineSimilaritySorted[index]] <= 0 or len(top_200_dict) >= 200:
            break
        else:
            top_200_dict[url_list[cosineSimilaritySorted[index]]] = cosineSimilaritySorted[index]
    for key in page_rank:
        if key in top_200_dict:
            top_200_ordered[key] = top_200_dict[key]
    if len(top_200_ordered) < len(top_200_dict):
        for key in top_200_dict:
            if key not in top_200_ordered:
                top_200_ordered[key] = top_200_dict[key]

    with open("./results/top_200_pages", 'w', encoding="utf-8") as fobj:
        for key in top_200_ordered:
            fobj.write(key)
            fobj.write("\n")
    with open("./results/top_200_SimilarityScore", 'w', encoding="utf-8") as fobj:
        for key in top_200_ordered:
            fobj.write(str(cosineSimilarity[top_200_ordered[key]]))
            fobj.write("\n")
    with open("./results/top_200_PageRankScore", 'w', encoding="utf-8") as fobj:
        for key in top_200_ordered:
            fobj.write(str(page_rank[key]))
            fobj.write("\n")



def main(query):
    # query = "cornelia caragea"
    settings.init()
    import time
    start = time.time()
    preprocess.import_crawled_data(3000)
    cosineSimilarity, cosineSimilaritySorted = TF_IDF(query)
    page_rank = preprocess.import_page_rank()
    write_results(cosineSimilarity, cosineSimilaritySorted, page_rank)
    end = time.time()
    print(end - start)
    print("END")


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
    # main()