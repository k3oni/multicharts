# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 13:40:27 2016

@author: delvin
"""

import os, numpy as np, collections
from datetime import datetime
import math
from logger import infor

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
                                        
class datasrc:
    def __init__(self):
        pass
    
    @staticmethod
    def loadDataDir(directory):
        dataDict = dict()
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
                            #infor(e)
                            pass
                            
                        
                dataDict[file[0:-4]] = instru
        return dataDict
    
    @staticmethod
    def writeToCSV(mat, filename):
        np.savetxt(filename, mat, delimiter=",", fmt="%20.5f")             

    @staticmethod
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
                        
                # remove entries cannot be aligned                  
                setDiff = set(dataAligned.keys()) - set(dataDict[sym].keys())
                dataAligned = {key : dataAligned[key] for key in set(dataAligned.keys()) if key not in setDiff}
                symList.append(sym)
                                                               
        orderedAlignedData = collections.OrderedDict(sorted(dataAligned.items(), key = lambda t:t[0]))

        return orderedAlignedData, symList
        
    @staticmethod
    def getRangeData(dataDict, symList, tsRange):
        rangeData = dict()
        for ts in dataDict.keys():
            if tsRange[0] <= ts and ts <= tsRange[1]:
                rangeData[ts] = dataDict[ts]
        orderedData = collections.OrderedDict(sorted(rangeData.items(), key=lambda t:t[0]))
        return orderedData, symList
    
    @staticmethod
    def getDataForSymbol(dataDict, symList, sym, field):
        index = symList.index(sym)
        symData = {key:dataDict[key][index].close for key in dataDict.keys()}      
        #symData = eval("{key:locals()['dataDict'][key][index].%s for key in locals()['dataDict'].keys()}" % field)
        return symData
        
    @staticmethod
    def partitionData(orderedAlignedData, N):
        partLength = math.floor(len(orderedAlignedData) / float(N))
        dataset = [dict(orderedAlignedData.items()[0+i*partLength:(i+1)*partLength]) for i in range(N)]
        return dataset
        
        

