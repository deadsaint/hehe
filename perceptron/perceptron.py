'''
Created on 2012-10-15

@author: zxy
'''
#coding : utf-8
#author : zxy
#date   : 2012.9.21
#modify : 2012.10.15 add tf-idf
from __future__ import division
from math import log
import os
import re
import random


PATH = "./file"
WORDFILEPATH = PATH + "/KeyWord.dat"
NUMOFFEATURESPATH = PATH + "/numoffeatures.dat"
FEATUREFILEPATH1 = PATH + "/Feature1.dat"
FEATUREFILEPATH2 = PATH + "/Feature2.dat"
FEATUREFILEPATH3 = PATH + "/Feature3.dat"
FEATUREFILEPATH4 = PATH + "/Feature4.dat"
FEATUREFILEPATH5 = PATH + "/Feature5.dat"
FEATURELIST = [FEATUREFILEPATH1,FEATUREFILEPATH2,FEATUREFILEPATH3,FEATUREFILEPATH4,FEATUREFILEPATH5]
TIMES = 10
ALPHA = 0.25
MAX = 2000
numoffeatures = 0
precision = [0.0 for x in range(5)]
recall = [0.0 for x in range(5)]
f1 = [0.0 for x in range(5)]


def FindFilenames():
    '''Find the names of news file'''
    filenames1 = os.listdir("./baseball")
    for i in range(len(filenames1)):
        filenames1[i] = "./baseball/" + filenames1[i]
    filenames2 = os.listdir("./hockey")
    for i in range(len(filenames2)):
        filenames2[i] = "./hockey/" + filenames2[i]
    filenames = filenames1 + filenames2
    return filenames


def GenWordList(name,normal):
    '''Get data and normalize data in file.
        normal = 1 sort and ease dulplicate
    '''
    f = open(name,"r")
    data = f.read()
    f.close()
    REG = re.compile('[a-zA-Z]+')
    wordlist = re.findall(REG,data.lower())
    if normal:
        wordlist = sorted(list(set(wordlist)))
    return wordlist


def Tf(wordlist):
    diclist = []
    checked = []
    length = len(wordlist)
    temp  = 1 / length
    for word in wordlist:
    	if word in checked:#ease duplicate
    		continue
    	else:
    		checked.append(word)
    	print "[Info] %s." % word
        dic = {"word":word,"tfidf":wordlist.count(word) * temp}#count/length
        diclist.append(dic)
    return diclist


def Idf(diclist,wordlist):
    '''idf = log(D+1/ti)'''
    D = 3 #2(files) + 1
    login = log(D/2)
    logout = log(D/1)
    resultlist = []
    for dic in diclist:
    	print "[Info] %s." % dic['word']
        if dic['word'] in wordlist:
            tfidf  = dic['tfidf']*login
        else:
            tfidf = dic['tfidf'] * logout
        resultlist.append({"word":dic['word'],"tfidf":tfidf})
    return resultlist


def TfIdf(wordlist_baseball,wordlist_hockey):
    '''Take all files as two big files. so D = 2.
    '''
    diclist_baseball = Tf(wordlist_baseball)
    diclist_hockey = Tf(wordlist_hockey)
    
    diclist_baseball = Idf(diclist_baseball,wordlist_hockey)
    diclist_hockey = Idf(diclist_hockey,wordlist_baseball)
    diclist_baseball.sort(key = lambda obj:obj.get('tfidf'))
    diclist_hockey.sort(key = lambda obj:obj.get('tfidf'))
    wordlist = []
    for dic in diclist_baseball[int(len(diclist_baseball)/2):] + diclist_hockey[int(len(diclist_hockey)/2):]:
        wordlist.append(dic['word'])
    return wordlist


def GenKeywordFile():
    '''Generate the file containing key words.(all stored in lower case)'''
    keywordfile = open(WORDFILEPATH,"w")
    
    filenames = FindFilenames()
    #random.shuffle(filenames)
    #for name in filenames:
    #    print name
    print "[Info]Working..."
    wordlist_baseball = []
    wordlist_hockey = []
    for name in filenames:
        if name[2] == "b":
            wordlist_baseball = wordlist_baseball + GenWordList(name,0)
        else:
            wordlist_hockey = wordlist_hockey + GenWordList(name,0)
    wordlist = TfIdf(wordlist_baseball,wordlist_hockey)
    
    global numoffeatures
    wordlist = sorted(list(set(wordlist)))
    for word in wordlist:
        if len(word) > 2:
            numoffeatures += 1
            keywordfile.write(word + '\n')
    keywordfile.close()
    numff = open(NUMOFFEATURESPATH,"w")
    numff.write(str(numoffeatures))
    numff.close()


