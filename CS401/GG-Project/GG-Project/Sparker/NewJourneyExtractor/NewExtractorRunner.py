from paths import *
from MainSrc.PythonVersionHandler import *
from Sparker.NewJourneyExtractor.BotFilter import *
from Sparker.NewJourneyExtractor.Sessionizer import *
from Sparker.NewJourneyExtractor.ReadyTests import *
from Sparker.NewJourneyExtractor.ReadyTests2 import *
from Sparker.NewJourneyExtractor.FinalizedRunners import *
from Sparker.NewJourneyExtractor.SearchExtractor import *
from Sparker.NewJourneyExtractor.NewProductPreferrer import *
from Sparker.SparkLogProcesser.SparkLogReader import *
from Sparker.SparkLogProcesser.SparkLogFileHandler import *
from LogProcesser.scalaToPython.python_codes.StringUtil import *

def may17ExtractionTest():
    inputPath = joinPath(filteredLogsFromMayFolder, '2017-05-17')
    keywords = get32Keywords()
    outputPath = joinPath(inputPath, '2017-05-17_extractedLogs')
    saveExtractedLogsByKeywordsFromHDFS(inputPath, keywords, outputPath)

def runNewExtractionMethods():
    may17ExtractionTest()