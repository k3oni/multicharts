# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 13:40:27 2016

@author: delvin
"""

import os, numpy as np, collections
import datetime
import math
from logger import infor
from EVATools import tools

class Entry:    
    def __init__(self):
        self.ts = ""
        self.open = -1
        self.high = -1
        self.low = -1
        self.close = -1
        self.volume = -1
        
    def __str__(self):
        return "{ts} : {open}, {high}, {low}, {close}".format( 
                ts = self.ts, 
                open =self.open, 
                high = self.high, 
                low = self.low, 
                close = self.close)
                                        
class datasrc:
    def __init__(self):
        pass
    
    @staticmethod
    def loadDataDir(directory):
        """ Read all 'instrument.csv' file in a given directory
            csv format is "timestamp, open, high, low, close"
            return a dictionary with
                key: file name without suffix
                value: a dictionary with
                        key: timestamp
                        value: entry object
        """
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
                            entry.ts = datetime.datetime.strptime(cols[0], '%m/%d/%Y %H:%M')
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
    def alignData(dataDict):
        # dataAligned:
        #   key : entry.ts
        #   value : list of entries
    
        firstKey = list(dataDict.keys())[0]    
        firstDict = dataDict[firstKey]
        dataAligned = {k: [firstDict[k]] for k in firstDict.keys()}
        symList = [firstKey]
    
        for sym in dataDict.keys():
            if sym != firstKey:
                # combine entries with same key
                for k in set(dataAligned.keys()) & set(dataDict[sym].keys()):
                    try:
                        dataAligned[k].append(dataDict[sym][k])
                    except (KeyError, AttributeError) as e:
                        print(e)
                        
                # remove entries cannot be aligned                  
                setDiff = set(dataAligned.keys()) - set(dataDict[sym].keys())
                dataAligned = {key : dataAligned[key] 
                               for key in set(dataAligned.keys()) 
                               if key not in setDiff}
                symList.append(sym)
                                                               
        orderedAlignedData = collections.OrderedDict(
                                sorted(dataAligned.items(),key = lambda t:t[0]))

        return orderedAlignedData, symList

    @staticmethod
    def getDailyClosePrice(orderedAlignedData, symList):
        tsSet = sorted(orderedAlignedData.keys())
        dateSet = [datetime.date(ts.year, ts.month, ts.day) for ts in tsSet]
        distinctDate = list(reversed(sorted(list(set(dateSet)))))
        
        # dailyClose
        # key: date
        # value: dict with key of sym and value of close price
        dailyClose = dict()
        today = distinctDate.pop()
        while len(distinctDate) != 0:
            nextDay = distinctDate.pop()
            firstMatch = next(ts for ts in tsSet if ts.year == nextDay.year
                    and ts.month == nextDay.month and ts.day == nextDay.day)
            preTS = tsSet[tsSet.index(firstMatch)-1]
            symClose = dict()
            for i in range(len(symList)):            
                symClose[symList[i]] = orderedAlignedData[preTS][i].close
                
            dailyClose[today] = symClose
            today = nextDay

        # dailyClose transformed
        # key: symbol
        # value: dict with key of date and value of close price

        def transform(sym):
            return {d : dailyClose[d][sym] for d in dailyClose.keys()}
        return {sym : transform(sym) for sym in symList}
        
    @staticmethod
    def getTradingDay(timestamps):
        dateSet = [datetime.date(ts.year, ts.month, ts.day) 
                        for ts in timestamps]
        return sorted(list(set(dateSet)))
        
    @staticmethod
    def getDailyFirstTimestamp(timestamps):
        dates = datasrc.getTradingDay(timestamps)
        return sorted([next(ts for ts in sorted(timestamps) 
                    if tools.getDateFromDatetime(ts) == date) for date in dates])
        
    @staticmethod
    def getDailyLastTimestamp(timestamps):
        firstTS = datasrc.getDailyFirstTimestamp(timestamps)
        timestamps = sorted(timestamps)
        return sorted([ timestamps[timestamps.index(ts)-1] for ts in firstTS[1:]])
        
    @staticmethod
    def getRangeData(dataDict, symList, tsRange):
        rangeData = dict()
        for ts in dataDict.keys():
            if tsRange[0] <= ts and ts <= tsRange[1]:
                rangeData[ts] = dataDict[ts]
        orderedData = collections.OrderedDict(sorted(rangeData.items(), 
                                                         key=lambda t:t[0]))
        return orderedData, symList
    
    @staticmethod
    def getDataForSymbol(dataDict, symList, sym, field):
        index = symList.index(sym)
        symData = {key:dataDict[key][index].close for key in dataDict.keys()}      
        return symData
        
    @staticmethod
    def partitionData(orderedAlignedData, N):
        partLength = math.floor(len(orderedAlignedData) / float(N))
        dataset = [dict(orderedAlignedData.items()[0+i*partLength:(i+1)*partLength]) 
                    for i in range(N)]
        return dataset
        
    @staticmethod
    def writeToCSV(mat, filename):
        np.savetxt(filename, mat, delimiter=",", fmt="%20.5f")         

