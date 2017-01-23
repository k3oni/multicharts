#!/usr/bin/python
###############################################################################
## tickfeed provide tick data
## current only support tickdata forward from zmq server

import abc, threading
from enum import Enum
from tools.common import infor
from tools.timezonemap import datetimeTool
from datetime import datetime, timedelta

class dataType(Enum):
    liveTickData = 1
    liveBarData  = 2
    historicalTickData = 3
    historicalBarData = 4

class feedType:
    UrlFeed = 1
    FileFeed = 2
    hdf5Feed = 3
    hdfBarFeed = 4

class feed(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, dataType, timezone):
        self.dataType = dataType
        self.constrains = []
        self.lastMsgTS = None
        self.timezone = timezone

    @abc.abstractmethod
    def setDataSrc(self, src):
        return
    
    @abc.abstractmethod
    def getRawMsg(self):
        pass

    @abc.abstractmethod
    def postProcess(self, msg):
        pass

    def getNextMsg(self):
        msg = self.getRawMsg()
        self.lastMsgTS = msg.dt
        if self.isInterested(msg):
            msg = self.postProcess(msg)
            return msg
        else:
            return None

    def isInterested(self, msg):
        for c in self.constrains:
            if not c(msg):
                return False
        return True  

    def addConstrains(self, constrain):
        self.constrains.append(constrain)

    def getNextZMQMsg(self):
        return

    def isEnd(self):
        return

    def now(self):
        return self.timezone.localize(datetime.now())

    # check if data is received on time    
    def setCheckTimePoint(self, checkPeriod, begin, end, validPeriod):
        timeslot = datetimeTool.generateTimeSlot(checkPeriod, begin, end)       
        self.lastMsgTS = self.now()
        infor("Start up for checking data update %s" % self.lastMsgTS, color='green')
        for ts in timeslot:
            if ts >= self.lastMsgTS:
                delay = (ts - self.now()).total_seconds()
                threading.Timer(delay, self.checkDataUpdate, \
                    [ts, checkPeriod, end, validPeriod]).start()
                break

    def checkDataUpdate(self, ts, checkPeriod, end, validPeriod):
        result = True
        if ts > self.lastMsgTS + validPeriod:
            infor('Warning: No data updated since %s' % self.lastMsgTS, color='red')
            result = False
        nextTS = ts + checkPeriod
        if nextTS < end:
            delay = (nextTS-self.now()).total_seconds()
            threading.Timer(delay, self.checkDataUpdate, \
                [nextTS, checkPeriod, end, validPeriod]).start()
        return result   