def GenClass(name):
    if name[2] == 'b':
        m_class = "+1"
    elif name[2] == 'h':
        m_class = "-1"
    else:
        print "[Error] name error!"
    return m_class


def SplitFeature(featurelist,filename):
    '''Write splited feature into single featurefile'''
    f = open(filename,"w")
    for line in featurelist:
        f.write(line + "\n")
    f.close()
    
    
def GenFeatureFile():
    '''Generate feature line for every single news'''
    filenames = FindFilenames()
    random.shuffle(filenames)
    wordfile = open(WORDFILEPATH,"r")
    worddic = [l.strip() for l in wordfile.readlines()] #eliminate '\n'
    #print worddic
    print "[Info]Working..."
    
    featurelist = []
    for nameindex in range(len(filenames)):
        wordlist = GenWordList(filenames[nameindex],0)
        line = GenClass(filenames[nameindex])
        for wordindex in range(len(worddic)):
            if wordlist.count(worddic[wordindex]) > 0:
                line += " " + str(wordindex) + ":" + str(wordlist.count(worddic[wordindex]))
        print ".",
        featurelist.append(line)
    print "."
    splitlengthoffeature = int(len(featurelist)/5)
    SplitFeature(featurelist[0:splitlengthoffeature],FEATUREFILEPATH1)
    SplitFeature(featurelist[splitlengthoffeature:splitlengthoffeature*2],FEATUREFILEPATH2)
    SplitFeature(featurelist[splitlengthoffeature*2:splitlengthoffeature*3],FEATUREFILEPATH3)
    SplitFeature(featurelist[splitlengthoffeature*3:splitlengthoffeature*4],FEATUREFILEPATH4)
    SplitFeature(featurelist[splitlengthoffeature*4:splitlengthoffeature*5],FEATUREFILEPATH5)

    
def DataPreprocess():
    '''
    Preprocess news data for train and test.
    '''
    
    print "[Info]Generate key word file start."
    GenKeywordFile()
    print "[Info]Key word file complete."

    print "[Info]Generate feature file start."
    GenFeatureFile()
    print "[Info]Feature file complete."


def GetLines(filenamelist):
    '''Put lines of give files into linelist'''
    linelist = []
    for filename in filenamelist:
        f = open(filename,"r")
        linelist += [l.strip() for l in f.readlines()]
        f.close()
    return linelist


def GetX(line):
    x = [0 for item in range(numoffeatures)]
    #print "numoffeatures:" + str(numoffeatures),

    line = line[3:len(line)]
    pairlist = line.split(' ')
    for pair in pairlist:
        (num, value) = pair.split(':')
        #print "[Data]num of X:" + num + " value:" + value
        x[int(num)] = int(value)
    return x

    
def Train(filenamelist):
    '''train perceptron with given data.'''
    linelist = GetLines(filenamelist)
    w = [0 for item in range(numoffeatures)]
    y = [0 for item in range(MAX)]
    x_seed = [0 for item in range(numoffeatures)]
    x = [x_seed for item in range(MAX)]
    i = 0
    for line in linelist:
        y[i] = int(line[0:2])
        x[i] = GetX(line)
        i += 1
    length = i
    print "[Info]Working...",
    for convergence in range(TIMES):
        for i in range(length): # loop all lines in four file.
            print "[Info]convergence" + str(convergence) + "...line" + str(i)
            #print ".",
            p = 0
            for j in range(numoffeatures):
                p += w[j] * x[i][j]
            if y[i] * p <= 0:
                for j in range(numoffeatures):
                    w[j] += ALPHA * y[i] * x[i][j]
    #print "."
    return w


def Test(w,filenamelist):
    linelist = GetLines(filenamelist)
    resultlist = []
    for line in linelist:
        p = 0
        y = int(line[0:2])
        x = GetX(line)
        for j in range(numoffeatures):
            p += w[j] * x[j]
        if p <= 0:
            y_p = -1 #class1
        else:
            y_p = 1 #class2
        result = {'actual':y, 'predicted':y_p}
        resultlist.append(result)
    #print resultlist
    return resultlist


