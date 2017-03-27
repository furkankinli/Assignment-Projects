from MainSrc.PythonVersionHandler import *
from . import SparkLogReader as LogReader
from Sparker.PySparkImports import *
from .SparkLogFileHandler import *
from LogProcesser.JsonIO import *
from paths import *

def unique(list1):
    return list(set(list1))

def checkDuplication():
    logs = LogReader.readLogs(TEST_LOGS, duplicated = True)
    deduplicatedLogs = unique(logs)
    logsCount = len(logs)
    deduplicatedLogsCount = len(deduplicatedLogs)
    duplicationCount = logsCount - deduplicatedLogsCount
    duplicated = logsCount != deduplicatedLogsCount
    print_('Duplication occurred:', duplicated, duplicationCount, logsCount, deduplicatedLogsCount)

def generateParsedTestFile(fromFileName = TEST_LOGS, toFileName = joinPath(testFolder, TEST_LOGS_FILE)):
    LogReader.generateParsedLogs(fromFileName, toFileName)

def infoExists(fileName):
    return os.path.exists(fileName + '.json')

def extractLogKeys(logs = None, fromFileName = TEST_LOGS, toFileName = 'keyList'):
    logs = getLogs(logs, fromFileName)
    def keysUpdater(log): return list(log.keys())
    keys = logs.map(keysUpdater).reduce(lambda a, b: unique(a+b))
    if LogReader.WRITING_ALLOWED:
        writeToJson(keys, joinPath(testFolder, toFileName))
    return keys   
    
def readLogKeys(logs = None, fileName = 'keyList'):
    fileName = joinPath(testFolder, fileName)
    if not (infoExists(fileName) and LogReader.WRITING_ALLOWED):
        return extractLogKeys(logs)
    return evalJson(fileName)

def getSnippedLogs(keys, logs = None, fromFileName = TEST_LOGS, toFileName = 'transpose'): 
    logs = getLogs(logs, fromFileName)
    if isinstance(keys, str):
        keys = [keys]
    def getSnippedLog(log):
        snippedLog = {}
        for key in keys:
            if key in log.keys():
                snippedLog[key] = log[key]
            else:
                snippedLog[key] = None
        return snippedLog
    return logs.map(getSnippedLog)

transpose = None
transposeClean = None
def takeTransposesOfLogs(logs = None, fromFileName = TEST_LOGS, toFileName = 'transpose'):
    logs = getLogs(logs, fromFileName)
    logKeys = readLogKeys(logs)
    global transpose, transposeClean
    transpose = {}
    transposeClean = {}
    for key in logKeys:
        transpose[key] = sc_().emptyRDD()
        transposeClean[key] = sc_().emptyRDD()
    def rowToColumn(log):
        for key in logKeys:
            if key in log.keys():
                transpose[key].union(log[key])
                transposeClean[key].union(log[key])
                print_(transpose[key].count())
            else:
                transpose[key].union(None)
    logs.foreach(rowToColumn)
    if LogReader.WRITING_ALLOWED:
        writeToJson(transpose, joinPath(testFolder, toFileName))
        writeToJson(transposeClean, joinPath(testFolder, toFileName + '_clean'))
    else:
        print_('Transposes has been generated' )
    return transpose, transposeClean
    
def readTransposes(logs = None, fileName = 'transpose'):
    fileName = joinPath(testFolder, fileName)
    if not (infoExists(fileName) and LogReader.WRITING_ALLOWED):
        return takeTransposesOfLogs(logs)
    return evalJson(fileName), evalJson(fileName + '_clean')

def getSubTranspose(keys, logs = None, fromFileName = TEST_LOGS): 
    if transpose == None:
        logs = getLogs(logs, fromFileName)
        subTranspose = {}
        for key in keys:
            subTranspose[key] = RDD()
        for log in logs:
            for key in keys:
                subTranspose[key] = log[key] if key in log.keys() else None 
        return subTranspose
    else:
        return  {key: transpose[key] for key in keys}

