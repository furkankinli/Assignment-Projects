l = []
def addPyFiles(sc, ):
    import os
    for filename in os.listdir(dr):
        #if filename in l: continue
        l.append(filename)
        p = joinPath(dr, filename)
        if filename[-3:] == '.py':
            sc.addPyFile(p) 
        #elif os.path.isdir(p):
        #    ##sc.addPyFile(p) 
        #    sc = addPyFiles(sc, p)
    return sc

def runSpark():
    import PythonVersionHandler, PySparkImports, SparkLogFileHandler
    conf = PySparkImports.SparkConf()
    conf.set("spark.master", "spark://osldevptst02.host.gittigidiyor.net:7077")
    conf.set("spark.executor.memory", "12g")
    conf.set("spark.executor.instances", "2")
    sc = PySparkImports.SparkContext(conf=conf) 
    dr = PythonVersionHandler.joinPath(PythonVersionHandler.joinPath(PythonVersionHandler.joinPath(gitDir, 'CS401'), 'GG-Project'), 'GG-Project')
    sc = addPyFiles(sc, dr)
    SparkLogFileHandler.setSparkContext(sc)

def run(): 
    runSpark() 
    import NewExtractorRunner
    NewExtractorRunner.runNewExtractionMethods()