def Evaluate(resultlist,index):
    tp = 0
    fp = 0
    fn = 0
    tn = 0
    global precision
    global recall
    global f1
    for result in resultlist:
        if result['actual'] == 1 and result['predicted'] == 1:
            tp += 1
        elif result['actual'] == -1 and result['predicted'] == 1:
            fp += 1
        elif result['actual'] == 1 and result['predicted'] == -1:
            fn += 1
        else:
            tn += 1
    print "[Data]tp:" + str(tp)
    print "[Data]fp:" + str(fp)
    print "[Data]fn:" + str(fn)
    print "[Data]tn:" + str(tn)
    precision[index-1] = tp / (tp + fp)
    recall[index-1] = tp / (tp + fn)
    print "[Data]precision:" + str(precision[index-1])
    print "[Data]recall:" + str(recall[index-1])
    f1[index-1] = 2 * precision[index-1] * recall[index-1] / (precision[index-1] + recall[index-1])
    print "[Data]f1:" + str(f1[index-1])

    
def Perceptron():
    '''Use perceptron to train model with 4/5 of the data and 1/5 as test data.'''
    "TODO"
    #loop 5 times
    global numoffeatures
    global precision
    global recall
    global f1
    numff = open(NUMOFFEATURESPATH,"r")
    numoffeatures = int(numff.read())
    numff.close()
    print "Features:" + str(numoffeatures)
    print "[Info]Loop times:" + str(TIMES)
    print "[Info]Loop1."
    print "[Info]Loop1 training."
    w = Train([FEATURELIST[1],FEATURELIST[2],FEATURELIST[3],FEATURELIST[4]])
    print "[Info]Loop1 testing."
    resultlist = Test(w,[FEATURELIST[0]])
    print "[Info]Loop1 evaluating."
    Evaluate(resultlist,1)

    print "[Info]Loop2."
    print "[Info]Loop2 training."
    w = Train([FEATURELIST[0],FEATURELIST[2],FEATURELIST[3],FEATURELIST[4]])
    print "[Info]Loop2 testing."
    resultlist = Test(w,[FEATURELIST[1]])
    print "[Info]Loop2 evaluating."
    Evaluate(resultlist,2)

    print "[Info]Loop3."
    print "[Info]Loop3 training."
    w = Train([FEATURELIST[0],FEATURELIST[1],FEATURELIST[3],FEATURELIST[4]])
    print "[Info]Loop3 testing."
    resultlist = Test(w,[FEATURELIST[2]])
    print "[Info]Loop3 evaluating."
    Evaluate(resultlist,3)

    print "[Info]Loop4."
    print "[Info]Loop4 training."
    w = Train([FEATURELIST[0],FEATURELIST[1],FEATURELIST[2],FEATURELIST[4]])
    print "[Info]Loop4 testing."
    resultlist = Test(w,[FEATURELIST[3]])
    print "[Info]Loop4 evaluating."
    Evaluate(resultlist,4)

    print "[Info]Loop5."
    print "[Info]Loop5 training."
    w = Train([FEATURELIST[0],FEATURELIST[1],FEATURELIST[2],FEATURELIST[3]])
    print "[Info]Loop5 testing."
    resultlist = Test(w,[FEATURELIST[4]])
    print "[Info]Loop5 evaluating."
    Evaluate(resultlist,5)

    avg_precision = (precision[0]+precision[1]+precision[2]+precision[3]+precision[4])/5
    avg_recall = (recall[0]+recall[1]+recall[2]+recall[3]+recall[4])/5
    avg_f1 = (f1[0]+f1[1]+f1[2]+f1[3]+f1[4])/5
    print "[Data]The average result."
    print "[Data]avg_precision" + str(avg_precision)
    print "[Data]avg_recall" + str(avg_recall)
    print "[Data]avg_f1" + str(avg_f1)
def main():
    '''
    This is the main function.
    '''
    numoffeatures = 0
    if not os.path.exists(PATH):
        os.mkdir(PATH)
    print "[Info]Data preprocess start."
    #DataPreprocess()
    print "[Info]Data preprocess complete."
    #raw_input("Press any key to continue.")
    
    print "[Info]Perceptron start."
    Perceptron()
    print "[Info]Perceptron complete."
    raw_input("Press any key to continue.")
if __name__ == '__main__':
    main()
