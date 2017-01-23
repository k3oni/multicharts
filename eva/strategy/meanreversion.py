#!/usr/bin/python
###############################################################################
# Mean Reversion Framework
# Independent EP computation

from strategy import strategy
from tools.common import infor, vipinfor, err, warning
from indicator.ep import EP
from feed.feed import dataType
from bar.bar import barLength, barField
from tools.bbg2IB import toIBContract
from datetime import datetime, timedelta
from msg.msg import msgType
from oms.order import order, ActionType, OrderType, TimeInForce, EntryExitType

class meanReversion(strategy):

    def __init__(self, engine, cfg):
        strategy.__init__(self, engine, cfg)
        self.para = self.getConfig().getParameters()
        self.levelNum = self.para['levelNum']
        self.posPerPositiveLevel = self.para['positionPerPositiveLevel']
        self.posPerNegativeLevel = self.para['positionPerNegativeLevel']
        self.instrument = self.para['Instrument']
        self.epGenerator = EP(self.para)
        self.isTrade = None
        self.ep = None
        self.leveldiff = None
        self.levelOrderMap = dict()

    def onStrategyInit(self):
        strategy.onStrategyInit(self)

    def onSessionInit(self, sessionStart, sessionEnd):
        strategy.onSessionInit(self, sessionStart, sessionEnd)

        # session date
        self.today = sessionStart.replace(hour=0, minute=0, second=0, microsecond=0)

        # contract to trade
        self.contract = toIBContract(self.barCtrl.dbs.getActiveContract(\
                                        self.instrument, self.today))

        if sessionStart.hour == 9:
            self.prepareEP(sessionStart, self.today)

    def onMsg(self, msg):
        strategy.onMsg(self, msg)
        if (msg.msgtype == msgType.barmsg or msg.msgtype == msgType.tickmsg):
            if self.epGenerator.EPDone == False:
                self.isTrade, self.ep, self.leveldiff = self.computeEP(msg)
                self.levels = self.initLevels(self.ep, self.levelNum, self.leveldiff)
                self.levelPosition = self.genLevelPosition(self.levels, self.levelNum)
                self.initPosition(msg)
            else:
                pass

        if msg.msgtype == msgType.omsmsg:
            pass

    def prepareEP(self, sessionStart, today):
        # initialize epGenerator variables
        self.epGenerator.doTrade = True
        self.epGenerator.isExtremeDay = False
        self.epGenerator.epvalue = None
        self.epGenerator.leveldiff = None 
        self.epGenerator.EPDone = False

        # prepare data to compute EP
        start  = sessionStart + timedelta(days = -self.para['preDayNum']) 
        end    = sessionStart + timedelta(days = -1)

        statusHr, self.epGenerator.hrbar  = self.barCtrl.getBlockData(\
                            self.instrument, barLength.hourly, \
                            dataType.historicalBarData, start, end, [barField.open,\
                            barField.high, barField.low, barField.close])

        statusDay, self.epGenerator.daybar  = self.barCtrl.getBlockData(\
                            self.instrument, barLength.daily, \
                            dataType.historicalBarData, start, end, [barField.open,\
                            barField.high, barField.low, barField.close])

        statusDC, self.epGenerator.daybarclose = self.barCtrl.getBlockData(\
                            self.instrument, barLength.daily,\
                            dataType.historicalBarData, start, end, [barField.close])

        if statusHr == False or statusDay == False or statusDC == False:             
                raise Exception('Problem with daily data used by EP.')        
        
        # time to compute EP
        eptime = datetime.strptime(self.para['eptime'], '%H:%M:%S')
        self.eptime = self.today.replace(hour=eptime.hour, minute=eptime.minute)
        vipinfor('EP is ready to compute.')

    def computeEP(self, msg):
        if  msg.msgtype == msgType.barmsg and \
            msg.getBarStartTime() >= self.eptime and \
            msg.getContract() == self.contract: 

            infor("Datetime to compute EP: %s" % msg.getBarStartTime()) 
            self.epGenerator.EPDone = True
            reportTS = msg.getBarStartTime()
            self.epGenerator.computeEPandLevelDiff(msg.open, reportTS)

        if msg.msgtype == msgType.tickmsg and \
            msg.getTS() >= self.eptime and\
            msg.getContract() == self.contractIB and\
            msg.isTradePrice():
            
            infor("Datetime to compute EP: %s" % msg.getTS())
            reportTS = msg.getTS() 
            self.epGenerator.EPDone = True
            self.epGenerator.computeEPandLevelDiff(float(msg.getContent()), reportTS)

        return self.epGenerator.doTrade, self.epGenerator.epvalue, self.epGenerator.leveldiff

    def genLevelPosition(self, levels, levelNum):
        # levelPosition stands for a price out of some level
        # levelPosition = 0 for a price between level -1 and level 1
        # levelPosition = 1 for a price between level 1 and level 2
        # levelPosition = 6 for a price between level 6 and level 7
        # support self.levelNum = 7, levelPosition = 7 for a price out of level 7
        def levelPosition(price):
            for i in range(0, levelNum):
                if price >= levels[i] and price < levels[i+1]:
                    return i
                if price <= levels[-i] and price > levels[-i-1]:
                    return -i
            if price >= levels[levelNum-1]:
                return levelNum-1
            if price <= levels[-(levelNum-1)]:
                return -(levelNum-1)
            return None
        return levelPosition

    def initLevels(self, ep, levelNum, levelDiff):
        levels = dict()
        for i in range(0, levelNum+1):
            levels[i]  = ep + i * levelDiff
            levels[-i] = ep - i * levelDiff
        return levels

    def getOpenPosition(self, levelPosition):
        openPosition = 0
        # posPerPositiveLevel[0] is position when price is between level 1 and level 2
        # posPerPositiveLevel[1] is position when price is between level 2 and level 3
        # posPerNegativeLevel[0] is position when price is between level -1 and level -2
        # posPerNegativeLevel[1] is position when price is between level -2 and level -3
        # when levelNum = 7, posPerPositiveLevel[6] is position when price is out of level 7

        # levelPosition = 0, position = 0
        # levlePosition = 1, position = posPerPositiveLevel[0] 
        # levlePosition = 2, position = posPerPositiveLevel[0] + posPerPositiveLevel[1]
        # levlePosition = -1, position = posPerNegativeLevel[0] 
        # levlePosition = -2, position = posPerNegativeLevel[0] + posPerNegativeLevel[1]

        if levelPosition >= 1:
            for i in range(0, levelPosition):
                openPosition = openPosition - self.posPerPositiveLevel[i]
        if levelPosition <= -1:
            for i in range(0, -levelPosition):
                openPosition = openPosition + self.posPerNegativeLevel[i]

        return openPosition

    def initPosition(self, msg):
        price = None

        if msg.msgtype == msgType.barmsg \
            and msg.getContract() == self.contract:
            price = msg.open

        if msg.msgtype == msgType.tickmsg \
            and msg.getContract() == self.contract:
            price = float(msg.getContent())

        curLevel = self.levelPosition(price)
        vipinfor('Current price : %s' % price)
        vipinfor('Current level : %s' % curLevel)

        # market open positions
        openPosition = self.getOpenPosition(curLevel)
        vipinfor('Open position: %s' % openPosition)
        #self.oms.sendOrder(marketOrder, openPosition)  
        # prepare other limit positions
        self.updateLevelOrderMap(self.levelNum, self.levels, self.posPerPositiveLevel,\
                self.posPerNegativeLevel, curLevel)
        #self.showLevelOrderMap(self.levelNum)

    def clearLevelOrderMap(self, levelNum):
        for i in range(0, levelNum+1):
            self.levelOrderMap[i] = []
            self.levelOrderMap[-i] = []                

    def updateLevelOrderMap(self, levelNum, levels, posPerPositiveLevel,\
                             posPerNegativeLevel, curLevel):
        self.clearLevelOrderMap(levelNum)
        oid = 1

        if curLevel == 0:
            for i in range(1, levelNum+1):
                self.levelOrderMap[i].append(order(oid, self.contract, posPerPositiveLevel[i-1], \
                    levels[i], ActionType.sell, EntryExitType.entry, OrderType.limit, \
                    TimeInForce.day)) 
                self.levelOrderMap[-i].append(order(oid, self.contract, posPerNegativeLevel[i-1], \
                    levels[-i], ActionType.buy, EntryExitType.entry, OrderType.limit,\
                    TimeInForce.day)) 

        if curLevel > 0:
            for i in range(curLevel+1, levelNum+1):
                self.levelOrderMap[i].append(order(oid, self.contract, posPerPositiveLevel[i-1], \
                    levels[i], ActionType.sell, EntryExitType.entry, OrderType.limit, \
                    TimeInForce.day))
 
            for i in range(0, curLevel): 
                self.levelOrderMap[i].append(order(oid, self.contract, posPerPositiveLevel[i], \
                    levels[i], ActionType.buy, EntryExitType.exit, OrderType.limit, \
                    TimeInForce.day))

            for i in range(-levelNum, 0, -1): 
                self.levelOrderMap[i].append(order(oid, self.contract, posPerNegativeLevel[-i-1], \
                    levels[i], ActionType.buy, EntryExitType.entry, OrderType.limit, \
                    TimeInForce.day))
                 
        if curLevel < 0:
            for i in range(1, levelNum+1):
                self.levelOrderMap[i].append(order(oid, self.contract, posPerPositiveLevel[i-1], \
                    levels[i], ActionType.sell, EntryExitType.entry, OrderType.limit, \
                    TimeInForce.day))

            for i in range(curLevel+1, 1):
                self.levelOrderMap[i].append(order(oid, self.contract, posPerNegativeLevel[i], \
                    levels[i], ActionType.sell, EntryExitType.exit, OrderType.limit, \
                    TimeInForce.day))
                
            for i in range(-levelNum, curLevel):            
                self.levelOrderMap[i].append(order(oid, self.contract, posPerNegativeLevel[i], \
                    levels[i], ActionType.buy, EntryExitType.entry, OrderType.limit, \
                    TimeInForce.day))

    def showLevelOrderMap(self, levelNum):
        for i in range(levelNum, -levelNum, -1):
            vipinfor('Limit order in level %s' % i)
            orderlist = self.levelOrderMap[i]
            for o in orderlist:
                o.display()

