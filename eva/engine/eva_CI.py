#!/usr/bin/python
###############################################################################
# platform is the backtest system with everything else as its component

import sys, os
sys.path.append('/home/delvin/code/python/eva')

from tools.common import infor, err
from jsonconfig import jsonConfig
from barcontroller import barController
from indicatorcontroller import indicatorController
from strategycontrol import strategyControl
from evadb.dbservice import dbservice
from datetime import datetime
from pytz import timezone
import signal

class EVA:

    def __init__(self, today, tz):
        self.cfg = []
        self.today = today
        self.ctrlc = False
        signal.signal(signal.SIGINT, self.signal_handler)
        self.tz = tz

    # duty 1: load previous configure
    def loadConfig(self, src):
        jcfg = jsonConfig()
        self.cfg = jcfg.load(src)

    # duty 2: allocate resource for research or strategy
    def getBarController(self, dbservice):
        return barController(dbservice, self.cfg.getSystemConfig(), self.today)

    def getIndicatorController(self):
        return indicatorController()

    def getDBService(self):
        return dbservice(self.cfg.system['dbname'], \
                         self.cfg.system['dbuser'], \
                         self.cfg.system['dbpasswd'],\
                         self.cfg.system['dbip'],\
                         self.cfg.system['dbport'])

    def makeStrategy(self, stratcfg):
        strat = strategyControl().createStrategy(self, stratcfg)
        return strat

    # duty 3: spawn research or strategy project
    def initialize(self, src):
        self.loadConfig(src)
        self.localtz = timezone(self.cfg.system['timezone'])

    def getToday(self):
        return self.today

    def now(self):
        return self.localtz.localize(datetime.now())
    
    def getConfig(self):
        return self.cfg

    def getCtrlC(self):
        return self.ctrlc

    def signal_handler(self, signal, frame):
        self.ctrlc = True
        infor('EVA received ctrl+C signal. Exit now.')
        sys.exit(0)

    def run(self):
        stratcfgs = self.cfg.getStratCfg()
        for cfg in stratcfgs:
            strat = self.makeStrategy(cfg)
            strat.run()       

    def helloworld(self):
        infor("Hello, I am EVA Version 1.0.")
        infor("Today is %s." % self.today.strftime('%Y-%m-%d'))

if __name__ == '__main__':
    tz = 'Asia/Hong_Kong'
    today = timezone(tz).localize(datetime.today())
    eva = EVA(today, tz)
    eva.initialize('/home/delvin/code/python/eva/engine/CI_backtest.eva')
    eva.helloworld()
    eva.run()
