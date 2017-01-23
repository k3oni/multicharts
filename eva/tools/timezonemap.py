#!/usr/bin/python
################################################################################
from datetime import datetime, time, timedelta
from dateutil import tz
from tools.common import infor
import django.utils.timezone as dj
import pytz
import pprint
import itertools

class timeZoneMap:

    tzm = dict()

    def __init__(self):
        pass

    @staticmethod
    def getDatetimeWithTimezone(dt, timezone):
        tzinfor = pytz.timezone(timezone)
        return tzinfor.localize(dt)
    
    @staticmethod
    def datestr2Date(dtstr, timezone, format = '%Y-%m-%d'):
        dt = datetime.strptime(dtstr, format)
        return timeZoneMap.getDatetimeWithTimezone(dt, timezone)

    @staticmethod
    def getTimezoneFromDatetime(dt):
        return dt.time().tzinfo    

    @staticmethod
    def getDeltaFromTime(timestring): # 'hh:mm:ss'
        t = datetime.strptime(timestring, '%H:%M:%S')
        return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

class datetimeTool:
    def __init__(self):
        pass

    @staticmethod
    def dt_to_epoch(dt, scale=1000):
        base = datetime(1970,1,1)
        return int((dt.replace(tzinfo=None)-base).total_seconds()*scale)
    
    @staticmethod
    def bindDateSession(dates, sessions):
        def setSession(d):
            daysession = []
            for s in sessions:
                beg = d.replace(hour=s[0].hour, minute=s[0].minute, second=s[0].second, microsecond=0)
                end = d.replace(hour=s[1].hour, minute=s[1].minute, second=s[1].second, microsecond=0)
                daysession.append((beg, end))
            return daysession
        sessions = map(setSession, dates)
        sessionlist = list(itertools.chain(*sessions))
        return sessionlist

    @staticmethod
    def epoch_to_dt(epoch, scale=1000, timezone='Asia/Hong_Kong'):
        dt = datetime.utcfromtimestamp(epoch/scale)
        if timezone == 'UTC':
            return dt
        else:
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz(timezone)
            return dt.replace(tzinfo=from_zone).astimezone(to_zone)

    @staticmethod
    def removeTimezone(dt):
        return dt.replace(tzinfo=None)

    @staticmethod
    def generateTimeSlot(period, begin, end): 
        # period is timedelta, begin and end: datetime
        timeslot = []
        barEnd = begin
        while True:
            barEnd = min(barEnd + period, end)
            timeslot.append(barEnd)
            if barEnd == end:
                break
        return timeslot
    @staticmethod
    def checkDatetimeAware(dt):
        check = 'aware' if dj.is_aware(dt) else 'unware'
        infor('dt is %s' % check, color = 'red')
        
if __name__ == "__main__":
    timeZoneMap.listUTCOffset()
