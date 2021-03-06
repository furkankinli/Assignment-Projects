from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from OutputLogger import OutputLogger
import sys
import os

# Machine based
COMPUTERNAME = os.getenv('COMPUTERNAME') 
if COMPUTERNAME == None: COMPUTERNAME = 'server'

def joinPath(*args):
    return os.path.join(args[0], args[1])
    if isinstance(args[0], list): args = args[0]
    if len(args) < 1: return args
    else:
        path = args[0]
        for arg in args[1:]:
            os.path.join(path, arg)
        return path
    
PYTHON_VERSION = sys.version_info[0]

gitDir = ''
allLogsPath = ''
if COMPUTERNAME == 'MSI': 
    gitDir = 'D:\\OneDrive\\Projects\\Assignment-Projects'
elif COMPUTERNAME == 'LM-IST-00UBFVH8':
    gitDir = '/Users/miek/Documents/Projects/Assignment-Projects'
else:
    gitDir = '/soe/cicekm/Projects/Assignment-Projects'

outputFileName = joinPath(gitDir, 'CS466/CIFAR10_Tensorflow/CIFAR10_Tensorflow/output.txt')

from datetime import datetime
import time

import tensorflow as tf

import os
import re
import sys
import tarfile

from six.moves import urllib, xrange
import numpy as np

#from PythonVersionHandler import *
#import cifar10_input
#import cifar10
#import MyModel
#import tfFLAGS