def extractCounts(logs = None, fromFileName = TEST_LOGS, toFileName = 'counts'):
    logs = getLogs(logs, fromFileName)
    logKeys = readLogKeys(logs)
    transpose, cleenTranspose = readTransposes(logs)
    totalCounts = {}
    valueCounts = {}
    for key in logKeys:
        totalCounts[key] = cleenTranspose[key].count()
        valueCounts[key] = cleenTranspose[key].distinct().count()
    if LogReader.WRITING_ALLOWED:
        writeToJson(totalCounts, joinPath(testFolder, toFileName + 'OfValues'))
        writeToJson(valueCounts, joinPath(testFolder, toFileName + 'OfUniqueValues'))
    return totalCounts, valueCounts
    
def readCounts(logs = None, fileName = 'counts'):
    totalCountsFileName = joinPath(testFolder, fileName + 'OfValues')
    valueCountsFileName = joinPath(testFolder, fileName + 'OfUniqueValues')
    if not (infoExists(fileName) and LogReader.WRITING_ALLOWED):
        return extractCounts(logs)
    return evalJson(totalCountsFileName), evalJson(valueCountsFileName)

def getLogsColumnAsList(key, logs = None, fromFileName = TEST_LOGS):
    if transpose == None:
        logs = getLogs(logs, fromFileName)
        return logs.map(lambda log: log[key] if key in log.keys() else None).collect()
    else:
        return transpose[key]
    
def isMatching(valueMap, log):
    for key, value in valueMap.items():
        if not key in log.keys():
            return False
        elif isinstance(value, list) and log[key] in value:
            return True 
        elif not key in log.keys() or log[key] != value:
            return False
        else:
            return True

def getLogsWhere(valueMap, logs = None): 
    return logs.filter(lambda log: isMatching(valueMap, log))

def getLogsWhereValue(value, key = None, logs = None):
    if key == None:
        logs = getLogs(logs) 
        def keyIterator(log):
            for logKey in log.keys():
                if isMatching({logKey: value}, log):
                    return True 
            return False
        return logs.filter(keyIterator)
    else:
        return getLogsWhere({key: value}, logs)
    
def getModuleMap(logs = None, modules = None): 
    moduleMap = {}
    if modules == None:
        modules = getLogsColumnAsList('module', logs)
    for module in modules:
        moduleMap[module] = getLogsWhereValue(module, 'module', logs = logs)
    return moduleMap

def getModuleCounts(logs = None, modules = None): 
    if logs == None:
        logs = getLogs(logs)
    if isinstance(logs, PipelinedRDD):
        logs = getModuleMap(logs)
    counts = {}
    if modules == None:
        for key, logLists in logs.items():
            counts[key] = logLists.count()
    else:
        for module in modules:
            if module in logs.keys():
                counts[module] = logs[module].count()
            else:
                counts[module] = 0
    return counts

def hasSearchThisProduct(searchLog, productLog):
    if not 'ids' in searchLog.keys() or not 'id' in productLog.keys():
        return False
    if isinstance(searchLog['ids'], str):
        return str(productLog['id']) == searchLog['ids']
    else:
        return productLog['id'] in searchLog['ids'] 

def findProductIndexOnSearch(searchLog, productLog):
    if not 'ids' in searchLog.keys() or not 'id' in productLog.keys():
        return -1
    if isinstance(searchLog['ids'], str):
        return 0 if str(productLog['id']) == searchLog['ids'] else -1
    else:
        return searchLog['ids'].index(productLog['id'])

def logsMatching(first, second, keys = None):
    if keys == None:
        keys = [key for key in first.keys() if key in second.keys()]
    elif isinstance(keys, str):
        keys = [keys]
    for key in keys:
        if key in first.keys() and key in second.keys():
            if first[key] != second[key]:
                return False
    return True

focusedModules = ['newsession', 'search', 'item' 'cart', 'payment']
def getJourneyFromCookie(cookie, logs = None): 
    logs = getLogs(logs) 
    modules = getModuleMap(logs)   
    paymentIds = getLogsColumnAsList('id', modules['payment'])
    cartIds = getLogsColumnAsList('id', modules['cart'])    
    commonIds = [id for id in paymentIds if id in cartIds]
    paymentIdCookies = getSnippedLogs(['id', '_c'], modules['payment'])
    focusedLogs = getLogsWhereValue(focusedModules, 'module', logs)
    paymentIdCookies = paymentIdCookies.collect()
    def select(log):
        for paymentLog in paymentIdCookies:
            if log['module'] =='search': 
                if hasSearchThisProduct(log, paymentLog):
                    return True
            else:
                if logsMatching(log, paymentLog, ['_c']):
                    return True
        return False
    myLogs = focusedLogs.filter(select)
    sampleJourney = getLogsWhereValue(cookie, '_c', myLogs)
    sampleJourney = sampleJourney.sortBy(lambda log: log['timestamp'])
    return sampleJourney

