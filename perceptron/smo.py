'''
Created on 2012-10-19

@author: zxy
'''
from __future__ import division
import time
import globals
import os


LOGPATH = "." + os.altsep + "log.dat"
numoffeatures = 0
precision = [0.0 for x in range(5)]
recall = [0.0 for x in range(5)]
f1 = [0.0 for x in range(5)]
#configs
C = 1
TOL = 0.01 #numerical tolerance 


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


def Kernel(x1,x2):
    '''the kernel function'''
    result = 0.0
    for i in range(len(x1)):
        result += x1[i] * x2[i]
    return result


def GetU(x,y,alpha,b):
    '''u = all[yi * alphai * kernel(xi,xtarget)] - b'''
    result = [0 for item in range(len(x))]
    for iterate in range(len(x)):
        targetx = x[iterate]
        for i in range(len(x)):
            result[iterate] += y[i] * alpha[i] * kernel(x[i], targetx)
        result[iterate] -= b
    return result


def AlphaSupportExist(alpha):
    for item in alpha:
        if item > 0 and item < C:
            return True
    return False


def GenIndex_j(index_i,x,y,alpha,u,b):
    '''index_j = max(abs(ei - ej))'''
    index_j = 0
    maxvalue = 0
    ei = u[index_i] - y[index_i]
    for index in range(len(x)):
        ej = u[index] - y[index]
        if maxvalue < abs(ei - ej):
            maxvalue = abs(ei - ej)
            index_j = index
    return index_j


def GenLH(yi,yj,alpha_i,alpha_j):
    if yi != yj:
        L = max([0,alpha_j - alpha_i])
        H = min([C,C - alpha_i + alpha_j])
    else:
        L = max([0,alpha_i + alpha_j - C])
        H = min([C,alpha_i + alpha_j])
    return (L,H)


def Takestep(index_i,index_j,x,y,alpha,u,b):
    changed = False
    if index_i == index_j:
        return (alpha,u,b,changed)
    alpha_i = alpha[index_i]
    alpha_j = alpha[index_j]
    yi = y[index_i]
    yj = y[index_j]
    ei = u[index_i] - yi
    ej = u[index_j] - yj
    (L,H) = GenLH(yi,yj,alpha_i,alpha_j)
    if L == H:
        return (alpha,u,b,changed)
    kii = kernel(x[index_i],x[index_i])
    kjj = kernel(x[index_j],x[index_j])
    kij = kernel(x[index_i],x[index_j])
    eta = kii + kjj - 2 * kij
    if eta != 0:
        alpha_j_new = alpha_j + yj * (ei - ej) / eta
        if alpha_j_new > H:
            alpha_j_new = H
        elif alpha_j_new < L:
            alpha_j_new = L
    alpha_i_new = alpha_i + yi * yj * (alpha_j - alpha_j_new)

    #update alpha,b, u
    (alpha[index_i],alpha[index_j]) = (alpha_i_new,alpha_j_new)
    bi = ei + yi * (alpha_i_new - alpha_i) * kii + yj * (alpha_j_new - alpha_j) * kij + b
    bj = ej + yi * (alpha_i_new - alpha_i) * kij + yj * (alpha_j_new - alpha_j) * kjj + b
    if alpha_i_new > 0 and alpha_i_new < C:
        b = bi
    elif alpha_j_new > 0 and alpha_j_new < C:
        b = bj
    else:
        b = (bi + bj) / 2
    u = GetU(x,y,alpha,b)
    changed = True
    return (alpha,u,b,changed)


def examineExample(index_i,x,y,alpha,u,b):
    '''exmaine index_i and get index_j to Takestep.'''
    alpha_i = alpha[index_i]
    yi = y[index_i]
    ei = u[index_i] - yi
    ri = ei * yi
    changed = False

    if ri < -TOL and alpha_i < C or ri > TOL and alpha_i > 0: # check kkt violates
        #get index_j using heuristic method.
        if AlphaSupportExist(alpha):
            index_j = GenIndex_j(index_i,x,y,alpha,u,b)
            (alpha,u,b,changed) = Takestep(index_i,index_j,x,y,alpha,u,b)
            if changed:
                return (alpha,u,b,changed)
        loopshuffle = random.shuffle([item in range(len(alpha))])
        #loop all  0 < alpha < c from random item
        for index_j in loopshuffle:
            if alpha[index_j] > 0 and alpha[index_j] < C:
                (alpha,u,b,changed) = Takestep(index_i,index_j,x,y,alpha,u,b)
                if changed:
                    return (alpha,u,b,changed)
        #loop all alpha
        for index_j in loopshuffle:
            (alpha,u,b,changed) = Takestep(index_i,index_j,x,y,alpha,u,b)
            if changed:
                return (alpha,u,b,changed)
    return (alpha,u,b,changed)


def Train(filenamelist):
    '''train smo with given data'''
    linelist = GetLines(filenamelist)
    numofexample = len(linelist)
    w = [0 for item in range(numoffeatures)]
    u = [0 for item in range(numofexample)]
    alpha = [0 for item in range(numofexample)]
    b = 0
    y = [0 for item in range(numofexample)]
    x_seed = [0 for item in range(numoffeatures)]
    x = [x_seed for item in range(numofexample)]
    i = 0
    for line in linelist:
        y[i] = int(line[0:2])
        x[i] = GetX(line)
        i += 1
    u = GetU(x,y,alpha,b)
    alphachanged = False
    exmainall = True
    while alphachanged or exmainall:
        alphachanged = False
        if exmainall:
            #loop all examples
            for i in range(numofexample):
                (alpha,u,b,alphachanged) = examineExample(i,x,y,alpha,u,b)
        else:
            #loop all alpha != 0 and C
            for i in range(numofexample):
                if alpha[i] >0 and alpha[i] < C:
                    (alpha,u,b,alphachanged) = examineExample(i,x,y,alpha,u,b)
        if exmainall:
            exmainall = 0
        elif not alphachanged:
            exmainall = 1
    #TODO: calculate w from alpha x y
    for iterate in range(numoffeatures):
        for in_iterate in range(numofexample):
            w[iterate] += alpha[in_iterate] * y[in_iterate] * x[in_iterate][iterate]
    return (w,b)



