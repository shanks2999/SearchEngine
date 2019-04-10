from collections import OrderedDict
from operator import itemgetter
import numpy as np


def buildInvertedIndex(tokenCollection):
    from collections import OrderedDict
    invertedIndex = OrderedDict()
    vocabulary = {}
    docSet = []
    index = 0
    for d in range(len(tokenCollection)):
        temp = set()
        for word in tokenCollection[d]:
            temp.add(word)
            if word not in invertedIndex:
                invertedIndex[word] = {}
                invertedIndex[word][d] = 1
                vocabulary[word] = index
                index += 1
            else:
                if d not in invertedIndex[word]:
                    invertedIndex[word][d] = 0
                invertedIndex[word][d] += 1
        docSet.append(temp.copy())
    return invertedIndex, vocabulary, docSet


def buildVectorSpaceModel(tokenCollection, invertedIndex, vocabulary):
    import numpy
    import math
    N = len(tokenCollection)
    vectorSpaceModel = numpy.zeros((N, len(vocabulary)))
    for d in range(len(tokenCollection)):
        # max = 0
        # for w in docSet[d]:
        #     if invertedIndex[w][d] > max:
        #         max = invertedIndex[w][d]
        for term in tokenCollection[d]:
            if term in vocabulary:
                vectorSpaceModel[d][vocabulary[term]] = (invertedIndex[term][d] if d in invertedIndex[term] else 0) * math.log2(N/len(invertedIndex[term]))
    return vectorSpaceModel


def transformIntoVectorSpaceModel(tokenCollection,  invertedIndex, vocabulary, N):
    import numpy
    import math
    vectorSpaceModel = numpy.zeros((1, len(vocabulary)))
    # collection = getFrequencyPerDocument(tokenCollection)
    for term in tokenCollection:
        if term in vocabulary:
            vectorSpaceModel[0][vocabulary[term]] = math.log2(N/len(invertedIndex[term]))
    return vectorSpaceModel


def getCosineSimilarity(documentModel, queryModel, vocabulary, tokenQueries, docSet):
    import numpy
    numpy.seterr(invalid='ignore')
    import math
    cs = numpy.zeros(documentModel.shape[0])

    for d in range(documentModel.shape[0]):
        a = 0
        b = 0
        c = 0
        for term in tokenQueries:
            if term in vocabulary:
                a += (documentModel[d][vocabulary[term]] * queryModel[0][vocabulary[term]])
                c += queryModel[0][vocabulary[term]] ** 2
        for term in docSet[d]:
            b += documentModel[d][vocabulary[term]] ** 2
        cs[d] = a/(math.sqrt(b)*math.sqrt(c))
    return cs, np.argsort(-cs)


def writeTop500DocumentPairs(cosineSimilarity, cosineSimilaritySorted):
    with open("./output_relevance.txt", 'w') as fobj:
        for i in range(len(cosineSimilaritySorted)):
            cs = cosineSimilarity[i]
            s = "Query " + str(i+1) + ": \n" + str([x+1 for x in cosineSimilaritySorted[i][::-1][:500]]) + "\n\n\n\n"
            fobj.write(s)


def calculatePrecisionRecall(cosineSimilaritySorted, relevance, top):
    import numpy as np
    pr = {}
    pList=[]
    rList=[]
    N = len(cosineSimilaritySorted[0])

    for i in range(len(relevance)):
        count = 0
        for j in range(N-1, N-1-top, -1):
            if (cosineSimilaritySorted[i][j]+1) in relevance[i+1]:
                count += 1

        p = count / top
        r = count / len(relevance[i+1])
        pList.append(p)
        rList.append((r))
    pr["p"] = pList[:]
    pr["r"] = rList[:]
    pr["ap"] = np.array(pList).mean()
    pr["ar"] = np.array(rList).mean()
    return pr.copy()


def writeAveragePrecisionRecall(cosineSimilaritySorted, relevance):
    pr = {}
    pr[10] = calculatePrecisionRecall(cosineSimilaritySorted, relevance, 10)
    pr[50] = calculatePrecisionRecall(cosineSimilaritySorted, relevance, 50)
    pr[100] = calculatePrecisionRecall(cosineSimilaritySorted, relevance, 100)
    pr[500] = calculatePrecisionRecall(cosineSimilaritySorted, relevance, 500)

    with open("./output_precision_recall.txt", 'w') as fobj:
        for key in pr:
            fobj.write("\nTop "+str(key)+ " documents in rank list")
            for j in range(len(relevance)):
                fobj.write('\nQuery: ' + str(j+1) + "\t\tPr: " + str(pr[key]["p"][j]) + "\t\tRe: " + str(pr[key]["r"][j]))
            fobj.write("\nAvg Preciion: \t" + str(pr[key]["ap"]))
            fobj.write("\nAvg Recall: \t" + str(pr[key]["ar"]))
            fobj.write("\n\n")











def calculatePageRankScore(theList):
    pageRank = []
    for i in range(len(theList)):
        newScores = OrderedDict()
        oldScores = OrderedDict()
        N = len(theList[i])
        B = 0.15 * (1/N)
        for node in theList[i]:
            oldScores[node] = 1/N
            newScores[node] = 1/N
        for iteration in range(10):
            for node in theList[i]:
                summation = 0
                for connectedNodes in theList[i][node]:
                    summation += theList[i][node][connectedNodes] / \
                                 sum([theList[i][connectedNodes][x] for x in theList[i][connectedNodes]]) * \
                                 oldScores[connectedNodes]
                newScores[node] = (0.85 * summation) + B
            oldScores = newScores.copy()
        pageRank.append(oldScores.copy())
    return pageRank


