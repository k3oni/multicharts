# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 13:28:41 2016

@author: delvin
"""
import math
import datetime
from logger import infor
from datasrc import datasrc

class strategy:
    def __init__(self, strategyName, instruments, oms = None, tradeManager = None):
        self.strategyName = strategyName
        self.instruments = instruments
        self.oms = oms
        self.tm = tradeManager

    def setOMS(self, oms):
        self.oms = oms
        
    def getOMS(self):
        return self.oms
        
    def setTradeManager(self, tradeManager):
        self.tm = tradeManager

    def getTradeManager(self):
        return self.tm

    def training(self, instruments, data):
        pass
    
    def validate(self, instruments, data):
        pass
    
    def buy(self, ts, instrument, price):
        self.oms.buy(ts, instrument, price)

    def sell(self, ts, instrument, price):
        self.oms.sell(ts, instrument, price)
        
    def getNetPosition(self, instrument, date):
        return self.tm.getNetPosition(instrument, date)

       
        
class pairTradingStrategy(strategy):
    def __init__(self, strategyName, instruments):
        strategy.__init__(self, strategyName, instruments)
        self.spreadHistory = dict()
        
    def computeSpread(self, instruments, data):
        pass

    def getSpreadHistory(self):
        return self.spreadHistory
        
    def getSpreadTrades(self):
        return self.tm.spreadTrades
    
    def marketBuyPair(self, ts, spread, spreadSz):
        return self.oms.marketBuyPair(ts, self.instruments, spread, spreadSz)
        
    def marketSellPair(self, ts, spread, spreadSz):
        return self.oms.marketSellPair(ts, self.instruments, spread, spreadSz)


class GoldArb(pairTradingStrategy):
    def __init__(self, strategyName, instruments, contractSz):
        pairTradingStrategy.__init__(self, strategyName, instruments)
        self.length = None
        self.warmupPeriod = None
        self.leveldiff = None        
        self.weight = None
        self.contractSz = dict()
        self.mean = None
        self.meanHistory = dict()
       
        for ins, c in zip(instruments, contractSz):
            self.contractSz[ins] = c
        
    def getNetPosition(self):
        return self.tm.getNetPosition()

###############################################################################
    @staticmethod
    def computeSpread(gc, aua, usdcny):
        troyoz = 31.1034768        
        return aua * troyoz / usdcny - gc
        
    def getMeanWeight(self, length):
        self.weight = float(2 / (float(length) + 1))
        return self.weight

    def getMeanHistory(self):
        return self.meanHistory
        
    def computeMean(self, preMean, spread, weight):    
        return preMean * (1-weight) + spread * weight

    
    def genSignal(self, ts, price, mean, leveldiff):       
        curPos = self.getNetPosition()
        
        curLevel = float(price-mean)/leveldiff
        curLevelUp = -math.ceil(curLevel)
        curLevelDown = -math.floor(curLevel)

        if ts == datetime.datetime(2016, 10, 21, 9, 53, 00):
            infor("%s curPos %s curLevelDown %s" % (ts, curPos, curLevelDown))

        if curPos < curLevelUp:
            self.marketBuyPair(ts, price, curLevelUp-curPos)
            infor("{ts} {spread} buy {sz} {curLevel} {curPos}".format(\
                    ts=ts, spread=price, sz=curLevelUp-curPos,
                    curLevel=curLevelUp, curPos=curPos))
        if curPos > curLevelDown:
            infor("{ts} {spread} sell {sz} {curLevel} {curPos}".format(\
                    ts=ts, spread=price, sz=curLevelDown-curPos,
                    curLevel=curLevelDown, curPos=curPos))
            self.marketSellPair(ts, price, curPos-curLevelDown)
        
        
    
    def training(self, instruments, data):
        pairTradingStrategy.training(self, instruments, data)        

        
        gcDict = datasrc.getDataForSymbol(data, instruments, "GC", "close")
        AUADict = datasrc.getDataForSymbol(data, instruments, "AUAA", "close")
        USDCNYDict = datasrc.getDataForSymbol(data, instruments, "USDCNY", "close")
                    
        ts = sorted(gcDict.keys())
        
        self.length = 400
        self.warmupPeriod = self.length
        self.leveldiff = 1        
        self.weight = self.getMeanWeight(self.length)
        pid = 0
        
        for t in ts:
            spread = self.computeSpread(gcDict[t], AUADict[t], USDCNYDict[t])
            self.spreadHistory[t] = spread
            self.oms.updateCurrentPrice("GC", gcDict[t])
            self.oms.updateCurrentPrice("AUAA", AUADict[t])
            
            if pid == 0:
                self.mean = spread
            else:
                self.mean = self.computeMean(self.mean, spread, self.weight)            
            self.meanHistory[t] = self.mean            

            if pid > self.warmupPeriod:
                self.genSignal(t, spread, self.mean, self.leveldiff)
            pid += 1
            
    def onlineValidate(self, ts, instruments, data):
        GCIndex = instruments.index("GC")
        AUAIndex = instruments.index("AUAA")
        USDCNYIndex = instruments.index("USDCNY")
        gc = data[GCIndex]
        aua = data[AUAIndex]
        usdcny = data[USDCNYIndex]
        spread = self.computeSpread(gc, aua, usdcny)        
        
        self.mean = self.computeEP(self.mean, spread, self.weight)
        self.genSignal(ts, spread, self.mean, self.leveldiff)
    
    def showTrades(self, tsRange):
        from view import View as vi
        from event import Event, EventType
        
        spreadHistory = self.getSpreadHistory()
        meanHistory = self.getMeanHistory()
        spreadTrades = self.getSpreadTrades()
        tradeEvent = Event(EventType.SpreadTrade, spreadTrades)
        
        # plot
        xtickIntv = 60        
        vi.plotSeries(spreadHistory, "AUAA-GC", xtick_interval = xtickIntv, \
                        event = tradeEvent, tsRange = tsRange)                     
        vi.plotSeries(meanHistory, "Mean", xtick_interval = xtickIntv, \
                        tsRange = tsRange, newFigure = False, color = 'r')
        leveldiffDict = {ts : meanHistory[ts] + self.leveldiff for ts in meanHistory.keys()}
        vi.plotSeries(leveldiffDict, "leveldiff", xtick_interval = xtickIntv, \
                        tsRange = tsRange, newFigure = False, color = ':g')
        leveldiffDict = {ts : meanHistory[ts] - self.leveldiff for ts in meanHistory.keys()}
        vi.plotSeries(leveldiffDict, "leveldiff", xtick_interval = xtickIntv, \
                        tsRange = tsRange, newFigure = False, color = ':g')    

    