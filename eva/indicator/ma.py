#!/usr/bin/python
###############################################################################
# simple mean average
from tools.common import infor

class SMA:
    def __init__(self, period):
        self.period = period
        # use array for sma
        self.sma = []
        self.index = 0

        # use circular array for data
        self.histmax = 2 * period
        self.hist = [None] * self.histmax
        self.head = 0
        self.tail = period

    def initSMA(self, initdata):
        if self.period > len(initdata):
            raise ValueError('Insufficient data to initialize SMA')
        
        self.sma.append(sum(initdata[self.head:self.tail])/float(self.period))

        for i in range(self.head, self.tail):
            self.hist[i] = initdata[i]

        for i in range(self.period, len(initdata)):
            self.update(initdata[i])

        return self.sma[-1]
        
    def update(self, datapoint):
        newsum = self.sma[self.index]*self.period-self.hist[self.head]+datapoint

        # update sma and its index
        self.sma.append(newsum/float(self.period))
        self.index = self.index + 1

        # update circular data array
        self.hist[self.tail] = datapoint
        self.head = (self.head + 1) % self.histmax
        self.tail = (self.tail + 1) % self.histmax
        return self.sma[-1]

    def getSMA(self):
        return self.sma
                
        
class EMA:
    def __init__(self, period):
        self.weight = 2 / float(period + 1)
        self.ema = []
        self.index = 0

    def initEMA(self, initdata):
        for d in initdata:
            self.update(d)
        return self.ema[-1]       

    def update(self, datapoint):
        if self.index == 0:
            self.ema.append(datapoint)
        else:
            self.ema.append(float(1-self.weight)*self.ema[-1]\
                                +float(self.weight)*datapoint)
        self.index = self.index + 1

        return self.ema[-1]

    def log(self):
        print('ema ' + str(self.index-1) + ' ' + str(self.ema[self.index-1]))
         
