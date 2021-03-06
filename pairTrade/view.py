# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 14:10:08 2016

@author: delvin
"""

from matplotlib import pyplot as plt
from event import EventType
from PnLSystem import SpreadTrade, TradeAction, pairTradeManager
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
                dpi = None,\
                saveFile = False,\
                event = None):

        if newFigure:               
            plt.figure(figsize=(sz_x, sz_y))
            
        ts = sorted(dataSeries.keys())
        
        if tsRange != None:
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
            
        if saveFile:
            if dpi == None:    
                plt.savefig(imageDir + sym + '.png')
            else:
                plt.savefig(imageDir + sym + ".png", dpi=dpi)
                
    @staticmethod
    def plotData(alignedData, symList, xtick_interval = 1000):    
        GCIndex = symList.index("GC")
        AUAIndex = symList.index("AUAA")
        USDCNYIndex = symList.index("USDCNY")
        
        closeList1 = {entryList[GCIndex].ts : entryList[GCIndex].close 
                          for entryList in alignedData.values()}
        closeList2 = {entryList[AUAIndex].ts : entryList[AUAIndex].close 
                          for entryList in alignedData.values()}
        fx = {entryList[USDCNYIndex].ts : entryList[USDCNYIndex].close 
                          for entryList in alignedData.values()}       
    
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
            stack = []
            
            for st in sorted(spreadTrades.keys()):
                try:
                    entry = spreadTrades[st]
                    x = ts.index(entry.ts)
                    y = entry.spread
                    plt.plot(x, y, 'ro-')
                    '''
                    if entry.action == TradeAction.Long:
                        action = "Long"
                    if entry.action == TradeAction.Short:
                        action = "Short"
                        
                    content = "{ts} {action} {spread:.2f}".format(\
                        ts = entry.ts, action = action, spread =entry.spread)              
                    
                    plt.annotate(xy =(x, y), s=content)
                    '''
                    if len(stack) == 0:
                        stack.append(entry)
                    else:
                        if (stack[-1].action == TradeAction.Long\
                            and entry.action == TradeAction.Short)\
                            or\
                            (stack[-1].action == TradeAction.Short\
                             and entry.action == TradeAction.Long):
                            matchEntry = stack.pop()
                            x1 = ts.index(matchEntry.ts)
                            y1 = matchEntry.spread
                            x2 = ts.index(entry.ts)
                            y2 = entry.spread
                            pnl = pairTradeManager.getSpreadTradePnL([matchEntry, entry])
                            if pnl > 0:
                                color = 'g'
                            else:
                                color = 'r'
                            plt.plot([x1, x2], [y1, y2], color=color)
                        else:
                            stack.append(entry)      
                except (ValueError, KeyError) as e:
                    infor(e)
            