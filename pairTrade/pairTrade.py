# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 12:48:26 2016

@author: delvin
"""
import os, collections
from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np
from pprint import pprint

showException = False

class Entry:
    
    def __init__(self):
        self.ts = ""
        self.open = -1
        self.high = -1
        self.low = -1
        self.close = -1
        self.volume = -1
        
    def __str__(self):
        return "%s : %s, %s, %s, %s" % (self.ts, self.open, self.high, 
                                        self.low, self.close)

def loadDataDir(directory):
    fileDict = dict()
    os.chdir(directory)
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            instru = dict()
            with open(file) as f:
                for row in f:
                    try:
                        cols = row.split(',')
                        entry = Entry()
                        entry.ts = datetime.strptime(cols[0], '%m/%d/%Y %H:%M')
                        entry.open = float(cols[1])
                        entry.high = float(cols[2])
                        entry.low = float(cols[3])
                        entry.close = float(cols[4])
                        instru[entry.ts] = entry
                    except ValueError as e:
                        print(e)
                        
                    
            fileDict[file[0:-4]] = instru
            
    #check file loaded 
    #print("fileDict.keys" , fileDict.keys())
    #for key in fileDict.keys():
    #    print(key, " keys ", fileDict[key].keys())
      
    return fileDict                

def alignData(dataDict):
    # dataAligned:
    #   key : entry.ts
    #   value : list of entries

    firstKey = dataDict.keys()[0]    
    firstDict = dataDict[firstKey]
    dataAligned = {k: [firstDict[k]] for k in firstDict.keys()}
    symList = [firstKey]

    for sym in dataDict.keys():
        if sym <> firstKey:
            # combine entries with same key
            for k in set(dataAligned.keys()) & set(dataDict[sym].keys()):
                try:
                    dataAligned[k].append(dataDict[sym][k])
                except (KeyError, AttributeError) as e:
                    print(e)
                    pass
                    
            # remove entries cannot be aligned                  
            setDiff = set(dataAligned.keys()) - set(dataDict[sym].keys())
            dataAligned = {key : dataAligned[key] for key in set(dataAligned.keys()) if key not in setDiff}
            symList.append(sym)
                                                           
    orderedAlignedData = collections.OrderedDict(sorted(dataAligned.items(), key = lambda t:t[0]))
    #for e in orderedAlignedData.keys():
    #    print(orderedAlignedData[e][0].ts)
    return orderedAlignedData, symList

def writeToCSV(mat, filename):
    np.savetxt(filename, mat, delimiter=",", fmt="%20.5f")

def computeSpread(alignedData, symList):
    troyoz = 31.1034768  #g
    #usd = 6.4 # rmb
    #ratio = troyoz / usd
    GCIndex = symList.index("GC")
    AUAIndex = symList.index("AUAA")
    USDCNYIndex = symList.index("USDCNY")
    
    closeList1 = [entryList[GCIndex].close for entryList in alignedData.values()]
    closeList2 = [entryList[AUAIndex].close for entryList in alignedData.values()]
    fx = [entryList[USDCNYIndex].close for entryList in alignedData.values()]    
    sym = "%s - %s" % (symList[AUAIndex], symList[GCIndex])    
    spread  = [aua * troyoz / usdcny - gc for (gc, aua, usdcny) in zip(closeList1, closeList2, fx)]
    ts = alignedData.keys()

    print(closeList1)
    print(closeList2)
    print(fx)     
      
    #tsInt = [int(t.strftime("%Y%m%d%H%M")) for t in ts]\    
    #dataset = np.array([tsInt, closeList1, closeList2, fx, spread])
    #dataset = np.transpose(dataset)
    #writeToCSV(dataset, "C:\Users\delvin\Desktop\code\pairTrade\debug\checkfile.csv")
       
    return sym, ts, spread

def plotSeries(ts, dataSeries, sym, \
                tsRange = None, \
                imageDir = "C:\Users\delvin\Desktop\code\pairTrade\data\\",\
                sz_x = 16,\
                sz_y = 12,\
                xtick_interval = 1000,
                newFigure = True,
                color = 'b'):

    if tsRange <> None:
        tsStart = tsRange[0]
        tsEnd = tsRange[1]
    else:
        tsStart = ts[0]
        tsEnd = ts[-1]

    
    dataInterval = []
    tsInterval = []
    count = 0
    for t in ts:
        if tsStart <=t and t <= tsEnd:
            dataInterval.append(dataSeries[count])
            tsInterval.append(ts[count])
        count += 1
        
    sampleTicks = range(0, len(tsInterval), xtick_interval)    
    sampleTS = [tsInterval[i] for i in sampleTicks]
 
    if newFigure:               
        plt.figure(figsize=(sz_x, sz_y))
    plt.title(sym)    
    plt.xticks(sampleTicks, sampleTS, rotation=90)
    plt.grid()    
    plt.plot(dataInterval, color)
    plt.savefig(imageDir + sym + '.png')
    
def plotData(alignedData, symList):

    ts = alignedData.keys()       
 
    GCIndex = symList.index("GC")
    AUAIndex = symList.index("AUAA")
    USDCNYIndex = symList.index("USDCNY")
    
    closeList1 = [entryList[GCIndex].close for entryList in alignedData.values()]
    closeList2 = [entryList[AUAIndex].close for entryList in alignedData.values()]
    fx = [entryList[USDCNYIndex].close for entryList in alignedData.values()]    

    plotSeries(ts, closeList1, symList[0])
    plotSeries(ts, closeList2, symList[1])
    plotSeries(ts, fx, symList[2])
    
    troyoz = 31.1034768
    ratio  = [troyoz / usdcny for usdcny in fx]
    plotSeries(ts, ratio, "ratio")
      
def computeEP(spread, length):
    weight = float(2 / (float(length) + 1))

    x = spread[0]    
    mean = []
    for y in spread:
        x = x * (1-weight) + y * weight
        mean.append(x)
    return mean

if __name__ == "__main__":
    dataPath = "C:\Users\delvin\Desktop\code\pairTrade\data"
    imageDir = "C:\Users\delvin\Desktop\code\pairTrade\data\\"
    initLength = 400
    leveldiff = .5    
    dataDict = loadDataDir(dataPath)  
    alignedData, symList = alignData(dataDict)    
    plotData(alignedData, symList)
    sym, ts, spread = computeSpread(alignedData, symList)
    plotSeries(ts, spread, sym, tsRange=[datetime(2016, 10, 25), datetime(2016, 10, 30)], xtick_interval=60)
    #plotSeries(ts, spread, sym)
    mean = computeEP(spread, initLength)
    plotSeries(ts, mean, "mean", newFigure=False, color='r', tsRange=[datetime(2016, 10, 25), datetime(2016, 10, 30)], xtick_interval=60) 
    plotSeries(ts, np.array(mean)+leveldiff, "mean", newFigure=False, color=':g', tsRange=[datetime(2016, 10, 25), datetime(2016, 10, 30)], xtick_interval=60)
    plotSeries(ts, np.array(mean)-leveldiff, "mean", newFigure=False, color=':g', tsRange=[datetime(2016, 10, 25), datetime(2016, 10, 30)], xtick_interval=60)

    #plotSeries(ts, mean, "mean", newFigure=False, color='r')
