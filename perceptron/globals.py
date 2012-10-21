'''
Created on 2012-10-19

@author: zxy
'''
import os


PATH = "." + os.altsep + "file"
WORDFILEPATH = PATH + os.altsep + "KeyWord.dat"
NUMOFFEATURESPATH = PATH + os.altsep + "numoffeatures.dat"
FEATUREFILEPATH1 = PATH + os.altsep + "Feature1.dat"
FEATUREFILEPATH2 = PATH + os.altsep + "Feature2.dat"
FEATUREFILEPATH3 = PATH + os.altsep + "Feature3.dat"
FEATUREFILEPATH4 = PATH + os.altsep + "Feature4.dat"
FEATUREFILEPATH5 = PATH + os.altsep + "Feature5.dat"
FEATURELIST = [FEATUREFILEPATH1,FEATUREFILEPATH2,FEATUREFILEPATH3,FEATUREFILEPATH4,FEATUREFILEPATH5]
STOPWORDPATH = "." + os.altsep + "stopword.dat"
TIMES = 2
ALPHA = 0.25
MAX = 2000