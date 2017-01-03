from ProductProcesser import *
from ProductReader import *
from Standardizer import *
from SpecsReader import *
from Quantizer import *
from BsonIO import *
from CommonFieldQuantizer import *

def regenerateOutputs(): 
    generateSpecsStatistics()
    preprocessData()

def main():
    #generateFieldsExpandedProducts(printing = False)
    #products = readProducts(fileName = 'expandedProducts.bson', decoding = None)
    #generateCommonFieldList(products = products)
    #checkCommonFieldsCount(products)
    #generateCommonFieldStatistics(products)
    #generateCommonFieldsValueMap(products, regenerate = False)
    #generateCommonFieldValueLists(products = products,printing = False)
    #generateNotNullCommonFieldValueLists(products = products)
    #generateCommonFieldsMeanMap()
    #generateCommonFieldsSDMap()
    generateCommonFieldsZ_ScoredMap()
    categories = evalBson('categories.bson')
    map = {}
    for c in categories['data']['categories']:
        map[c['categoryCode']] = c['categoryName']
    writeToBson(map, 'categoryCodeNams.json') 
    print 'DONE'


main()
