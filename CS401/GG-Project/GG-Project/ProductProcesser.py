from ProductReader import *
from BsonIO import *

def readProducts(products = None, fileName = 'products.json',  decoding = 'unicode-escape'):
    return evalBson(fileName, decoding) if products == None else products 

def nullCargoInfo(product, field):
   product[field + '_' + "shippingDate"] = None
   product[field + '_' + "shippingTime"] = None
   product[field + '_' + "feeType"] = None
   product[field + '_' + "cargoFees"] = None
   return product 

def expandProductField(product, field):
    if product == None: print field, 'Trouble'
    if field == 'cargoInfo' and product[field] == None: 
        product.pop(field)
        return nullCargoInfo(product, field)
    else:
        fieldMap = product[field]
        for k, v in fieldMap.items():
            if k == 'store':
                product[field + '_storeId'] = v['storeId'] if v != None else None
            if not k in ['caddeFeature', 'mostSoldFeature', 'campaigns', 'store']:
                product[field + '_' + k] = v
        product.pop(field)
        return product

def generateFieldsExpandedProducts(fileName = 'expandedProducts.bson',  products = None, printing = False):
    products = readProducts(products)
    for product in products:
        product = fixQuotesOnProduct(product)
        product.pop('_id')
        product.pop('categories')
        product = expandProductField(product, 'feature')
        product = expandProductField(product, 'category')
        product = expandProductField(product, 'cargoInfo')
        product = expandProductField(product, 'member')
    writeToBson(products, fileName, decoding = 'unicode-escape', printText = True)

def checkCommonFieldsCount(products = None):
    products = readProducts(products)
    length = len(products[0])
    print length
    for product in products:
        if length != len(product):
            for k in product.keys():
                if not k in products[0].keys():
                    print k

def generateCommonFieldList(fileName = 'commonFieldList.bson', products = None, printing = False):
    products = readProducts(products)
    commonFieldList = products[0].keys()
    writeToBson(commonFieldList, fileName, printing, decoding = 'unicode-escape')
    return commonFieldList

def readCommonFieldList(fileName = 'commonFieldList.bson'):
    return evalBson(fileName)

def generateCommonFieldValueLists(fileName = 'commonFieldValueLists.bson',  products = None, printing = False):
    products = readProducts(products)
    commonFieldList = readCommonFieldList()
    commonFieldValueLists = {}
    for field in commonFieldList:
        commonFieldValueLists[field] = []
    for product in products:
        for field in commonFieldList:
            commonFieldValueLists[field].append(product[field])
    writeToBson(commonFieldValueLists, fileName, printText = printing, decoding = 'unicode-escape')

def readCommonFieldValueLists(fileName = 'commonFieldValueLists.bson'):
    return evalBson(fileName, decoding = 'unicode-escape')

def containsType(l, t):
    for e in l:
        if t == None:
            if e == None:
                return True
        elif isinstance(e, t):
            return True
        return False

def setWithNone(l):
    li = [e for e in l if e != None]
    li.append(None)
    return li

def getTypeOfListElement(l):
    li = setWithNone(l)
    if len(li) == 0:
        return type(None).__name__
    else:
        return type(li[0]).__name__

def generateCommonFieldValueTypes(fileName = 'commonFieldValueTypes.bson',  products = None, printing = False):
    products = readProducts(products)
    commonFieldValueLists = readCommonFieldValueLists()
    commonFieldValueTypes = {}
    for field, fieldList in commonFieldValueLists.items():
            commonFieldValueTypes[field] = getTypeOfListElement(fieldList)
    writeToBson(commonFieldValueTypes, fileName, printText = printing, decoding = 'unicode-escape')

def readCommonFieldValueTypes(fileName = 'commonFieldValueTypes.bson'):
    return evalBson(fileName, decoding = 'unicode-escape')

def generateCommonFieldValueTypeCounts(fileName = 'commonFieldValueTypeCounts.bson',  products = None, printing = False):
    commonFieldValueTypes = readCommonFieldValueTypes()
    typeCounts = {}
    typeList = commonFieldValueTypes.values()
    typeSet = list(set(typeList))
    for type in typeSet:
        typeCounts[type] = typeList.count(type)
    writeToBson(typeCounts, fileName, printText = printing, decoding = 'unicode-escape')

def generateCommonFieldValueSets(fileName = 'commonFieldValueSets.bson',  products = None, printing = False):
    products = readProducts(products)
    commonFieldValueLists = readCommonFieldValueLists()
    commonFieldValueSets = {}
    for field, fieldList in commonFieldValueLists.items():
        if containsType(fieldList, None):
            fieldList = setWithNone(fieldList)
        if not (containsType(fieldList, dict) or containsType(fieldList, list)):
            commonFieldValueSets[field] = list(set(fieldList))
        else:
            commonFieldValueSets[field] = fieldList
    writeToBson(commonFieldValueSets, fileName, printText = printing, decoding = 'unicode-escape')
    
def readCommonFieldValueSets(fileName = 'commonFieldValueSets.bson'):
    return evalBson(fileName, decoding = 'unicode-escape')

def generateCommonFieldValueCounts(fileName = 'commonFieldValueCounts.bson',  products = None, printing = False):
    commonFieldValueSets = readCommonFieldValueSets()
    valueCounts = {}
    for k, v in commonFieldValueSets.items():
        valueCounts[k] = len(v)
    writeToBson(valueCounts, fileName, printText = printing, decoding = 'unicode-escape')