def Train_old(filenamelist):
    '''train perceptron with given data.'''
    linelist = GetLines(filenamelist)
    w = [0 for item in range(numoffeatures)]
    y = [0 for item in range(globals.MAX)]
    x_seed = [0 for item in range(numoffeatures)]
    x = [x_seed for item in range(globals.MAX)]
    i = 0
    for line in linelist:
        y[i] = int(line[0:2])
        x[i] = GetX(line)
        i += 1
    length = i
    print "[Info]Working...",
    for convergence in range(globals.TIMES):
        for i in range(length): # loop all lines in four file.
            print "[Info]convergence" + str(convergence) + "...line" + str(i)
            #print ".",
            p = 0
            for j in range(numoffeatures):
                p += w[j] * x[i][j]
            if y[i] * p <= 0:
                for j in range(numoffeatures):
                    w[j] += globals.ALPHA * y[i] * x[i][j]
    #print "."
    return w

#TODO: change test adding b
def Test(w,b,filenamelist):
    linelist = GetLines(filenamelist)
    resultlist = []
    for line in linelist:
        p = 0
        y = int(line[0:2])
        x = GetX(line)
        for j in range(numoffeatures):
            p += w[j] * x[j]
        p -= b
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


#TODO: change train back value to turple    
def SMO():
    '''Use perceptron to train model with 4/5 of the data and 1/5 as test data.'''
    "TODO"
    #loop 5 times
    global numoffeatures
    global precision
    global recall
    global f1
    numff = open(globals.NUMOFFEATURESPATH,"r")
    numoffeatures = int(numff.read())
    numff.close()
    print "Features:" + str(numoffeatures)
    print "[Info]Loop times:" + str(globals.TIMES)
    print "[Info]Loop1."
    print "[Info]Loop1 training."
    (w,b) = Train([globals.FEATURELIST[1],globals.FEATURELIST[2],globals.FEATURELIST[3],globals.FEATURELIST[4]])
    print "[Info]Loop1 testing."
    resultlist = Test(w,b,[globals.FEATURELIST[0]])
    print "[Info]Loop1 evaluating."
    Evaluate(resultlist,1)

    print "[Info]Loop2."
    print "[Info]Loop2 training."
    w = Train([globals.FEATURELIST[0],globals.FEATURELIST[2],globals.FEATURELIST[3],globals.FEATURELIST[4]])
    print "[Info]Loop2 testing."
    resultlist = Test(w,[globals.FEATURELIST[1]])
    print "[Info]Loop2 evaluating."
    Evaluate(resultlist,2)

    print "[Info]Loop3."
    print "[Info]Loop3 training."
    w = Train([globals.FEATURELIST[0],globals.FEATURELIST[1],globals.FEATURELIST[3],globals.FEATURELIST[4]])
    print "[Info]Loop3 testing."
    resultlist = Test(w,[globals.FEATURELIST[2]])
    print "[Info]Loop3 evaluating."
    Evaluate(resultlist,3)

    print "[Info]Loop4."
    print "[Info]Loop4 training."
    w = Train([globals.FEATURELIST[0],globals.FEATURELIST[1],globals.FEATURELIST[2],globals.FEATURELIST[4]])
    print "[Info]Loop4 testing."
    resultlist = Test(w,[globals.FEATURELIST[3]])
    print "[Info]Loop4 evaluating."
    Evaluate(resultlist,4)

    print "[Info]Loop5."
    print "[Info]Loop5 training."
    w = Train([globals.FEATURELIST[0],globals.FEATURELIST[1],globals.FEATURELIST[2],globals.FEATURELIST[3]])
    print "[Info]Loop5 testing."
    resultlist = Test(w,[globals.FEATURELIST[4]])
    print "[Info]Loop5 evaluating."
    Evaluate(resultlist,5)

    avg_precision = (precision[0]+precision[1]+precision[2]+precision[3]+precision[4])/5
    avg_recall = (recall[0]+recall[1]+recall[2]+recall[3]+recall[4])/5
    avg_f1 = (f1[0]+f1[1]+f1[2]+f1[3]+f1[4])/5
    
    logdata = "*******************************************************************************\n"
    logdata += "[Info]%s" % time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime())
    logdata += "[Info]Iterate Time:%d\n" % globals.TIMES
    logdata += "[Info]Num of features: %d\n" % numoffeatures
    logdata += "[Data]avg_precision: %s\n" % str(avg_precision)
    logdata += "[Data]avg_recall: %s\n" % str(avg_recall)
    logdata += "[Data]avg_f1: %s\n" % str(avg_f1)
    logdata += "*******************************************************************************\n"
    print 
    print logdata
    logfile = open(LOGPATH,"a")
    logfile.write(logdata)
    logfile.close()
    
    
def main():
    '''
    This is the main function.
    '''
    print "[Info]SMO start."
    SMO()
    print "[Info]SMO complete."
    raw_input("Press any key to continue.")
    
    
if __name__ == '__main__':
    main()
