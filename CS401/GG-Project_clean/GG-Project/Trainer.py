
def evalProduct(productText):
    if 'D' in productText:
        productText = productText.replace('DenseVector(', '')[:-1]
    product = eval(productText)
    product = (product[0], DenseVector(product[1:]))
    return product

def readProductsFromHDFS(fileName = None):
    import paths, SparkLogFileHandler
    if fileName == None:
        products = SparkLogFileHandler.sc_().textFile(paths.newProductVectorFolder)
    else:
        products = SparkLogFileHandler.sc_().textFile(paths.newProductVectorFolder)
    products = products.map(evalProduct)
    #print_(products.first())
    #print_(fileName, products.count(), ' products have been read successfully by', nowStr())
    return products


def getProducts(ids, fileName = None):
    products = readProductsFromHDFS(fileName)
    ids = ids.map(lambda i: (i, i))
    products = products.map(lambda p: (p[0], p[1:]))
    foundProducts = ids.join(products).map(lambda p: p[1])
    import PythonVersionHandler
    PythonVersionHandler.print_logging(foundProducts.count(), 'products have been found in database to train by', PythonVersionHandler.nowStr())
    #print_(products.first())
    #products = products.map(lambda x: (x[0], DenseVector(x[1:])))
    return products

def readLabeledPairs(path):
    import paths, PythonVersionHandler, SparkLogFileHandler
    labeledPairs = SparkLogFileHandler.sc_().textFile(path)
    labeledPairs = labeledPairs.map(lambda x: eval(x))
    PythonVersionHandler.print_logging(path, 'with', labeledPairs.count(), 'labeledPairs will be reading by', PythonVersionHandler.nowStr())
    return labeledPairs

def generateTrainData(labeledPairs, products): 
    print_('train instances is being generated by', nowStr())
    trainData = labeledPairs.map(lambda x: (keyPairIds(x[0], x[1]), LabeledPoint(x[2], products[x[0]] - products[x[1]])))
    print_(trainData.count(), 'train instances have been generated by', nowStr())
    return trainData 

def scaleTrainData(data): #TO DO
    label = data.map(lambda x: x.label)
    features = data.map(lambda x: x.features)
    scaler = StandardScaler(withMean=True, withStd=True).fit(features)
    print_(data.count(), 'instances have been scaled by', nowStr())
    return label.zip(scaler.transform(features.map(lambda x: Vectors.dense(x.toArray())))).map(lambda x: LabeledPoint(x[0], x[1]))

def normalizeTrainData(data):
    labels = data.map(lambda x: x.label)
    features = data.map(lambda x: x.features)
    normalizer1 = Normalizer()
    # Each sample in data1 will be normalized using $L^2$ norm.
    print_(data.count(), 'instances have been normalized by', nowStr())
    return labels.zip(normalizer1.transform(features)).map(lambda x: LabeledPoint(x[0], x[1]))

def extractJourneyLogsFromDay(keyword, logsFile, journeyFile):
    logs = getLogs(None, logsFile)
    print_(logs.count(), 'Logs have been read successfully by', nowStr())
    journey = getJourneyByKeyword(logs, keyword)
    print_(journey.count(), 'Logs have been extracted for ' + keyword + ' journeys by', nowStr())
    journey.saveAsTextFile(journeyFile)
    print_(journeyFile, 'as', keyword, 'journey has been saved successfully by', nowStr())
    return journey

def extractLabeledPairsFromJourney(keyword, inputName, journeyFile, productsFile, outputFolder):
    keyword = keyword.replace(' ', '_')
    journey = readJourneyFromHDFS(journeyFile)
    modulizedIds = getLabeledPairsWithModulizedIds(journey)
    labeledPairsFile = inputName + '_' + keyword + '_' + 'labeledPairs'
    modulizedIds['labeledPairs'].saveAsTextFile(joinPath(outputFolder, labeledPairsFile))
    print_(labeledPairsFile, 'have been saved successfully by', nowStr())
    products = getProducts(modulizedIds['listed'], productsFile)
    journeyProductsFile = inputName + '_' + keyword + '_' + 'journey_products'
    products.saveAsTextFile(joinPath(outputFolder, journeyProductsFile))
    print_(journeyProductsFile, 'have been saved successfully by', nowStr())
    trainData = generateTrainData(modulizedIds['labeledPairs'], products)
    saveTrainDataToHDFS(trainData, outputFolder, inputName, keyword)
    return trainData

def generateTrainData1(logs, keyword, outputFolder): 
    rawKeyword = keyword
    keyword = keyword.replace(' ', '_')
    inputName = 'all_day'
    journeyFile = joinPath(outputFolder, keyword + '_' + inputName + '_journey')
    if logs != None:
        journey = getJourneyByKeyword(logs, rawKeyword)
        saveRDDToHDFS(journey, journeyFile)
    productsFile = None
    return extractLabeledPairsFromJourney(keyword, inputName, journeyFile, productsFile, outputFolder)

def evaluateModelOnData(model, data, dataName = 'Data', modelName = 'Model'):
    labelsAndPreds = data.map(lambda p: (p.label, model.predict(p.features)))
    truePredictionCount = labelsAndPreds.filter(lambda vp: vp[0] == vp[1]).count()
    instanceCount = data.count()
    accuracy = 100 * truePredictionCount / float(instanceCount)
    print_('\n'+modelName, 'has been evaluated on', dataName, 'by', nowStr())
    print_('The result accuracy is %' + '%.3f\n' % (accuracy))
    return labelsAndPreds

def trainPairWiseData(data, dataName = 'Data', modelName = 'Model', evaluate = True):
    model = SVMWithSGD.train(data, iterations=100)
    print_('\n'+modelName, 'has been trained on', dataName, 'by', nowStr())
    print_('The learned weights:\n' + str(model.weights).replace(',', ', ') + '\n')
    if evaluate:
        evaluateModelOnData(model, data, dataName, modelName)
    return model

def runTrainingExperiment(trainData, testData, modelName = 'Model', save = True, outputFolder = Day1_iPhone_6_DataFolder):
    rainData = scaleTrainData(trainData)
    #ttrainData = normalizeTrainData(trainData)
    model = trainPairWiseData(trainData, 'trainData', modelName)
    if save:
        modelPath = joinPath(outputFolder, modelName)
        try:
            model.save(sc_(), modelPath)
        except Py4JJavaError:
            pass
        print_(modelPath, 'has been saved successfully by', nowStr())
    return evaluateModelOnData(model, testData, 'testData', modelName)

def rankProducts(products, outputFolder, model = None, modelName = 'Model_v04_4'):
    if model == None:
        modelPath = joinPath(outputFolder, modelName)
        model = SVMModel.load(sc_(), modelPath)
    print_(products.first())
    if isinstance(products.first()[1], list):
        products = products.map(lambda x: (x[0], DenseVector(x[1])))
    products = products.map(lambda x: (-x[1].dot(model.weights), (x[0], x[1])))
    #print_(products.take(2))
    products = products.sortByKey()
    #print_(products.take(2))
    products = products.zipWithIndex().map(lambda x: (x[1] + 1, -x[0][0], x[0][1][0], x[0][1][1]))
    print_(products.count(), 'products have been ranked successfully by', nowStr())
    #print_(products.take(2))
    productsPath = joinPath(outputFolder, 'all_day_iphone_6_journey_rankedProducts')
    saveRDDToHDFS(products, productsPath)
    productsList = products.map(lambda x: x[2]).take(50)
    print_(productsList)
    return products