def calculateNGrams_PR(tokenUpdated, pageRank):
    nGrams = []
    for i in range(len(tokenUpdated)):
        myGrams = OrderedDict()
        for j in range(len(tokenUpdated[i])):
            if tokenUpdated[i][j] != "":
                if tokenUpdated[i][j] not in myGrams:
                    myGrams[tokenUpdated[i][j]] = pageRank[i][tokenUpdated[i][j]]
                if (j+1) < len(tokenUpdated[i]) and tokenUpdated[i][j+1] != "":
                    if (tokenUpdated[i][j] + " " + tokenUpdated[i][j+1]) not in myGrams:
                        myGrams[tokenUpdated[i][j] + " " + tokenUpdated[i][j+1]] = pageRank[i][tokenUpdated[i][j]] + pageRank[i][tokenUpdated[i][j+1]]

                    if (j+2) < len(tokenUpdated[i]) and tokenUpdated[i][j + 2] != "":
                        if (tokenUpdated[i][j] + " " + tokenUpdated[i][j + 1] + " " + tokenUpdated[i][j + 2]) not in myGrams:
                            myGrams[tokenUpdated[i][j] + " " + tokenUpdated[i][j + 1] + " " + tokenUpdated[i][j + 2]] = pageRank[i][tokenUpdated[i][j]] + \
                                                                                                                        pageRank[i][tokenUpdated[i][j + 1]] + \
                                                                                                                        pageRank[i][tokenUpdated[i][j+2]]
        myGrams = OrderedDict(sorted(myGrams.items(), key = itemgetter(1), reverse = True))
        nGrams.append(myGrams.copy())
    return nGrams


def calculateNGrams_TFIDF(tokenUpdated, documentModel, vocabulary):
    nGrams = []
    for i in range(len(tokenUpdated)):
        myGrams = OrderedDict()
        for j in range(len(tokenUpdated[i])):
            if tokenUpdated[i][j] != "":
                if tokenUpdated[i][j] not in myGrams:
                    myGrams[tokenUpdated[i][j]] = documentModel[i][vocabulary[tokenUpdated[i][j]]]
                if (j+1) < len(tokenUpdated[i]) and tokenUpdated[i][j+1] != "":
                    if (tokenUpdated[i][j] + " " + tokenUpdated[i][j+1]) not in myGrams:
                        myGrams[tokenUpdated[i][j] + " " + tokenUpdated[i][j+1]] = documentModel[i][vocabulary[tokenUpdated[i][j]]] + documentModel[i][vocabulary[tokenUpdated[i][j+1]]]

                    if (j+2) < len(tokenUpdated[i]) and tokenUpdated[i][j + 2] != "":
                        if (tokenUpdated[i][j] + " " + tokenUpdated[i][j + 1] + " " + tokenUpdated[i][j + 2]) not in myGrams:
                            myGrams[tokenUpdated[i][j] + " " + tokenUpdated[i][j + 1] + " " + tokenUpdated[i][j + 2]] = documentModel[i][vocabulary[tokenUpdated[i][j]]] + \
                                                                                                                        documentModel[i][vocabulary[tokenUpdated[i][j+1]]] + \
                                                                                                                        documentModel[i][vocabulary[tokenUpdated[i][j+2]]]
        myGrams = OrderedDict(sorted(myGrams.items(), key = itemgetter(1), reverse = True))
        nGrams.append(myGrams.copy())
    return nGrams


def calculateMRR(tokenUpdatedGold, nGrams):
    avgMRR = []
    top10MRR = np.zeros((len(nGrams), 10))
    for i in range(len(nGrams)):
        counter = 1
        for key in nGrams[i]:
            if key in tokenUpdatedGold[i]:
                mrr = 1/counter
                for j in range(counter-1, 10):
                    top10MRR[i][j] = mrr
                break
            counter += 1
            if counter > 10:
                break
    for i in range(10):
        avgMRR.append((sum(row[i] for row in top10MRR))/len(nGrams))
    return top10MRR, avgMRR


def buildInvertedIndex(tokenCollection):
    from collections import OrderedDict
    invertedIndex = OrderedDict()
    vocabulary = {}
    docSet = []
    index = 0
    for d in range(len(tokenCollection)):
        temp = set()
        for word in tokenCollection[d]:
            if word != "":
                temp.add(word)
                if word not in invertedIndex:
                    invertedIndex[word] = {}
                    invertedIndex[word][d] = 1
                    vocabulary[word] = index
                    index += 1
                else:
                    if d not in invertedIndex[word]:
                        invertedIndex[word][d] = 0
                    invertedIndex[word][d] += 1
        docSet.append(temp.copy())
    return invertedIndex, vocabulary, docSet


def buildVectorSpaceModel(tokenCollection, invertedIndex, vocabulary):
    import numpy
    import math
    N = len(tokenCollection)
    vectorSpaceModel = numpy.zeros((N, len(vocabulary)))
    for d in range(len(tokenCollection)):
        # max = 0
        # for w in docSet[d]:
        #     if invertedIndex[w][d] > max:
        #         max = invertedIndex[w][d]
        for term in tokenCollection[d]:
            if term != "" and term in vocabulary:
                vectorSpaceModel[d][vocabulary[term]] = (invertedIndex[term][d] if d in invertedIndex[term] else 0) * math.log2(N/len(invertedIndex[term]))
    return vectorSpaceModel
