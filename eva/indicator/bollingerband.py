#!/usr/bin/python
###############################################################################
# Bollinger Band
from ma import SMA
from collections import deque
from mstd import movingStd
from operator import add 
from tools.common import infor

class BollingerBand:

    def __init__(self, period, band):
        self.band = band
        self.period = period
        self.deque = []
        self.smagen = []
        self.mstdgen = []
        self.bandvalue = []
        self.isdebug = True

    def getInitBB(self, initdata):

        # moving average
        self.smagen = SMA(self.period)
        self.smagen.initSMA(initdata)

        # moving std
        self.mstdgen =  movingStd(self.period)
        self.mstdgen.initMovingStd(initdata)
        
        ma = self.smagen.getSMA()
        band = [b * self.band for b in self.mstdgen.getStd()]
        self.bandvalue = [sum(x) for x in zip(ma, band)]
        
        return self.bandvalue[-1]
    
    def update(self, datapoint):
        ma = self.smagen.update(datapoint)
        band = self.band * self.mstdgen.update(datapoint)
        self.bandvalue.append(ma + band)
        return self.bandvalue[-1]

    def getBand(self):
        return self.bandvalue[-1]

