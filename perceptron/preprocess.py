'''
Created on 2012-10-19

@author: zxy
'''
from __future__ import division
from math import log
import os
import re
import random
import globals


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
        #print "[Info] %s." % word
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
        #print "[Info] %s." % dic['word']
        if dic['word'] in wordlist:
            tfidf  = dic['tfidf']*login
        else:
            tfidf = dic['tfidf'] * logout
        resultlist.append({"word":dic['word'],"tfidf":tfidf})
    return resultlist


def OptimizeWordlist(diclist_baseball,diclist_hockey):
    '''Optimize diclist with large weight and stop word list. 
    '''
    stopwordfile = open(globals.STOPWORDPATH,"r")
    stopwordlist = [l.strip() for l in stopwordfile.readlines()]
    diclist = diclist_baseball[int(len(diclist_baseball)/2):] + diclist_hockey[int(len(diclist_hockey)/2):]
    wordlist = []
    for dic in diclist:
        if dic["word"] not in stopwordlist:
            wordlist.append(dic["word"])
    """
    for dic in diclist:
        wordlist.append(dic["word"])
    """
    stopwordfile.close()
    return wordlist

def TfIdf(wordlist_baseball,wordlist_hockey):
    '''Take all files as two big files. so D = 2.
    '''
    diclist_baseball = Tf(wordlist_baseball)
    diclist_hockey = Tf(wordlist_hockey)
    
    diclist_baseball = Idf(diclist_baseball,wordlist_hockey)
    diclist_hockey = Idf(diclist_hockey,wordlist_baseball)
    diclist_baseball.sort(key = lambda obj:obj.get('tfidf'))
    diclist_hockey.sort(key = lambda obj:obj.get('tfidf'))
    wordlist = OptimizeWordlist(diclist_baseball,diclist_hockey)
    return wordlist


def GenKeywordFile():
    '''Generate the file containing key words.(all stored in lower case)'''
    numoffeatures = 0
    keywordfile = open(globals.WORDFILEPATH,"w")
    
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
    wordlist = sorted(list(set(wordlist)))
    for word in wordlist:
        if len(word) > 2:
            numoffeatures += 1
            keywordfile.write(word + '\n')
    keywordfile.close()
    numff = open(globals.NUMOFFEATURESPATH,"w")
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
    wordfile = open(globals.WORDFILEPATH,"r")
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
    SplitFeature(featurelist[0:splitlengthoffeature],globals.FEATUREFILEPATH1)
    SplitFeature(featurelist[splitlengthoffeature:splitlengthoffeature*2],globals.FEATUREFILEPATH2)
    SplitFeature(featurelist[splitlengthoffeature*2:splitlengthoffeature*3],globals.FEATUREFILEPATH3)
    SplitFeature(featurelist[splitlengthoffeature*3:splitlengthoffeature*4],globals.FEATUREFILEPATH4)
    SplitFeature(featurelist[splitlengthoffeature*4:splitlengthoffeature*5],globals.FEATUREFILEPATH5)


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

  
def main():
    '''
    This is the main function.
    '''
    if not os.path.exists(globals.PATH):
        os.mkdir(globals.PATH)
    print "[Info]Data preprocess start."
    DataPreprocess()
    print "[Info]Data preprocess complete."
    raw_input("Press any key to continue.")
    
    
if __name__ == '__main__':
    main()

