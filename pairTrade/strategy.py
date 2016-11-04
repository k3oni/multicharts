# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 13:28:41 2016

@author: delvin
"""
import math
import datetime
from logger import infor
from datasrc import datasrc
from EVATools import tools
from PnLSystem import SpreadInfor

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
        
    def setSession(self, tsSet):
        self.dailyFirstTimestamp = datasrc.getDailyFirstTimestamp(tsSet)
        self.dailyLastTimestamp = datasrc.getDailyLastTimestamp(tsSet)
    
    def getSession(self):
        return self.dailyFirstTimestamp, self.dailyLastTimestamp
        
    def isMarketOpen(self, ts):
        return ts in self.dailyFirstTimestamp
        
    def onMarketOpen(self, date):
        self.tm.createTradeSheet(date)
        
    def isMarketClose(self, ts):
        return ts in self.dailyLastTimestamp
        
    def onMarketClose(self, date):
        pass

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
        
    def computePnL(self, dailyClose):
        self.tm.computePnL(dailyClose)
        
    def getTotalPnL(self):
        return self.tm.getTotalPnL()
    
    def showTotalPnL(self):
        return self.tm.showTotalPnL()
    
    def showPnL(self):
        self.tm.showPnL()
        
    def getEquityCurve(self):
        return self.tm.getEquityCurve()
        
    def showAllTrades(self):
        return self.tm.showAllTrades()

       
        
class pairTradingStrategy(strategy):
    def __init__(self, strategyName, instruments):
        strategy.__init__(self, strategyName, instruments)
        self.spreadHistory = dict()
        
    def computeSpread(self, instruments, data):
        pass
    
    def computeSpreadTradeFromTradeRecocrd(self):
        pass

    def getSpreadHistory(self):
        return self.spreadHistory
        
    def getSpreadTrades(self):
        return self.tm.spreadTrades
        
    def getSpreadTradeStack(self):
        return self.tm.spreadTradeStack
    
    def marketBuyPair(self, ts, spread, spreadSz, spreadInfor):
        return self.oms.marketBuyPair(ts, self.instruments, spread, spreadSz, spreadInfor)
        
    def marketSellPair(self, ts, spread, spreadSz, spreadInfor):
        return self.oms.marketSellPair(ts, self.instruments, spread, spreadSz, spreadInfor)


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

    def config(self):
        self.length = 800
        self.warmupPeriod = self.length
        self.leveldiff = 1        
        self.weight = self.getMeanWeight(self.length)
    
    def getNetPosition(self, date):
        return self.tm.getNetPosition(date)
            
    def onMarketOpen(self, date):
        pairTradingStrategy.onMarketOpen(self, date)
        self.tm.updateNetPosition(date)
        infor("Market open on {date} : Carry position {pos}".format(
                  pos = self.tm.getNetPosition(date), date = date))

###############################################################################
    @staticmethod    
    def computeSpread(gc, aua, usdcny):
        troyoz = 31.1034768
        spreadInfor = SpreadInfor(troyoz /usdcny, aua, -1, gc)     
        return aua * troyoz / usdcny - gc, spreadInfor
        
    def getMeanWeight(self, length):
        self.weight = float(2 / (float(length) + 1))
        return self.weight

    def getMeanHistory(self):
        return self.meanHistory
        
    def computeMean(self, preMean, spread, weight):    
        return preMean * (1-weight) + spread * weight

    
    def genSignal(self, ts, spread, spreadInfor, mean, leveldiff):       
        today = tools.getDateFromDatetime(ts)        
        curPos = self.getNetPosition(today)
        
        curLevel = float(spread-mean)/leveldiff
        curLevelUp = -math.ceil(curLevel)
        curLevelDown = -math.floor(curLevel)

        if curPos < curLevelUp:
            self.marketBuyPair(ts, spread, curLevelUp-curPos, spreadInfor)
            '''            
            infor("{ts} {spread} buy {sz} {curLevel} {curPos}".format(\
                    ts=ts, spread=price, sz=curLevelUp-curPos,
                    curLevel=curLevelUp, curPos=curPos))
            '''
        if curPos > curLevelDown:
            self.marketSellPair(ts, spread, curPos-curLevelDown, spreadInfor)
            '''
            infor("{ts} {spread} sell {sz} {curLevel} {curPos}".format(\
                    ts=ts, spread=price, sz=curLevelDown-curPos,
                    curLevel=curLevelDown, curPos=curPos))        
            '''
    
    def training(self, instruments, data):
        pairTradingStrategy.training(self, instruments, data)        
        
        gcDict = datasrc.getDataForSymbol(data, instruments, "GC", "close")
        AUADict = datasrc.getDataForSymbol(data, instruments, "AUAA", "close")
        USDCNYDict = datasrc.getDataForSymbol(data, instruments, "USDCNY", "close")
                    
        ts = sorted(gcDict.keys())
        self.config()        
        pid = 0
        
        for t in ts:
            if self.isMarketOpen(t):
                self.onMarketOpen(tools.getDateFromDatetime(t))
            
            if self.isMarketClose(t):
                self.onMarketClose(tools.getDateFromDatetime(t))
            
            spread, spreadInfor = self.computeSpread(gcDict[t], AUADict[t], USDCNYDict[t])
            self.spreadHistory[t] = spread
            self.oms.updateCurrentPrice("GC", gcDict[t])
            self.oms.updateCurrentPrice("AUAA", AUADict[t])
            
            if pid == 0:
                self.mean = spread
            else:
                self.mean = self.computeMean(self.mean, spread, self.weight)            
            self.meanHistory[t] = self.mean            

            if pid > self.warmupPeriod:
                self.genSignal(t, spread, spreadInfor, self.mean, self.leveldiff)
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
    
    def plotTrades(self, tsRange):
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
        
        for levelNum in range(-3, 4):
            leveldiffDict = {ts : meanHistory[ts] + levelNum * self.leveldiff for ts in meanHistory.keys()}
            vi.plotSeries(leveldiffDict, "leveldiff", xtick_interval = xtickIntv, \
                            tsRange = tsRange, newFigure = False, color = ':g')
        
        leveldiffDict = {ts : meanHistory[ts] - self.leveldiff for ts in meanHistory.keys()}
        vi.plotSeries(leveldiffDict, "leveldiff", xtick_interval = xtickIntv, \
                        tsRange = tsRange, newFigure = False, color = ':g', dpi = 900,
                        saveFile = True)    

    def showEquityCurve(self, usdcny, usdInstru, cnyInstru):       
        from view import View as vi
        from pprint import pprint
        ec, currency = self.getEquityCurve()
        
        for sym in ec.keys():
            vi.plotSeries(ec[sym], sym + "_pnl",
                          xtick_interval = 1, saveFile = True)


        # code is adhoc since contract class is not ready
        orderedDates = sorted(ec[usdInstru].keys())
        combinePnL = {d : ec[usdInstru][d] + ec[cnyInstru][d]/usdcny[d] for d in orderedDates}
        vi.plotSeries(combinePnL, "combined usd", xtick_interval=1, saveFile=True)
        
                