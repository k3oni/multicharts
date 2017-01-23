#!/usr/bin/python
###############################################################################
# tradingCalendar will fill trading calendar and trading hour for each instrument
# into database

import calendar 
import re
from enum import Enum
from tools.common import infor, err
from evadb.dbtool import dbtool
from dbentity import dbEntity
from datetime import datetime
from tools.timezonemap import timeZoneMap

class daytype(Enum):
    tradingDay = 1
    morningTradingDay = 2
    noTradingDay = 3

class evaCalendar(dbEntity):

    def __init__(self, dbname, dbuser, dbpasswd, tablename, instruTable):
        dbEntity.__init__(self, dbname, dbuser, dbpasswd, tablename)
        self.sdHandler = dict()
        self.sdHandler[daytype.morningTradingDay] = \
                self.handleMorningTradingDay
        self.sdHandler[daytype.noTradingDay] = \
                self.handleNoTradingDay
        self.instruTable = instruTable

    def createTable(self):
        sql = 'create table {tablename}(\
               instrid int,\
               update_ts timestamp with time zone,\
               datetime timestamp with time zone,\
               isTradingDay bool,\
               sessionStart timestamp with time zone,\
               sessionEnd  timestamp with time zone,\
               primary key (instrid, datetime, sessionStart, sessionEnd)\
               );'.format(tablename = self.tablename)
        self.dbtool.execute(sql)

    def fill(self, instruname):
        fut, suff = instruname.split()
        func = "run" + fut
        if func in dir(self):
            getattr(self, func)()
        else:
            err("Cannot run %s" % func)

    ###########################################################################
    #  functional operation
    #  since and till are datetime types
    def getTradingDate(self, instrument, since, till):
        instruid = self.instruTable.getInstrumentId(instrument)
        sql = "select distinct datetime from %s \
                where instrid=%d and datetime between \
                '%s' and '%s' and istradingday = true order by datetime; " % \
                (self.tablename, instruid, since, till)
        dates = self.dbtool.fetch(sql)
        if dates is None:
            infor("No trading day between %s and %s." % (since, till))
        return dates


    def getPreviousNTradingDate(self, instrument, date, N):
        instruid = self.instruTable.getInstrumentId(instrument)
        sql = "select distinct datetime from {fn} where instrid={iid} \
                and istradingday = true and datetime < '{dt}' \
                order by datetime desc limit {N};".format(\
                fn=self.tablename, iid=instruid, dt=date, N=N)
        dates = self.dbtool.fetch(sql)
        if len(dates) > 0:
            return dates[0][0]
        else:
            return None

    def getTradingHour(self, instrument, since, till):
        if since == None or till == None:
            infor('Invalid period with since date {sn} and till date {till}').\
                format(sn=since, till=till)
            return

        instruid = self.instruTable.getInstrumentId(instrument)

        sql = "select sessionstart, sessionend from %s \
                where instrid=%d and datetime between \
                '%s' and '%s' and istradingday = true order by datetime, sessionstart; " % \
                (self.tablename, instruid, since, till)
        hours = self.dbtool.fetch(sql)
        return hours
        
    ###########################################################################
    #  operation of db
    def insertCalendarItem(self, instrument, dt, isTrading, sessionStart, sessionEnd):
        instrId = self.instruTable.getInstrumentId(instrument)
        if sessionStart is None or sessionEnd is None:
            dtstart = dt
            dtend = dt
        else:
            dtstart = dt + timeZoneMap.getDeltaFromTime(sessionStart)
            dtend   = dt + timeZoneMap.getDeltaFromTime(sessionEnd)
        prefix = 'insert into {tn} values ('.format(tn = self.tablename)
        suffix = ');'
        statement = "%d, '%s', '%s', %s, '%s', '%s'" % \
                    (instrId, datetime.today(), dt, isTrading, dtstart, dtend)

        self.dbtool.execute(prefix + statement + suffix)

        check = "select count(*) from %s where instrid=%d and datetime='%s'and\
                    istradingday=%s and sessionstart='%s' and sessionend='%s'" %\
                (self.tablename, instrId, dt, isTrading, dtstart, dtend)
        self.dbtool.checkInserted(check, statement)       
 
    def deleteCalendarItem(self, instrument, date):
        instruid = self.instruTable.getInstrumentId(instrument)
        sql = "delete from %s where instrid = %s and datetime = '%s';" \
                % (self.tablename, instruid, date)
        self.dbtool.execute(sql)

        check = "select count(*) from %s where instrid=%s and datetime='%s';" \
            % (self.tablename, instruid, date)
        self.dbtool.checkDeleted(check, sql)        

    # set weekend days as non-trading days
    def setRegularDay(self, instru, timezone, yearStart, yearEnd, 
                            sessionStart, sessionEnd):

        for y in range(yearStart, yearEnd+1):
            for m in range(1, 13):
                ran = calendar.monthrange(y, m)
                for d in range(1, ran[1]+1):
                    dt = datetime(y, m, d)
                    dt = timeZoneMap.getDatetimeWithTimezone(dt, timezone)
                    isTrading = calendar.weekday(y,m,d) <= 4 # weekday
                    self.insertCalendarItem(instru, dt, isTrading, \
                        sessionStart, sessionEnd)

    def handleNoTradingDay(self, instrument, date, **kargs):
        self.deleteCalendarItem(instrument, date)
        self.insertCalendarItem(instrument, date, False, None, None)

    def handleMorningTradingDay(self, instrument, date, **kargs):
        self.deleteCalendarItem(instrument, date)
        self.insertCalendarItem(instrument, date, True, \
                kargs['sessionStart'], kargs['sessionEnd'])

    
    ###########################################################################
    # calendar for each specific futures

    def runHI1(self):
        instru = 'HI1 Index'
        timezone = self.instruTable.getInstrumentTimezone(instru)
        self.setRegularDay(instru, timezone, 2013, 2016, '09:15:00', '12:00:00')
        self.setRegularDay(instru, timezone, 2013, 2016, '13:00:00', '16:15:00')

        sd = dict()
        morningSessionStart = dict()
        morningSessionEnd = dict()

        # 2013 
        sd['20130101'] = daytype.noTradingDay
        sd['20130211'] = daytype.noTradingDay
        sd['20130212'] = daytype.noTradingDay
        sd['20130329'] = daytype.noTradingDay
        sd['20130401'] = daytype.noTradingDay
        sd['20130404'] = daytype.noTradingDay
        sd['20130501'] = daytype.noTradingDay
        sd['20130517'] = daytype.noTradingDay
        sd['20130612'] = daytype.noTradingDay
        sd['20130701'] = daytype.noTradingDay
        sd['20130920'] = daytype.noTradingDay
        sd['20131001'] = daytype.noTradingDay
        sd['20131014'] = daytype.noTradingDay
        sd['20131225'] = daytype.noTradingDay
        sd['20131226'] = daytype.noTradingDay
        
        sd['20131224'] = daytype.morningTradingDay
        sd['20131231'] = daytype.morningTradingDay
        
        morningSessionStart['20131224'] = '09:15:00'
        morningSessionEnd['20131224'] = '12:00:00'
        morningSessionStart['20131231'] = '09:15:00'
        morningSessionEnd['20131231'] = '12:00:00'
       
        
        # 2014 
        sd['20140101'] = daytype.noTradingDay
        sd['20140131'] = daytype.noTradingDay
        sd['20140203'] = daytype.noTradingDay
        sd['20140418'] = daytype.noTradingDay
        sd['20140421'] = daytype.noTradingDay
        sd['20140404'] = daytype.noTradingDay
        sd['20140501'] = daytype.noTradingDay
        sd['20140506'] = daytype.noTradingDay
        sd['20140602'] = daytype.noTradingDay
        sd['20140701'] = daytype.noTradingDay
        sd['20140909'] = daytype.noTradingDay
        sd['20141001'] = daytype.noTradingDay
        sd['20141002'] = daytype.noTradingDay
        sd['20141225'] = daytype.noTradingDay
        sd['20141226'] = daytype.noTradingDay
        
        sd['20140130'] = daytype.morningTradingDay
        sd['20141224'] = daytype.morningTradingDay
        sd['20141231'] = daytype.morningTradingDay

        morningSessionStart['20140130'] = '09:15:00'
        morningSessionEnd['20140130'] = '12:00:00'
        morningSessionStart['20141224'] = '09:15:00'
        morningSessionEnd['20141224'] = '12:00:00'
        morningSessionStart['20141231'] = '09:15:00'
        morningSessionEnd['20141231'] = '12:00:00'

        # 2015 
        sd['20150101'] = daytype.noTradingDay
        sd['20150219'] = daytype.noTradingDay
        sd['20150220'] = daytype.noTradingDay
        sd['20150403'] = daytype.noTradingDay
        sd['20150406'] = daytype.noTradingDay
        sd['20150407'] = daytype.noTradingDay
        sd['20150501'] = daytype.noTradingDay
        sd['20150525'] = daytype.noTradingDay
        sd['20150701'] = daytype.noTradingDay
        sd['20150903'] = daytype.noTradingDay
        sd['20150928'] = daytype.noTradingDay
        sd['20151001'] = daytype.noTradingDay
        sd['20151021'] = daytype.noTradingDay
        sd['20151225'] = daytype.noTradingDay
        
        sd['20150218'] = daytype.morningTradingDay
        sd['20151224'] = daytype.morningTradingDay
        sd['20151231'] = daytype.morningTradingDay
        
        morningSessionStart['20150218'] = '09:15:00'
        morningSessionEnd['20150218'] = '12:00:00'
        morningSessionStart['20151224'] = '09:15:00'
        morningSessionEnd['20151224'] = '12:00:00'
        morningSessionStart['20151231'] = '09:15:00'
        morningSessionEnd['20151231'] = '12:00:00'

        # 2016
        sd['20160101'] = daytype.noTradingDay
        sd['20160208'] = daytype.noTradingDay
        sd['20160209'] = daytype.noTradingDay
        sd['20160210'] = daytype.noTradingDay
        sd['20160325'] = daytype.noTradingDay
        sd['20160328'] = daytype.noTradingDay
        sd['20160404'] = daytype.noTradingDay
        sd['20160502'] = daytype.noTradingDay
        sd['20160609'] = daytype.noTradingDay
        sd['20160701'] = daytype.noTradingDay
        sd['20160916'] = daytype.noTradingDay
        sd['20161010'] = daytype.noTradingDay
        sd['20161226'] = daytype.noTradingDay
        sd['20161227'] = daytype.noTradingDay

        for k in sd.keys():
            self.sdHandler[sd[k]](instru, datetime.strptime(k,'%Y%m%d'), \
                    sessionStart = morningSessionStart.get(k),\
                    sessionEnd = morningSessionEnd.get(k)) 

    def runHC1(self):
        
        instru = 'HC1 Index'
        timezone = self.instruTable.getInstrumentTimezone(instru)

        self.setRegularDay(instru, 'Asia/Hong_Kong', 2013, 2016, '09:15:00', '12:00:00')
        self.setRegularDay(instru, 'Asia/Hong_Kong', 2013, 2016, '13:00:00', '16:15:00')

        sd = dict()
        morningSessionStart = dict()
        morningSessionEnd = dict()

        # 2013 
        sd['20130101'] = daytype.noTradingDay
        sd['20130211'] = daytype.noTradingDay
        sd['20130212'] = daytype.noTradingDay
        sd['20130329'] = daytype.noTradingDay
        sd['20130401'] = daytype.noTradingDay
        sd['20130404'] = daytype.noTradingDay
        sd['20130501'] = daytype.noTradingDay
        sd['20130517'] = daytype.noTradingDay
        sd['20130612'] = daytype.noTradingDay
        sd['20130701'] = daytype.noTradingDay
        sd['20130920'] = daytype.noTradingDay
        sd['20131001'] = daytype.noTradingDay
        sd['20131014'] = daytype.noTradingDay
        sd['20131225'] = daytype.noTradingDay
        sd['20131226'] = daytype.noTradingDay
        
        sd['20131224'] = daytype.morningTradingDay
        sd['20131231'] = daytype.morningTradingDay
        
        morningSessionStart['20131224'] = '09:15:00'
        morningSessionEnd['20131224'] = '12:00:00'
        morningSessionStart['20131231'] = '09:15:00'
        morningSessionEnd['20131231'] = '12:00:00'
       
        
        # 2014 
        sd['20140101'] = daytype.noTradingDay
        sd['20140131'] = daytype.noTradingDay
        sd['20140203'] = daytype.noTradingDay
        sd['20140418'] = daytype.noTradingDay
        sd['20140421'] = daytype.noTradingDay
        sd['20140404'] = daytype.noTradingDay
        sd['20140501'] = daytype.noTradingDay
        sd['20140506'] = daytype.noTradingDay
        sd['20140602'] = daytype.noTradingDay
        sd['20140701'] = daytype.noTradingDay
        sd['20140909'] = daytype.noTradingDay
        sd['20141001'] = daytype.noTradingDay
        sd['20141002'] = daytype.noTradingDay
        sd['20141225'] = daytype.noTradingDay
        sd['20141226'] = daytype.noTradingDay
        
        sd['20140130'] = daytype.morningTradingDay
        sd['20141224'] = daytype.morningTradingDay
        sd['20141231'] = daytype.morningTradingDay

        morningSessionStart['20140130'] = '09:15:00'
        morningSessionEnd['20140130'] = '12:00:00'
        morningSessionStart['20141224'] = '09:15:00'
        morningSessionEnd['20141224'] = '12:00:00'
        morningSessionStart['20141231'] = '09:15:00'
        morningSessionEnd['20141231'] = '12:00:00'

        # 2015 
        sd['20150101'] = daytype.noTradingDay
        sd['20150219'] = daytype.noTradingDay
        sd['20150220'] = daytype.noTradingDay
        sd['20150403'] = daytype.noTradingDay
        sd['20150406'] = daytype.noTradingDay
        sd['20150407'] = daytype.noTradingDay
        sd['20150501'] = daytype.noTradingDay
        sd['20150525'] = daytype.noTradingDay
        sd['20150701'] = daytype.noTradingDay
        sd['20150903'] = daytype.noTradingDay
        sd['20150928'] = daytype.noTradingDay
        sd['20151001'] = daytype.noTradingDay
        sd['20151021'] = daytype.noTradingDay
        sd['20151225'] = daytype.noTradingDay
        
        sd['20150218'] = daytype.morningTradingDay
        sd['20151224'] = daytype.morningTradingDay
        sd['20151231'] = daytype.morningTradingDay
        
        morningSessionStart['20150218'] = '09:15:00'
        morningSessionEnd['20150218'] = '12:00:00'
        morningSessionStart['20151224'] = '09:15:00'
        morningSessionEnd['20151224'] = '12:00:00'
        morningSessionStart['20151231'] = '09:15:00'
        morningSessionEnd['20151231'] = '12:00:00'

        # 2016
        sd['20160101'] = daytype.noTradingDay
        sd['20160208'] = daytype.noTradingDay
        sd['20160209'] = daytype.noTradingDay
        sd['20160210'] = daytype.noTradingDay
        sd['20160325'] = daytype.noTradingDay
        sd['20160328'] = daytype.noTradingDay
        sd['20160404'] = daytype.noTradingDay
        sd['20160502'] = daytype.noTradingDay
        sd['20160609'] = daytype.noTradingDay
        sd['20160701'] = daytype.noTradingDay
        sd['20160916'] = daytype.noTradingDay
        sd['20161010'] = daytype.noTradingDay
        sd['20161226'] = daytype.noTradingDay
        sd['20161227'] = daytype.noTradingDay

        for k in sd.keys():
            self.sdHandler[sd[k]](instru, datetime.strptime(k,'%Y%m%d'),\
                    sessionStart = morningSessionStart.get(k),\
                    sessionEnd = morningSessionEnd.get(k)) 
        
    def runFVSA(self):
        instru = 'FVSA Index'
        timezone = self.instruTable.getInstrumentTimezone(instru)
        
        self.setRegularDay(instru, timezone, 2013, 2016, '08:50:00', '22:00:00')
        sd = dict()
        
        sd['20130101'] = daytype.noTradingDay
        sd['20130329'] = daytype.noTradingDay 
        sd['20130401'] = daytype.noTradingDay
        sd['20130501'] = daytype.noTradingDay 
        sd['20131225'] = daytype.noTradingDay
        sd['20131226'] = daytype.noTradingDay 
        sd['20140101'] = daytype.noTradingDay
        sd['20140418'] = daytype.noTradingDay 
        sd['20140421'] = daytype.noTradingDay
        sd['20140501'] = daytype.noTradingDay 
        sd['20141225'] = daytype.noTradingDay
        sd['20141226'] = daytype.noTradingDay 
        sd['20150101'] = daytype.noTradingDay
        sd['20150403'] = daytype.noTradingDay 
        sd['20150406'] = daytype.noTradingDay
        sd['20150501'] = daytype.noTradingDay 
        sd['20151225'] = daytype.noTradingDay
        sd['20151226'] = daytype.noTradingDay 
        sd['20160101'] = daytype.noTradingDay
        sd['20160325'] = daytype.noTradingDay 
        sd['20160328'] = daytype.noTradingDay
        sd['20160501'] = daytype.noTradingDay 
        sd['20161225'] = daytype.noTradingDay
        sd['20161226'] = daytype.noTradingDay 
        sd['20161231'] = daytype.noTradingDay 

        for k in sd.keys():
            self.sdHandler[sd[k]](instru, datetime.strptime(k,'%Y%m%d'))

    def runUX1(self):
        instru = 'UX1 Index'
        timezone = self.instruTable.getInstrumentTimezone(instru)
        
        self.setRegularDay(instru, timezone, 2013, 2016, '02:00:00', '15:15:00')
        sd = dict()
        
        sd['20130101'] = daytype.noTradingDay
        sd['20130121'] = daytype.noTradingDay 
        sd['20130218'] = daytype.noTradingDay
        sd['20130329'] = daytype.noTradingDay 
        sd['20130527'] = daytype.noTradingDay
        sd['20130604'] = daytype.noTradingDay 
        sd['20130902'] = daytype.noTradingDay 
        sd['20131128'] = daytype.noTradingDay 
        sd['20131225'] = daytype.noTradingDay 

        sd['20140101'] = daytype.noTradingDay
        sd['20140120'] = daytype.noTradingDay 
        sd['20140217'] = daytype.noTradingDay
        sd['20140418'] = daytype.noTradingDay 
        sd['20140526'] = daytype.noTradingDay
        sd['20140604'] = daytype.noTradingDay 
        sd['20140901'] = daytype.noTradingDay 
        sd['20141127'] = daytype.noTradingDay 
        sd['20141225'] = daytype.noTradingDay 

        sd['20150101'] = daytype.noTradingDay
        sd['20150119'] = daytype.noTradingDay 
        sd['20150216'] = daytype.noTradingDay
        sd['20150403'] = daytype.noTradingDay 
        sd['20150525'] = daytype.noTradingDay
        sd['20150603'] = daytype.noTradingDay 
        sd['20150907'] = daytype.noTradingDay 
        sd['20151126'] = daytype.noTradingDay 
        sd['20151225'] = daytype.noTradingDay 

        sd['20160101'] = daytype.noTradingDay
        sd['20160118'] = daytype.noTradingDay 
        sd['20160215'] = daytype.noTradingDay
        sd['20160325'] = daytype.noTradingDay 
        sd['20160530'] = daytype.noTradingDay
        sd['20160604'] = daytype.noTradingDay 
        sd['20160905'] = daytype.noTradingDay 
        sd['20161010'] = daytype.noTradingDay 
        sd['20161111'] = daytype.noTradingDay 
        sd['20161124'] = daytype.noTradingDay 
        sd['20161226'] = daytype.noTradingDay 
        for k in sd.keys():
            self.sdHandler[sd[k]](instru, datetime.strptime(k,'%Y%m%d'))

