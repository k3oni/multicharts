# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 17:26:44 2016

@author: delvin
"""

from enum import Enum
from logger import infor
import pickle
import datetime
from pprint import pprint
from EVATools import tools


'''
The PnL System is for post trade analysis. A tradeManager has a set of tradeBook, 
which includes tradeSheets of a specific instrument. A tradeSheet includes 
tradeRecords in a specific date.
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

#  TradeSheet includes carried trades from previous trading and new trades on the day        
#  carry trades are not real trades but trades introduced for net position and pnl
class TradeSheet:
    def __init__(self, date):
        self.trades = []
        self.carryTrades = []
        self.date = date
        self.closePrice = None
    
    # real trade
    def addTradeRecord(self, tr):
        self.trades.append(tr)

    def getDayTrades(self):
        return self.trades

    # carry trades introduced from last trading session
    def addPreviousCarryTrades(self, tradeList):
        self.carryTrades = self.carryTrades + tradeList
        
    def clearPreviousCarryTrades(self):
        self.carryTrades = []

    def getDayTradesAndPreviousCarryTrades(self):
        return self.carryTrades + self.trades 

    def getCarryTradesForNextDay(self):
        tradesReversed = sorted(self.getDayTradesAndPreviousCarryTrades(), 
                            key=lambda entry:entry.ts)
        tradesReversed.reverse()        
        stack = []
        while len(tradesReversed) > 0:
            tr = tradesReversed.pop()
            if len(stack) == 0:
                stack.append(tr)
            else:
                lastTrade = stack.pop()
                if lastTrade.action == tr.action:
                    stack.insert(0, lastTrade)
                    stack.insert(0, tr)        
        stack.reverse()
        return stack
    
    # show all trades
    def showAllTrades(self):
        trades = self.getDayTradesAndPreviousCarryTrades()
        for tr in trades:
            tr.show()
    
    ###########################################################################                
    # PnL includes carry trades pnl and day trades pnl
    def computePnL(self, closePrice, unit):
        trades = self.getDayTradesAndPreviousCarryTrades()
        pnl = 0
        for tr in trades:
            if tr.action == TradeAction.Long:
                pnl = pnl + (closePrice - tr.price) * tr.contractNum
            if tr.action == TradeAction.Short:
                pnl = pnl + (tr.price - closePrice) * tr.contractNum               
        return pnl * unit
        
    def showPnL(self, instr, currency, closePrice, unit):
        trades = self.getDayTradesAndPreviousCarryTrades()
        fmt = "{ts}, {instr}, {action}, {price:.2f}, {closeprice}, {cnum}, {pnl:.2f}, {currency}"
        pnls = []
        for tr in trades:
            if tr.action == TradeAction.Long:
                pnl = (closePrice - tr.price) * tr.contractNum * unit
                pnlStr = fmt.format(ts = tr.ts, instr = instr, action = "buy",
                                    price = tr.price, closeprice = closePrice,
                                    pnl = pnl, cnum = tr.contractNum, currency = currency)
                
            if tr.action == TradeAction.Short:
                pnl = (tr.price - closePrice) * tr.contractNum * unit
                pnlStr = fmt.format(ts = tr.ts, instr = instr, action = "sell",
                                    price = tr.price, closeprice = closePrice,
                                    cnum = tr.contractNum,  pnl = pnl, 
                                    currency = currency)  
        
            pnls.append(pnlStr)
        
        dailyPnL = self.computePnL(closePrice, unit)
        fmt = "{date} summary, {instr}, {pnl:.2f}, {currency}"
        pnlsummary = fmt.format(date = self.date, instr = instr,
                                pnl = dailyPnL, currency = currency)
        pnls.append(pnlsummary)
        
        return pnls
        
    # net position includes carry trade position and day trade position
    def getNetPosition(self):
        return self.getLongPosition() + self.getShortPosition()
        
    def getLongPosition(self):
        trades = self.getDayTradesAndPreviousCarryTrades()
        pos = 0
        for t in trades:
            if t.action == TradeAction.Long:
                pos = pos + t.contractNum
        return pos
        
    def getShortPosition(self):
        trades = self.getDayTradesAndPreviousCarryTrades()
        pos = 0
        for t in trades:
            if t.action == TradeAction.Short:
                pos = pos - t.contractNum
        return pos
        
class TradeBook:
    def __init__(self, symbol, currency, unit):
        self.book = dict()
        self.symbol = symbol
        self.unit = unit
        self.currency = currency
        self.netPosition = dict()
        self.dailyPnL = dict()
        self.dailyClose = dict()

    # tradesheet
    def createTradeSheet(self, d):
        self.book[d] = TradeSheet(d)
        
    def addTradeSheet(self, d, tradesheet):
        if isinstance(d, datetime.date):
            self.book[d] = tradesheet
        else:
            infor("Error: wrong type of date. Use datetime.date object")
    
    def getTradeSheet(self, d):         
        return self.book[d]
            
    # show day trades and carry trades
    def getTradesPerDate(self, date):
        return self.book[date].getDayTradesAndPreviousCarryTrades()
        
    def getTrades(self):
        trades = []
        for d in self.book.keys():
            trades = trades + self.book[d].getTradesPerDate(d)
        return trades

    # net position is determined by day trades and carry trades             
    # build net position will re-calculate all net position since inception 
    def getTradingDayBefore(self, today):
        lastDay = None 
        try:
            preDays = [day for day in self.book.keys() if day < today]                      
            if len(preDays) > 0:            
                lastDay = sorted(preDays)[-1]
        except KeyError as e:
            infor(e)            
        return lastDay
    
    # net position            
    def buildNetPosition(self):
        try:           
            for today in sorted(self.book.keys()):
                self.updateNetPosition(today)
        except (KeyError, ValueError) as e:
            infor(e)

    def updateNetPosition(self, today):
        try:
            lastDay = self.getTradingDayBefore(today)                     
            if lastDay != None:
                carryTrades = self.book[lastDay].getCarryTradesForNextDay()
                self.book[today].clearPreviousCarryTrades()
                self.book[today].addPreviousCarryTrades(carryTrades)
            
            self.netPosition[today] = self.book[today].getNetPosition()
        except KeyError as e:
            infor(e)
            infor("Error : cannot update net position on %s" % today)

    def getNetPosition(self, day):
        try:
            return self.netPosition[day]
        except KeyError as e:
            infor(e)
            infor("Error : Cannot get net position on %s " % day)
               
    ###########################################################################        
    # PnL
    def setDailyClose(self, dailyClose):
        self.dailyClose = dailyClose
        
    # before compute PnL, you must set daily close price    
    def buildPnL(self):
        try:      
            for today in sorted(self.book.keys()):
                self.updatePnL(today)
        except KeyError as e:
            infor(e)

    def updateCarryTradesPrice(self, carryTrades, price):
        def setToPrice(trade):
            trade.price = price
            return trade
        return [setToPrice(trade) for trade in carryTrades] # return a list
            
    def updatePnL(self, today):
        try:
            lastDay = self.getTradingDayBefore(today) 
            if lastDay != None:
                carryTrades = self.book[lastDay].getCarryTradesForNextDay()
                carryTrades = self.updateCarryTradesPrice(carryTrades, 
                                                self.dailyClose[lastDay])
                self.book[today].clearPreviousCarryTrades()
                self.book[today].addPreviousCarryTrades(carryTrades)
            self.dailyPnL[today] = self.book[today].computePnL(self.dailyClose[today], self.unit)
        except KeyError as e:
            infor(e)
        
    def getPnL(self, day):
        try:
            return self.dailyPnL[day]
        except KeyError as e:
            infor(e)
            infor("Error : Cannot get PnL on %s " % day)
            
    def showPnL(self, day):
        return self.getTradeSheet(day).showPnL(self.symbol, self.currency, 
                                                self.dailyClose[day], self.unit)

        
class TradeManager:
    def __init__(self, instrumentList):
        self.__dict__['__type__'] = 'TradeManager'
        self.tradeBooks = dict()        
        self.pnlRecord = dict()
        self.instruments = instrumentList
        for s in self.instruments:
            self.tradeBooks[s.name] = TradeBook(s.name, s.currency, s.unit)
    
    # trade book       
    def getTradeBook(self, symbol):        
        return self.tradeBooks[symbol]

    def showTradeBook(self, symbol, date):
        self.getTradeBook(symbol).getTradeSheet(date).showAllTrades()
    
    # trade sheet
    def createTradeSheet(self, date):
        for inst in self.instruments:
            self.getTradeBook(inst.name).createTradeSheet(date)

    # trades
    def getTrades(self):
        trades = []
        for sym in self.tradeBooks.keys():
            trades = trades + self.tradeBooks[sym].getTrades()
        return trades

    def getTradesByDate(self, date):
        return {sym : self.getTradeBook[sym].getDayTradesAndPreviousCarryTrades(date)
                    for sym in self.instruments}
            
    def addTradeRecord(self, symbol, date, ts, action, price, contractNum):      
        tr = TradeRecord(ts, symbol, action, price, contractNum)
        self.getTradeBook(symbol).getTradeSheet(date).addTradeRecord(tr)
        self.getTradeBook(symbol).updateNetPosition(date)            

    # net position
    def getNetPosition(self, symbol, date):
        return self.getTradeBook(symbol).getNetPosition(date)
    
    # pnl
    def computePnL(self, symbolClosePrice):
        for sym in symbolClosePrice.keys():
            tradeBook = self.getTradeBook(sym)            
            tradeBook.setDailyClose(symbolClosePrice[sym])
            tradeBook.buildPnL()
       
    def getPnL(self, symbol, date):
        return self.getTradeBook(symbol).getPnL(date)
    
    def showPnL(self, symbol, date):
        return self.getTradeBook(symbol).showPnL(date)
        
    # save file
    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
            
class SpreadInfor:
    def __init__(self, coef0, p0, coef1, p1):
        self.p0 = p0
        self.coeff0 = coef0
        self.p1 = p1
        self.coeff1 = coef1
        
    def __str__(self):
        return "coeff0 %s p0 %s coeff1 %s p1 %s" % (self.coeff0, self.p0,
                                                    self.coeff1, self.p1)
        
    def show(self):
        return "coeff0 %.2f p0 %.2f coeff1 %.2f p1 %.2f" % (self.coeff0, self.p0,
                                                    self.coeff1, self.p1)
class SpreadTrade:
    def __init__(self, ts, action, spread, spreadsize, spreadInfor):
        self.ts = ts
        self.spread = spread
        self.spreadsize = spreadsize
        self.action = action
        self.spreadInfor = spreadInfor 
        
    def __str__(self):
         return "spread %s %.2f %s %s" % (self.ts, self.spread, 
                                        self.action, self.spreadInfor.show())
        
    def show(self):
         return "spread %s %.2f %s %s" % (self.ts, self.spread, 
                                        self.action, self.spreadInfor.show())
         
class pairTradeManager(TradeManager):
    # define spread = symbol[0] - symbol[1]
    def __init__(self, instrument1, instrument2, contractNum1, contractNum2):
        TradeManager.__init__(self, (instrument1, instrument2))
        self.contractNum1 = contractNum1
        self.contractNum2 = contractNum2
        self.spreadTrades = dict()
        self.spreadTradeStack = []
        
    # trade record manangement and access    
    def addPairTradeRecord(self, date, ts, action, price1, price2, pairNum):
        if action == TradeAction.Long:
            TradeManager.addTradeRecord(self, self.instruments[0].name, date, 
                    ts, TradeAction.Long, price1, self.contractNum1 * pairNum)
            TradeManager.addTradeRecord(self, self.instruments[1].name, date,
                    ts, TradeAction.Short, price2, self.contractNum2 * pairNum)

        if action == TradeAction.Short:
            TradeManager.addTradeRecord(self, self.instruments[0].name, date,
                    ts, TradeAction.Short, price1, self.contractNum1 * pairNum)
            TradeManager.addTradeRecord(self, self.instruments[1].name, date,
                    ts, TradeAction.Long, price2, self.contractNum2 * pairNum)


        
            
    def showTradeBook(self, date):
        TradeManager.showTradeBook(self, self.instruments[0].name, date)
        TradeManager.showTradeBook(self, self.instruments[1].name, date)

    def showAllTrades(self):
        sym = list(self.tradeBooks.keys())[0]
        days = sorted(self.tradeBooks[sym].book.keys())
        for d in days:
            self.showTradeBook(d)
    
    # spread trade            
    def addSpreadTradeRecord(self, ts, action, spread, spreadSize, spreadInfor):
        st = SpreadTrade(ts, action, spread, spreadSize, spreadInfor)
        self.spreadTrades[ts] = st
        self.spreadTradeStack.append(st)
        
    def getSpreadTrades(self):
        return self.spreadTrades
        
    def showSpreadTrades(self, date):
        spreadTrades = []
        for ts in sorted(self.spreadTrades.keys()):
            if tools.getDateFromDatetime(ts) == date:
                spreadTrades.append(self.spreadTrades[ts].show())      

        return spreadTrades                
      
    # net position
    def getNetPosition(self, date):
        pos1 = TradeManager.getNetPosition(self, self.instruments[0].name, date)
        pos2 = TradeManager.getNetPosition(self, self.instruments[1].name, date)
        
        if pos1 == 0 and pos2 == 0:
            return 0

        if float(pos1) / float(self.contractNum1) == -float(pos2) / float(self.contractNum2):
            return float(pos1) / float(self.contractNum1)
        else:
            infor("Spread position does not match.")
            return None
            
    def updateNetPosition(self, date):
        self.getTradeBook(self.instruments[0].name).updateNetPosition(date)
        self.getTradeBook(self.instruments[1].name).updateNetPosition(date)
    
    # pnl
    def getPnL(self, date):
        pnl1 = TradeManager.getPnL(self, self.instruments[0].name, date)
        pnl2 = TradeManager.getPnL(self, self.instruments[1].name, date)
        return {self.instruments[0].name : pnl1, self.instruments[1].name : pnl2}

    def showPnL(self):
        sym = list(self.tradeBooks.keys())[0]
        days = sorted(self.tradeBooks[sym].book.keys())
        
        title = "timestamp, instrument, action, price, closeprice, contractNum, pnl, currency"
        pprint(title)
        
        pnlRecord = []
        for d in days:
            pnl1 = TradeManager.showPnL(self, self.instruments[0].name, d)
            pnl2 = TradeManager.showPnL(self, self.instruments[1].name, d)
            spreadTrades = self.showSpreadTrades(d)
            pnlRecord = pnlRecord + pnl1 + pnl2 + spreadTrades
            
        for r in pnlRecord:    
            infor(r)
        
    def getTotalPnL(self):
        totalPnL = dict()
        currency = dict()
  
        for sym in self.tradeBooks.keys():
            currency[sym] = self.tradeBooks[sym].currency
            totalPnL[sym] = sum([self.getPnL(d)[sym] for d 
                                    in sorted(self.tradeBooks[sym].book.keys())])
        return totalPnL, currency
        
    def showTotalPnL(self):
        pnl, currency = self.getTotalPnL()
        for sym in pnl.keys():
            infor("{p:.2f} {c}".format(p = pnl[sym], c = currency[sym]))
        
    def getEquityCurve(self):
        from itertools import accumulate        
        equityCurves = dict()
        currency = dict()
        for sym in self.tradeBooks.keys():
            orderedDate = sorted(self.tradeBooks[sym].book.keys())
            pnlList = accumulate([self.getPnL(d)[sym] for d in orderedDate])
            equityCurves[sym] = {d : pnl for d, pnl in zip(orderedDate, pnlList)}
            currency[sym] = [ins.currency for ins in self.instruments if ins.name == sym][0]

        return equityCurves, currency
        
    @staticmethod     
    def getSpreadTradePnL(spreadTrades):
        pnl = 0
        for st in spreadTrades:
            if st.action == TradeAction.Long:
                pnl -= st.spread
            if st.action == TradeAction.Short:
                pnl += st.spread
        return pnl        
        
