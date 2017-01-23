#!/usr/bin/python
###############################################################################
# indicator controller

from indicator.ma import SMA
from indicator.bollingerband import BollingerBand
from indicator.stochastic import stochastic

class indicatorController:

    def __init__(self):
        pass

    def makeSMA(self, period):
        return SMA(period)

    def makeEMA(self, period):
        return EMA(period)

    def makeBollingerBand(self, period, band):
        return BollingerBand(period, band)

    def makeStochastic(self, period, smooth1, smooth2):
        return stochastic(self, period, smooth1, smooth2)

