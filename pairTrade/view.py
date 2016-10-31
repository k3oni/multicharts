# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 14:10:08 2016

@author: delvin
"""

from matplotlib import pyplot as plt
from event import EventType
from PnLSystem import SpreadTrade
from logger import infor

class View:
    def __init__(self):
        pass
    
    @staticmethod
    def plotSeries(dataSeries, sym, \
                tsRange = None, \
                imageDir = "",\
                sz_x = 16,\
                sz_y = 12,\
                xtick_interval = 1000,\
                newFigure = True,\
                color = 'b',\
                event = None):

        if newFigure:               
            plt.figure(figsize=(sz_x, sz_y))
            
        ts = sorted(dataSeries.keys())
        
        if tsRange <> None:
            tsStart = tsRange[0]
            tsEnd = tsRange[1]
        else:
            tsStart = ts[0]
            tsEnd = ts[-1]
    
        
        dataInterval = []
        tsInterval = []
        
        for t in ts:
            if tsStart <=t and t <= tsEnd:
                dataInterval.append(dataSeries[t])
                tsInterval.append(t)
       
        sampleTicks = range(0, len(tsInterval), xtick_interval)    
        sampleTS = [tsInterval[i] for i in sampleTicks] 
             
        plt.title(sym)
        plt.xticks(sampleTicks, sampleTS, rotation=90)
        plt.grid()    
        plt.plot(range(len(tsInterval)), dataInterval, color)

        if event != None:
            View.handleEvent(plt, tsInterval, event)
            
        plt.savefig(imageDir + sym + '.png')
    
    @staticmethod
    def plotData(alignedData, symList, xtick_interval = 1000):    
        GCIndex = symList.index("GC")
        AUAIndex = symList.index("AUAA")
        USDCNYIndex = symList.index("USDCNY")
        
        closeList1 = {entryList[GCIndex].ts : entryList[GCIndex].close for entryList in alignedData.values()}
        closeList2 = {entryList[AUAIndex].ts : entryList[AUAIndex].close for entryList in alignedData.values()}
        fx = {entryList[USDCNYIndex].ts : entryList[USDCNYIndex].close for entryList in alignedData.values()}       
    
        View.plotSeries(closeList1, symList[GCIndex], xtick_interval = xtick_interval)
        View.plotSeries(closeList2, symList[AUAIndex], xtick_interval = xtick_interval)
        View.plotSeries(fx, symList[USDCNYIndex], xtick_interval = xtick_interval)
        
        troyoz = 31.1034768
        ratio  = {k : troyoz / fx[k] for k in fx.keys()}
        
        View.plotSeries(ratio, "ratio", xtick_interval = xtick_interval)
        
    @staticmethod
    def handleEvent(plt, ts, event):
        if EventType.SpreadTrade == event.type:
            spreadTrades = event.content
            for st in spreadTrades.keys():
                try:
                    entry = spreadTrades[st]
                    x = ts.index(entry.ts)
                    y = entry.spread
                    content = "{ts} {action} {spread} {raw}".format(\
                        ts = entry.ts, action = entry.action, spread =entry.spread,\
                        raw = entry.rawPrice)
                    plt.plot(x, y, 'ro-')
                    plt.annotate(xy =(x, y), s=content)
                except (ValueError, KeyError) as e:
                    infor(e)
                    pass