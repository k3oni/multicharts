#!/usr/bin/python
#####################################################################
# stochastic oscillator
from collections import deque
from ma import SMA
import random
from tools.common import infor

class stochastic:
    
    def __init__(self, period, smooth1, smooth2):
        self.period = period
        self.smooth1 = smooth1
        self.smooth2 = smooth2
        self.dequeHigh = []
        self.dequeLow = []
        self.dequeClose = []
        self.maxlen = period 
        self.fastK = []
        self.slowK = [] #slowK or fastD#
        self.slowD = [] #slowD#
        self.isdebug = False 

    def initData(self, initHigh, initLow, initClose):
        if len(initHigh) != len(initLow) or len(initLow) != len(initClose):
            raise ValueError('Stochastic: initial data have no equal length')
        
        if len(initHigh) < self.period:
            raise ValueError('Insufficient data to initialize stochastic')

        self.dequeHigh = deque(initHigh[0:self.period], self.maxlen)
        self.dequeLow = deque(initLow[0:self.period], self.maxlen)
        self.dequeClose = deque(initClose[0:self.period], self.maxlen)
        
        self.updateFastK()
        for i in range(self.period, len(initHigh)):
            self.updateData(initHigh[i], initLow[i], initClose[i])
            self.updateFastK()
        
        self.slowK = SMA(self.smooth1)
        self.slowK.initSMA(self.fastK)

        self.slowD = SMA(self.smooth2)
        self.slowD.initSMA(self.slowK.getSMA())

        return self.getFastK(), self.getFastD(), self.getSlowK(), self.getSlowD()
        
    def updateData(self, high, low, close):
        self.dequeHigh.append(high)
        self.dequeLow.append(low)
        self.dequeClose.append(close)

    def updateFastK(self):
        high = max(self.dequeHigh)
        low  = min(self.dequeLow)
        close = self.dequeClose[-1]

        if high == low:
            fastk = 0
        else:
            fastk = float(close-low)/float(high-low) * 100

        self.fastK.append(fastk)

    def update(self, high, low, close):
        self.updateData(high, low, close)
        self.updateFastK()
        fastD = self.slowK.update(self.fastK[-1])
        self.slowD.update(fastD)
        return self.getFastK()[-1], self.getFastD()[-1], \
                self.getSlowK()[-1], self.getSlowD()[-1]

    def getFastK(self):
        return self.fastK

    def getFastD(self):
        return self.slowK.getSMA()
        
    def getSlowK(self):
        return self.getFastD()

    def getSlowD(self):
        return self.slowD.getSMA()

class stochastic2:
    
    def __init__(self, period, smooth1, smooth2):
        self.period = period
        self.smooth1 = smooth1
        self.smooth2 = smooth2
        self.dequeHigh = []
        self.dequeLow = []
        self.dequeClose = []
        self.maxlen = period 
        self.fastK = []
        self.slowK = [] 
        self.slowD = [] 
        self.close_low_data = []
        self.close_low_sma = []
        self.high_low_data = []
        self.high_low_sma = []

    def initData(self, initHigh, initLow, initClose):
        if len(initHigh) != len(initLow) or len(initLow) != len(initClose):
            raise ValueError('Stochastic: initial data have no equal length')
        
        if len(initHigh) < self.period*2:
            raise ValueError('Insufficient data. Need %s data to initialize stochastic'\
                                 % self.period*2)

        self.dequeHigh = deque(initHigh[0:self.period], self.maxlen)
        self.dequeLow = deque(initLow[0:self.period], self.maxlen)
        self.dequeClose = deque(initClose[0:self.period], self.maxlen)
        self.updateHLCL()

        for i in range(self.period, len(initHigh)):
            self.updateData(initHigh[i], initLow[i], initClose[i])
            self.updateHLCL()

        # init fastK 
        self.fastK = [x/y*100 if y<>0 else 0 for x, y in zip(self.close_low_data, \
                        self.high_low_data)]

        # init slowK 
        self.high_low_sma = SMA(self.smooth1)
        self.high_low_sma.initSMA(self.high_low_data)

        self.close_low_sma = SMA(self.smooth1)
        self.close_low_sma.initSMA(self.close_low_data)

        self.slowK = [x/y*100 if y<>0 else 0 for x, y in\
                        zip(self.close_low_sma.getSMA(), self.high_low_sma.getSMA())]

        self.slowD = SMA(self.smooth2)
        self.slowD.initSMA(self.slowK)

        return self.getFastK(), self.getFastD(), self.getSlowK(), self.getSlowD()

    def updateData(self, high, low, close):
        self.dequeHigh.append(high)
        self.dequeLow.append(low)
        self.dequeClose.append(close)

    def updateHLCL(self):
        high = max(self.dequeHigh)
        low  = min(self.dequeLow)
        close = self.dequeClose[-1]
        self.close_low_data.append(close-low)
        self.high_low_data.append(high-low)
        
    def updateFastK(self):
        high = max(self.dequeHigh)
        low  = min(self.dequeLow)
        close = self.dequeClose[-1]

        if high == low:
            fastk = 0
        else:
            fastk = float(close-low)/float(high-low) * 100

        #infor("high %s low %s close %s fastk %s" % (high, low, close, fastk))
        #self.fastK.append(fastk)

    def updateSlowK(self):
        high = max(self.dequeHigh)
        low  = min(self.dequeLow)
        close = self.dequeClose[-1]
    
        hl = self.high_low_sma.update(high-low)
        cl = self.close_low_sma.update(close-low)
        self.slowK.append(cl/hl if hl <>0  else 0)
        return self.slowK[-1]

    def update(self, high, low, close):
        self.updateData(high, low, close)
        self.updateFastK()
        lastSlowK = self.updateSlowK()
        self.slowD.update(lastSlowK)
        return self.getFastK()[-1], self.getFastD()[-1], \
                self.getSlowK()[-1], self.getSlowD()[-1]

    def getFastK(self):
        return self.fastK

    def getFastD(self):
        return self.slowK
        
    def getSlowK(self):
        return self.getFastD()

    def getSlowD(self):
        return self.slowD.getSMA()
