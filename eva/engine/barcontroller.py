#!/usr/bin/python
'''
Class barController provides all kinds of bar data service
'''

from feed.feed import dataType, feedType
from feed.feedfactory import feedFactory
from feed.hdfbarfeed import hdfBarFeed    
from evadb.dbservice import dbservice
from datetime import datetime, timedelta
from tools.logger import vipinfor, infor, debugger, err
from muxer import muxer
from enum import Enum
from bar.bar import barField, barLength
from tools.timezonemap import datetimeTool
import pandas as pd
from feed.constrainfactory import constrainFactory
import pytz
from tools.bbg2IB import toIBContract

class barController:

    def __init__(self,  dbservice, syscfg, today):
        self.constrains = dict()
        self.dbs = dbservice
        self.syscfg = syscfg
        self.feed = []
        self.today = today
        self.localTimezone = pytz.timezone(syscfg['timezone'])

    ############################################################################
    # system api
    def now(self):
        return self.localTimezone.localize(datetime.now())
    
    ############################################################################
    # level 1 api used by server
    # liveStreamTo is used by server to deliver data
    def liveStreamTo(self, socket, beg, end, topic):
        msgs = self.getLiveMsgs()

        while self.now() < beg - timedelta(seconds = 30):
            time.sleep(10)
            infor("sleeping ...")
  
        while self.now() <= end:
            m = msgs.next()
            m.display()
            buf = m.toZmqBuffer()
            socket.send_multipart([topic, buf])
                        
    # prepareLiveData is used by server to prepare data
    def prepareLiveData(self, instr, datatype, today, sessionBegin, sessionEnd,\
                             barLength=None):
        cf = constrainFactory(self.dbs)
        if datatype == dataType.liveTickData:        
            self.liveTickFeed = feedFactory().createFeed(feedType.UrlFeed, \
                                 self.syscfg['EvaTickUrl'], dataType.liveTickData,\
                                    timezone = self.localTimezone)
            self.liveTickFeed.addConstrains(cf.createInstrumentConstrain(instr, today))
            self.liveTickFeed.setCheckTimePoint(timedelta(seconds=60), \
                                sessionBegin, sessionEnd, timedelta(seconds=60))
            self.feed = self.liveTickFeed

        elif datatype == dataType.liveBarData:
            if barLength <> None:
                self.liveBarFeed = feedFactory().createFeed(feedType.UrlFeed, \
                                    self.syscfg['EvaBarUrl'], dataType.liveBarData,\
                                     timezone = self.localTimezone)
                self.liveBarFeed.addConstrains(cf.createInstrumentConstrain(instr, today))
                self.liveBarFeed.setCheckTimePoint(timedelta(seconds=60), \
                                    sessionBegin, sessionEnd, timedelta(seconds=60))
                self.liveBarFeed.setBarGenerator(barLength, sessionBegin, sessionEnd)
                self.feed = self.liveBarFeed
            else:
                err('Request for bar data but bar Length is set to None.', color='red')
        else:
            infor("Cannot tell data type")            

    ###########################################################################
    # level 2 api used by level 1 api
    # generate live msgs
    def getLiveMsgs(self):
        fd = self.feed
        while True:
            msg = fd.getNextMsg()
            if msg <> None:
                yield msg

    def addConstrains(self, feed, constrain):
        if feed not in self.constrains.keys():
            self.constrains[feed] = []
        self.constrains[feed].append(constrain)

    ###########################################################################
    # data in form of messages
    # this function creates messages for each trading session
    # in design, each feed only hanlde contract information
    # and we should create a feed for each contract when it is active
    # currently, bar data is supported and in the future tick data is supported
    # since tick data is large, it is assume tick data are stored in a daily file
    # I will load data day by day 

    def createSessionData(self, ds):
        sessionData = dict()
        tradday = self.dbs.getTradingDate(ds.getInstrument(), \
                       ds.getStartDate(), ds.getTillDate())

        # instrument data file
        src = self.dbs.getInstrumentFilePath(ds.getInstrument())
        tz  = self.dbs.getTimezone(ds.getInstrument())
        # for each session per trading day, generate messages
        for day in tradday:
            # generate data feed
            d = day[0]
            contract = self.dbs.getActiveContract(ds.getInstrument(), d)
            expire = self.dbs.getExpireDate(contract)
            fd = feedFactory().createFeed(feedType.hdfBarFeed, \
                                src, \
                                ds.getDataType(), \
                                self.localTimezone,\
                                instrument = ds.getInstrument(), \
                                contract = toIBContract(contract),\
                                expireYear = str(expire.year),\
                                expireMonth = str(expire.month),\
                                barlen = ds.getBarLength().barlen)

            # trading hours for d day
            tradhours = self.dbs.getTradingHour(ds.getInstrument(), d, d)
            fd.setDataSrc(d, d, tradhours)

            # package messages in each session
            for th in tradhours:
                msgset = []
                fd.reset()                
                while not fd.isEnd():
                    msg = fd.getNextMsg()
                    if th[0] <= msg.getBarStartTime() and msg.getBarStartTime() <= th[1]:
                        msgset.append(msg)
                sessionData[th] = msgset

        return sessionData
    
    def getMessageStream(self, datasrcs, start ,end):
        sessionDS = dict()
        for ds in datasrcs:
            sessionDS[ds] = self.createSessionData(ds)        

        # strategy start and end trading hours
        tradhour = self.dbs.getTradingHour(datasrcs[0].getInstrument(), start, end)
        ms = dict()
        for session in tradhour:
            ms[session] = muxer(sessionDS, session)

        return ms

    def checkDailyBar(self, dataTS, instrument, since, till):
        dates = self.dbs.getTradingDate(instrument, since, till)
        if len(dates) <> len(dataTS):
            err('Daily Bar retrieved and required does not match.')
            err('Dates form reference data, Length %s' % len(dates))
            err(dates)
            err('Dates from daily data, Length %s' % len(dataTS))
            err(dataTS)
            return False
        return True

    # data in form of list of data
    def getBlockData(self, instrument, barlen, datatype, since, till, field=None):
        status = True
        data_contract_list = self.dbs.getActiveContractGroup(instrument, since, till)
        df = pd.DataFrame()        
        tz = self.dbs.getTimezone(instrument)
        field = map(lambda x:x.value, field)
 
        # get each contract and load data for each contract
        for dc in data_contract_list:
            start = dc[0]
            end = dc[1]
            contract = dc[2]
            expire = dc[3]
            expireYear = str(expire.year)
            expireMonth = "%02d" % expire.month
            hbfeed = hdfBarFeed(datatype, self.dbs.getInstrumentFilePath(instrument), \
                    self.localTimezone, instrument, contract, expireYear, expireMonth, barlen)
            
            # intraday bars
            if barlen == barLength.min1 or barlen == barLength.hourly:
                tradhour = self.dbs.getTradingHour(instrument, start, end)
                block =  hbfeed.getBlockData(start, end, tradhour, field)
            # daily bar
            elif barlen == barLength.daily:
                block = hbfeed.getDailyBar(start, end, field)
                status = self.checkDailyBar(block['timestamp'], instrument, start, end)
            else:
                err("Bar type %s is not supported." % barlen)
                status = False

            df = df.append(block)
            df = df.sort(['timestamp'])

        result = [df['timestamp'].tolist()]

            
        for f in field:
            result = result + [df[f].tolist()]
        return status, result
