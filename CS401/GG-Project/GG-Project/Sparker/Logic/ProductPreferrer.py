from Sparker.SparkLogProcesser.SparkLogOperator import *
from Sparker.SparkLogProcesser.SparkLogReader import *
from Sparker.SparkLogProcesser.SparkLogAnalyzer import *
from Sparker.SparkLogProcesser.SparkLogFileHandler import *
from MainSrc.PythonVersionHandler import *
from Sparker.PySparkImports import *
import Sparker.SparkLogProcesser.SparkLogAnalyzer as SLA

def getListedIdsFromJourney(journey):
    searches = journey.filter(SLA.isSearchLog)
    return getIdsFromSearches(searches)#sc_().parallelize().distinct()#unique()

def getLoggedIds(journey, module):
    interestingLogs = sortedLogs(journey.filter(lambda log: log['module'] == module))
    return interestingLogs.map(lambda log: (log['id']))

def printActionsByModule(logs, module):
    printActions(logs.filter(lambda log: log['module'] == module))

def summaryIds(ids):
    #print_(ids['listed'])
    #print_(ids['paidCnt'].collect())
    #print_(ids['cartCnt'].collect())
    #print_(ids['clickedCnt'].collect())
    print_('Listed counts =', len(ids['listed']), 'Paid counts =', ids['paidCnt'].count(), 
           'Cart counts =', ids['cartCnt'].count(), 'Clicked counts =', ids['clickedCnt'].count())# ids['listed'].count(), 
    
def cleanCount(ids):
    #ids['cartCnt'] = ids['cartCnt'].subtractByKey(ids['paidCnt'])
    #ids['clickedCnt'] = ids['clickedCnt'].subtractByKey(ids['paidCnt']).subtractByKey(ids['cartCnt'])
    #return ids 
    s = ids['listed']
    ids['paidCnt'] = ids['paidCnt'].filter(lambda l: l[0] in s)
    ids['cartCnt'] = ids['cartCnt'].filter(lambda l: l[0] in s).subtractByKey(ids['paidCnt'])
    ids['clickedCnt'] = ids['clickedCnt'].filter(lambda l: l[0] in s).subtractByKey(ids['paidCnt']).subtractByKey(ids['cartCnt'])
    return ids 

def countIds(ids):
    for process in ['paid', 'cart', 'clicked']:
        ids[process+'Cnt'] =  sc_().parallelize(ids[process].countByValue().items())
    return ids

def modulizeIds(journey):
    productLogs = journey.filter(isProductLog)
    ids = { 
    'listed': getListedIdsFromJourney(journey),
    'paid': getLoggedIds(productLogs, 'payment'),
    'cart': getLoggedIds(productLogs, 'cart'),
    'clicked': getLoggedIds(productLogs, 'item') }
    #summaryIds(ids)
    ids = countIds(ids)
    summaryIds(ids)
    ids = cleanCount(ids)
    summaryIds(ids)
    return ids

def keyPairIds(id1, id2):
    return str(id1) + '_' + str(id2)

positive = 1
negative = -1

def getLabeledPairsWithModulizedIds(journey):
    ids = modulizeIds(journey)
    paidCnt = ids['paidCnt'].collect()
    cartCnt = ids['cartCnt'].collect()
    clickedCnt = ids['clickedCnt'].collect()
    labeledPairs = {}

    def addDominantPair(id1, id2): 
        if id1 != id2:
            labeledPairs[keyPairIds(id1, id2)] = positive
            labeledPairs[keyPairIds(id2, id1)] = negative

    def labelByValues(v1, v2):
        return positive if v1 > v2 else negative

    def addPairByValue(id1, id2, v1, v2): 
        #if v1 == v2: return 
        if id1 != id2:
            labeledPairs[keyPairIds(id1, id2)] = labelByValues(v1, v2)
            labeledPairs[keyPairIds(id2, id1)] = labelByValues(v2, v1)

    for paidId, pCount in paidCnt:
        for paidId2, pCount2 in paidCnt:
             addPairByValue(paidId, paidId2, pCount, pCount2)
        for cartId, cartCount in cartCnt:
             addDominantPair(paidId, cartId)
        for clickedId, clickedCount in clickedCnt:
             addDominantPair(paidId, clickedId)
             
    for cartId, cartCount in cartCnt:
        for cartId2, cartCount2 in cartCnt:
             addPairByValue(cartId, cartId2, cartCount, cartCount2)
        for clickedId, clickedCount in clickedCnt:
             addDominantPair(cartId, clickedId)
             
    for clickedId, clickedCount in clickedCnt:
        for clickedId2, clickedCount2 in clickedCnt:
             addPairByValue(clickedId, clickedId2, clickedCount, clickedCount2)
    #labeledPairs.saveAsTextFile('hdfs://osldevptst01.host.gittigidiyor.net:8020/user/root/data/part0&1_iphone_6')
    ids['labeledPairs'] = sc_().parallelize([(key, v) for key, v in labeledPairs.items()])
    print_(ids['labeledPairs'].count(), ' labeled pairs has been generated by', nowStr())
    return ids

def getInterestingIds(journey): 
    labeledPairs = getLabeledPairsWithModulizedIds(journey)
    #print_(labeledPairs)
    return labeledPairs