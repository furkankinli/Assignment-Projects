
def evalProduct(productText):
    if 'D' in productText:
        productText = productText.replace('DenseVector([', '')[:-3] + ')'
    product = eval(productText)
    product = (product[0], product[1:])
    return product

def readProductsFromHDFS(fileName = None):
    import paths, SparkLogFileHandler
    if fileName == None:
        products = SparkLogFileHandler.sc_().textFile(paths.newProductVectorFolder)
    else:
        products = SparkLogFileHandler.sc_().textFile(fileName)
    products = products.map(evalProduct)
    #print_(products.first())
    #print_(fileName, products.count(), ' products have been read successfully by', nowStr())
    return products


def getProducts(ids, fileName = None):
    import PySparkImports
    products = readProductsFromHDFS(fileName)
    ids = ids.map(lambda i: (i, i))
    foundProducts = ids.join(products).map(lambda p: (p[1][0], PySparkImports.DenseVector(p[1][1])))
    import PythonVersionHandler
    PythonVersionHandler.print_logging(foundProducts.count(), 'products have been found in database to train by', PythonVersionHandler.nowStr())
    #print_(products.first())
    #products = products.map(lambda x: (x[0], DenseVector(x[1:])))
    f = foundProducts.collect()
    print(f)
    return foundProducts

def readLabeledPairs(path):
    import paths, PythonVersionHandler, SparkLogFileHandler
    labeledPairs = SparkLogFileHandler.sc_().textFile(path)
    labeledPairs = labeledPairs.map(eval)
    PythonVersionHandler.print_logging(path, 'with', labeledPairs.count(), 'labeledPairs will be reading by', PythonVersionHandler.nowStr())
    return labeledPairs

def normalizeTrainData(data):
    labels = data.map(lambda x: x.label)
    features = data.map(lambda x: x.features)
    normalizer1 = Normalizer()
    # Each sample in data1 will be normalized using $L^2$ norm.
    print_(data.count(), 'instances have been normalized by', PythonVersionHandler.nowStr())
    return labels.zip(normalizer1.transform(features)).map(lambda x: LabeledPoint(x[0], x[1]))

def scaleTrainData(features):
    import PythonVersionHandler, PySparkImports
    scaler = PySparkImports.StandardScaler(withMean=True, withStd=True).fit(features)
    PythonVersionHandler.print_high_logging(data.count(), 'instances have been scaled by', PythonVersionHandler.nowStr())
    return scaler.transform(features)#.map(lambda x: PySparkImports.Vectors.dense(x.toArray()))

def generateTrainData(labeledPairs, products):  #TO DO
    import PythonVersionHandler
    PythonVersionHandler.print_high_logging('train instances is being generated by', PythonVersionHandler.nowStr())
    labels = labeledPairs.map(lambda x: x[2])
    features = labeledPairs.map(lambda x: products.lookup(x[0]) - products.lookup(x[1]))
    features = scaleTrainData(features)
    trainData = labels.zip(features).map(lambda x: LabeledPoint(x[0], x[1]))
    PythonVersionHandler.print_high_logging(trainData.count(), 'train instances have been generated by', PythonVersionHandler.nowStr())
    return trainData 

def splitDataScientifically(data, weights = [0.70, 0.30]):
    import PythonVersionHandler
    trainData, testData = data.randomSplit(weights)
    PythonVersionHandler.print_high_logging(trainData.count(), 'distinct instances have been selected to be trained', PythonVersionHandler.nowStr())
    PythonVersionHandler.print_high_logging(testData.count(), 'distinct instances have been selected to be tested', PythonVersionHandler.nowStr())
    return trainData, testData

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

def saveSpecificProduct(products, outputPath):
    import paths, SparkLogFileHandler
    #products = products.map(lambda x: tuple([x[0]]+x[1].toArray()))
    try: 
       SparkLogFileHandler.saveRDDToHDFS(products, outputPath)
    except:
        pass


def train(labeledPairsPath, productsPath, outputPath, saving = True):
    labeledPairs = readLabeledPairs(labeledPairsPath)
    ids = labeledPairs.flatMap(lambda i: i[0]).distinct()
    products = getProducts(ids, productsPath)
    if saving:
        saveSpecificProduct(products, outputPath)
    trainData = generateTrainData(labeledPairs, products)
    trainData, testData = splitDataScientifically(trainData)
    model = trainPairWiseData(trainData, dataName = 'TrainData')
    evaluateModelOnData(model, testData, dataName = 'TestData')