productModules = ['cart', 'payment', 'item']
def getProductLogs(modules):
    if isinstance(modules, PipelinedRDD):
        modules = getModuleMap(modules)   
    logs = sc_().emptyRDD()
    for module in productModules:
        logs.union(modules[module])
    return logs

def getSearchLogs(logs):
    return getLogsWhereValue('search', 'module', logs)

def isProductLog(log):
    return 'module' in list(log.keys()) and log['module'] in productModules

def isSearchLog(log):
    return 'module' in list(log.keys()) and log['module'] == 'search'

def getInterestingCookiesFromKeyword(modules, keyword):
    searches = getLogsWhereValue(keyword, 'keyword', modules['search'])
    productCookies = getLogsColumnAsList('_c', getProductLogs(modules))
    interestingCookies = []
    searchCookies = getLogsColumnAsList('_c', searches)
    for c in productCookies:
        if c in searchCookies and c != None:
            interestingCookies.append(c)
    return unique(interestingCookies)

def getIdsFromSearches(searches):
    if isinstance(searches, dict): searches = [searches]
    ids = []
    def searchId(search):
        if 'ids' in list(search.keys()):
            ids.extend(search['ids'] if isinstance(search['ids'], list) else [search['ids']])
    searches.foreach(searchId)
    return ids

def getInterestingLogsFromKeyword(modules, keyword):
    searches = getLogsWhereValue(keyword, 'keyword', modules['search'])
    ids = getIdsFromSearches(searches)
    interestingCookies = getInterestingCookiesFromKeyword(modules, keyword)
    logs = getLogsWhereValue(interestingCookies, '_c', getProductLogs(modules) + modules['newsession'])
    return logs.filter(lambda log: log.keys() and log['id'] in ids)

def findLastSearchContainsProduct(productLog, journey):
    searches = getLogsWhereValue('search', 'module', journey)
    searches = LogReader.sortedLogs(searches, ascending = True)
    for search, i in searches.zipWithIndex().collect():
        if hasSearchThisProduct(search, productLog):
            return i, findProductIndexOnSearch(search, productLog)
    return -1, -1

def getJourneyByKeyword(modules, keyword):
    if isinstance(keyword, str): 
        keyword = [keyword] 
    if isinstance(modules, PipelinedRDD):
        modules = getModuleMap(modules)   
    searches = getLogsWhereValue(keyword, 'keyword', modules['search'])
    interestingLogs = getInterestingLogsFromKeyword(modules, keyword)
    journey = searches.union(interestingLogs)
    return LogReader.sortedLogs(journey)

def cookieChanged(previousLog, currentLog):
    if previousLog == None or \
        ('_c' in previousLog.keys() and not '_c' in currentLog.keys()) or \
        (not '_c' in previousLog.keys() and '_c' in currentLog.keys()) or \
        (not '_c' in previousLog.keys() and not '_c' in currentLog.keys()):
        return False
    else:
        return previousLog['_c'] != currentLog['_c']

def groupLogsByCookie(logs):
    #logs = LogReader.sortedLogs(logs)   
    #logs = logs.groupBy(lambda log: log['_c'] if '_c' in list(log.keys()) else '0000')
    #def parallelizeLogs(pair): 
    #    return pair[1]
    #return logs.map(parallelizeLogs)
    groupedLogs = []
    logs = logs.collect()
    for i, log in enumerate(logs):
        if i == 0 or cookieChanged(logs[i-1], log):
            groupedLogs.append([])
        groupedLogs[-1].append(log) 
    groupedLogsRDD = []
    for group in groupedLogs:
        groupedLogsRDD.append(group)
    return groupedLogsRDD