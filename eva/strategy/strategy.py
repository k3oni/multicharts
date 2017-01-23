#!/usr/bin/python
###############################################################################
from feed.feed import dataType
from datetime import timedelta, datetime
from tools.common import vipinfor, infor, err
from tools.observable import observable
from tools.timezonemap import datetimeTool
from threading import Timer
import time, Queue, signal
from strategymode import strategyMode
from oms import oms
from backtestmode import backtestMode
from livetrademode import livetradeMode
from papertrademode import papertradeMode

class strategy(observable):

    def __init__(self, engine, config):
        observable.__init__(self)
        self.engine = engine
        self.config = config
        self.dbs = self.engine.getDBService()
        self.barCtrl = self.engine.getBarController(self.dbs)
        self.indCtrl = self.engine.getIndicatorController()    
        self.modeHandler = None
        if  config.getMode()  == strategyMode.backtest:
            vipinfor('Backback for strategy %s' % config.getStrategyName())
            vipinfor('Backtest period from %s to %s' % (config.getStartDate(), \
                                                        config.getEndDate()))
            self.modeHandler = backtestMode(self)

        elif config.getMode() == strategyMode.paperTrading:
            vipinfor('Run paper trading for strategy %s' % config.getStrategyName())
            self.modeHandler = papertradeMode(self)

        elif config.getMode() == strategyMode.liveTrading:
            vipinfor('Run live trading for strategy %s' % config.getStrategyName())
            self.modeHander = livetradeMode(self)

        else:
            err('Strategy {name} has unsupport mode. No running.'.\
                format(config.getStrategyName()))
            return

    def __exit__(self):
        observable.__exit__(self)

    # strategy loop
    def run(self):
        self.onStrategyInit()
        self.runStrategy()
        self.onStrategyClear()
    
    def onStrategyInit(self):
        self.requestResource()

    def requestResource(self):
        pass

    def runStrategy(self):
        self.modeHandler.run()

    def onStrategyClear(self):
        pass

    # these callback are in strategy mode
    def onSessionInit(self, sessionStart, sessionEnd):
        infor("Start session %s - %s" % (sessionStart, sessionEnd))

    def onSessionClear(self, sessionStart, sessionEnd):
        infor("End session %s - %s" % (sessionStart, sessionEnd))

    def onMsg(self, msg):
        pass
    
    # system service
    def signal_handler(self):
        pass 

    def getToday(self):
        return self.engine.getToday()

    def now(self):
        return self.engine.now()

    def getConfig(self):
        return self.config
    
    def getBinder(self):
        if self.config.getMode() == strategyMode.paperTrading or \
            self.config.getMode() == strategyMode.liveTrading:
            return self.modeHandler.binder
        else:
            return None 

    def getNonBinder(self):
        if self.config.getMode() == strategyMode.paperTrading or \
            self.config.getMode() == strategyMode.liveTrading:
            return self.modeHandler.nonbinder
        else:
            return None 

    def getOMS(self):
        return self.modeHandler.getOMS()
