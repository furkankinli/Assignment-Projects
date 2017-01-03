from ProductProcesser import *
import math

def generateCommonFieldsValueMap(products = None, fileName = 'commonFieldValueMap.bson', regenerate = False):
    products = readProducts(products)
    statistics = readCommonFieldStatistics(products, regenerate)
    fieldsValueMap = {}
    for field in statistics['fieldList']:
        if statistics['fieldValueTypes'][field] == 'str':
            if not field in ['title','subTitle']:
                valueMap = {}
                count = 1
                for value in statistics['fieldValueSets'][field]:
                    if type(value) is str: 
                        value = value.decode('utf-8') 
                    valueMap[value] = count
                    count += 1
                fieldsValueMap[field] = valueMap
        elif statistics['fieldValueTypes'][field] == 'bool': 
            fieldsValueMap[field] = {False: 1, True: 2}
    writeToBson(fieldsValueMap, fileName)

def readCommonFieldValueMap(fileName = 'commonFieldValueMap.bson'):
    return evalBson(fileName)

def generateNotNullCommonFieldValueLists(products = None, fileName = 'commonFieldNotNullValueLists.bson', regenerate = False):
    products = readProducts(products)
    statistics = readCommonFieldStatistics(products, regenerate)
    fieldValueMap = readCommonFieldValueMap()
    fieldsValueLists = {}
    for field in statistics['fieldList']:
        valueList = statistics['fieldValueLists'][field]
        if statistics['fieldValueTypes'][field] in ['str', 'bool'] and  not field in ['title','subTitle']:
            for i in range(len(valueList)):
                valueList[i] = fieldValueMap[field][str(valueList[i])]
        if field in ['cargoInfo_cargoFees_ABROAD_fee', 'cargoInfo_cargoFees_DOMESTIC_fee', 'member_soldCount','member_storeId']:
            fieldsValueLists[field] = [v if v != None else 0 for v in valueList]
        elif field is 'productModifiedDate':
            fieldsValueLists[field] = [product['productModifiedDate'] if product['productModifiedDate'] != None else product['startDate'] for product in products]
        else:
            fieldsValueLists[field] = valueList
    writeToBson(fieldsValueLists,fileName, sort = False) 

def readeNotNullCommonFieldValueLists(fileName = 'commonFieldNotNullValueLists.bson'):
    return evalBson(fileName)

def generateCommonFieldsMeanMap(products = None, fileName = 'commonFieldMeanMap.bson', regenerate = False):
    products = readProducts(products)
    statistics = readCommonFieldStatistics(products, regenerate)
    fieldValueMap = readeNotNullCommonFieldValueLists()
    meanMap = {}
    for field in statistics['fieldList']:
        if not field in ['title','subTitle', 'specs']:
            valueList = fieldValueMap[field]
            sum = 0.0
            for v in valueList: sum += v 
            meanMap[field] = sum / len(valueList)
    writeToBson(meanMap, fileName)

def readeCommonFieldsMeanMap(fileName = 'commonFieldMeanMap.bson'):
    return evalBson(fileName)

def generateCommonFieldsSDMap(products = None, fileName = 'commonFieldSDMap.bson', regenerate = False):
    products = readProducts(products)
    statistics = readCommonFieldStatistics(products, regenerate)
    fieldValueMap = readeNotNullCommonFieldValueLists()
    meanMap = readeCommonFieldsMeanMap()
    SDMap = {}
    for field in statistics['fieldList']:
        if not field in ['title','subTitle', 'specs']:
            valueList = fieldValueMap[field]
            sum = 0
            for value in valueList:
                 sum += (value - meanMap[field])**2 
            SDMap[field] = math.sqrt(sum)/len(valueList)
    writeToBson(SDMap, fileName)

def readeCommonFieldsSDMap(fileName = 'commonFieldSDMap.bson'):
    return evalBson(fileName)

def generateCommonFieldsZ_ScoredMap(products = None, fileName = 'commonFieldsZ_ScoredMap.bson', regenerate = False):
    products = readProducts(products)
    statistics = readCommonFieldStatistics(products, regenerate)
    fieldValueMap = readeNotNullCommonFieldValueLists()
    meanMap = readeCommonFieldsMeanMap()
    SDMap = readeCommonFieldsSDMap()
    Z_ScoredMap = {}
    for field in statistics['fieldList']:
        Z_ScoredMap[field] = []
        valueList = fieldValueMap[field]
        if not field in ['title','subTitle', 'specs']:
            for value in valueList:
                 Z_ScoredMap[field].append(((value - meanMap[field])/SDMap[field]) if SDMap[field] != 0 else 0) 
        else:
            Z_ScoredMap[field] = valueList
    writeToBson(Z_ScoredMap, fileName)