# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 17:26:44 2016

@author: delvin
"""

from enum import Enum
from logger import infor
import pickle
import datetime


'''
The PnL System is for post trade analysis
A tradeManager has a set of tradeBook, which includes tradeSheets of a specific instrument.
A tradeSheet includes tradeRecords in a specific date.


'''

class TradeAction(Enum):
    Long = 1
    Short = 2
    Entry = 3
    Exit = 4

class TradeRecord:
    def __init__(self, timestamp, instrument, tradeaction, price, contractNum):
        self.ts = timestamp
        self.ins = instrument
        self.action = tradeaction
        self.price = price
        self.contractNum = contractNum
        
    def show(self):
        msg = "{ts} {ins} {action} {price} {cn}".format(
                ts = self.ts, action = self.action, price =self.price,
                cn = self.contractNum, ins = self.ins)
        infor(msg)
        
    def __str__(self):
        return "{ts} {ins} {action} {price} {cn}".format(
                ts = self.ts, action = self.action, price =self.price,
                cn = self.contractNum, ins =self.ins)

        
class TradeSheet:
    def __init__(self):
        self.trades = []
    
    def addTradeRecord(self, tr):
        self.trades.append(tr)
        
    def getTrades(self):
        return self.trades
        
    def showAllTrades(self):
        if len(self.trades) == 0:
            # infor("No trade in tradebook")
            return
        for tr in self.trades:
            tr.show()

    def computePnL(self):
        if len(self.trades) == 0:
            return 0
        pnl = 0
        for tr in self.trades:
            if tr.action == TradeAction.Long:
                pnl = pnl - tr.price * tr.contractNum
            if tr.action == TradeAction.Short:
                pnl = pnl + tr.price * tr.contractNum
                
        return pnl
    
    def getNetPosition(self):
        return self.getLongPosition() + self.getShortPosition()
        
    def getLongPosition(self):
        if len(self.trades) == 0:
            return 0
        pos = 0
        for t in self.trades:
            if t.action == TradeAction.Long:
                pos = pos + t.contractNum
        return pos
        
    def getShortPosition(self):
        if len(self.trades) == 0:
            return 0
        pos = 0
        for t in self.trades:
            if t.action == TradeAction.Short:
                pos = pos - t.contractNum
        return pos
        
class TradeBook:
    def __init__(self, symbol):
        self.book = dict()
        self.symbol = symbol

    def addTradeSheet(self, d, tradesheet):
        if isinstance(d, datetime.date):
            self.book[d] = tradesheet
        else:
            infor("Error: wrong type of date. Use datetime.date object")
            
    def getTrades(self):
        trades = []
        for d in self.book.keys():
            trades = trades + self.book[d].getTrades()
        return trades
    
    def getTradeSheet(self, d):
        if d not in self.book.keys():
            self.addTradeSheet(d, TradeSheet())
            
        return self.book[d]

    def computeNetProfit(self, since, till):
        pass

    def computeSharpeRatio(self, since, till):
        pass
         
        
class TradeManager:
    def __init__(self, symbolList):
        self.__dict__['__type__'] = 'TradeManager'
        self.tradeBooks = dict()        
        self.pnlRecord = dict()
        self.symbols = symbolList
        for s in self.symbols:
            self.tradeBooks[s] = TradeBook(s)
    
    # each symbol has a trade book        
    def getTradeBook(self, symbol):        
        return self.tradeBooks[symbol]
        
    def getTrades(self):
        trades = []
        for sym in self.tradeBooks.keys():
            trades = trades + self.tradeBooks[sym].getTrades()
        return trades

    def addTradeRecord(self, symbol, date, ts, action, price, contractNum):      
        tr = TradeRecord(ts, symbol, action, price, contractNum)
        self.getTradeBook(symbol).getTradeSheet(date).addTradeRecord(tr)

    def getNetPosition(self, symbol, date):
        np = self.getTradeBook(symbol).getTradeSheet(date).getNetPosition()
        return np        
        
    def getPnL(self, symbol, date):
        if date in self.pnlRecord.keys():
            return self.pnlRecord[date]
        else:
            pnl = self.getTradeBook(symbol).getTradeSheet(date).computePnL()
            self.recordPnL(date, pnl)
            return pnl
        
    def recordPnL(self, date, pnl):
        self.pnlRecord[date] = pnl
        
    def showTradeBook(self, symbol, date):
        self.getTradeBook(symbol).getTradeSheet(date).showAllTrades()
        
    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

        
class SpreadTrade:
    def __init__(self, ts, action, spread, spreadsize, rawPrice):
        self.ts = ts
        self.spread = spread
        self.spreadsize = spreadsize
        self.action = action
        self.rawPrice = rawPrice 
        
    def __str__(self):
        return "%s %s %s %s" % (self.ts, self.spread, self.action, self.rawPrice)
        
class pairTradeManager(TradeManager):
    # define spread = symbol[0] - symbol[1]
    def __init__(self, symbol1, symbol2, contractNum1, contractNum2):
        TradeManager.__init__(self, (symbol1, symbol2))
        self.contractNum1 = contractNum1
        self.contractNum2 = contractNum2
        self.spreadTrades = dict()
        
    def addPairTradeRecord(self, date, ts, action, price1, price2, pairNum):
        if action == TradeAction.Long:
            TradeManager.addTradeRecord(self, self.symbols[0], date, ts, TradeAction.Long, price1, self.contractNum1 * pairNum)
            TradeManager.addTradeRecord(self, self.symbols[1], date, ts, TradeAction.Short, price2, self.contractNum2 * pairNum)
            #infor("Long symbol1 " + str(self.contractNum1 * pairNum) + " short symbol2 " + str(self.contractNum2 * pairNum))

        if action == TradeAction.Short:
            TradeManager.addTradeRecord(self, self.symbols[0], date, ts, TradeAction.Short, price1, self.contractNum1 * pairNum)
            TradeManager.addTradeRecord(self, self.symbols[1], date, ts, TradeAction.Long, price2, self.contractNum2 * pairNum)
            #infor("Short symbol1 " + str(self.contractNum1 * pairNum) + " long symbol2 " + str(self.contractNum2 * pairNum)) 
        
    def addSpreadTradeRecord(self, ts, action, spread, spreadSize, rawPrice):
        self.spreadTrades[ts] = SpreadTrade(ts, action, spread, spreadSize, rawPrice)
        
    def getSpreadTradeRecord(self):
        return self.spreadTrades
      
    def getNetPositionByDate(self, date):
        pos1 = TradeManager.getNetPosition(self, self.symbols[0], date)
        pos2 = TradeManager.getNetPosition(self, self.symbols[1], date)
        
        if pos1 == 0 and pos2 == 0:
            return 0
        
        return float(pos1) / float(self.contractNum1)

    def getNetPosition(self):
        sym = self.tradeBooks.keys()[0]
        days = sorted(self.tradeBooks[sym].book.keys())
        netPos = 0
        for d in days:
            netPos += self.getNetPositionByDate(d)
        return netPos
        
    def getPnL(self, date):
        pnl1 = TradeManager.getPnL(self, TradeManager.symbols[0], date)
        pnl2 = TradeManager.getPnL(self, TradeManager.symbols[1], date)
        return pnl1 + pnl2
        
    def showTradeBook(self, date):
        # infor("Show trade book on " + str(date))
        TradeManager.showTradeBook(self, self.symbols[0], date)
        TradeManager.showTradeBook(self, self.symbols[1], date)

    def showAllTrades(self):
        sym = self.tradeBooks.keys()[0]
        days = sorted(self.tradeBooks[sym].book.keys())
        for d in days:
            self.showTradeBook(d)