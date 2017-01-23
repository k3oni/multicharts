#!/usr/bin/python
################################################################################

from strategy import strategy
from strategy.ep import EP
from strategy.meanreversion import meanReversion
from tools.common import infor

class strategyControl:

    def __init__(self):
        self.strategy = strategy
        self.EP = EP
        self.meanReversion = meanReversion

    def createStrategy(self, engine, cfg):
        class_ = getattr(self, cfg.getStrategyName()) 
        return class_(engine, cfg) 
