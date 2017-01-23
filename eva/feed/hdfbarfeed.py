#!/usr/bin/python
################################################################################
from tools.common import infor, err
import pandas as pd
from feed import feed
from tools.timezonemap import datetimeTool as dtt, timeZoneMap as tzm 
from msg.hdf5barmsg import hdf5BarMsg
from bar.bar import barLength

class hdfBarFeed(feed):
    # hdfBarFeed only handle per contract information
    # barcontroller will handle per instrument data 

    def __init__(self, datatype, filename, timezone, instru, contract, expireYear, \
                    expireMonth, barlen):
        feed.__init__(self, datatype, timezone)
        self.filename = filename
        self.instru = instru
        self.expireYear = expireYear
        self.expireMonth = expireMonth
        self.contract = contract
        self.barlen = barlen
        self.df = []
        self.counter = 0

    def setDataSrc(self, since, till, tradhour, fields=None):
        self.df = pd.DataFrame()
        tablename = "/M{year}{month}/{barsize}".format(year=self.expireYear, \
                        month=self.expireMonth, barsize=self.barlen)
   
        for session in tradhour:
            condition = 'timestamp>={start} and timestamp<={end} '.\
                    format(start=dtt.dt_to_epoch(session[0], 1), \
                           end=dtt.dt_to_epoch(session[1], 1))  
            if fields is None:                
                df = pd.read_hdf(self.filename, tablename, where=[condition])
            else:
                df = pd.read_hdf(self.filename, tablename, where=[condition], \
                                    columns=['timestamp'] + fields)
            if 'timestamp' in df.columns: 
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

            self.df = self.df.append(df)

        return self.df

    def getBlockData(self, since, till, tradhour, fields=None):
        return self.setDataSrc(since, till, tradhour, fields) 

    def getDailyBar(self, since, till, fields=None):
        tablename = "/M{year}{month}/{barsize}/RTH".format(year=self.expireYear, \
                        month=self.expireMonth, barsize=self.barlen)

        condition = 'timestamp>={start} and timestamp<={end} '.\
                format(start=dtt.dt_to_epoch(since, 1),  end=dtt.dt_to_epoch(till, 1))  
        if fields is None:                
            df = pd.read_hdf(self.filename, tablename, where=[condition])
        else:
            df = pd.read_hdf(self.filename, tablename, where=[condition], \
                                columns=['timestamp'] + fields)

        if 'timestamp' in df.columns: 
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        return df

    def getRawMsg(self):
        row = self.df.iloc[self.counter,:]
        self.counter = self.counter + 1
        
        # get instrument timezone
        # convert dt with timezone 
        return hdf5BarMsg.createMsg(self.instru, self.contract, \
                            self.timezone.localize(row['timestamp']),\
                            None, self.barlen, row['open'], row['high'], row['low'], \
                            row['close'], row['volume'])
         
    def postProcess(self, msg):
        return msg

    #def getNextMsg(self):
    #    row = self.df.iloc[self.counter,:]
    #    self.counter = self.counter + 1
    #    
    #    # get instrument timezone
    #    # convert dt with timezone 
    #    return hdf5BarMsg.createMsg(self.instru, self.contract, \
    #                        tzm.getDatetimeWithTimezone(row['timestamp'], self.timezone),\
    #                        None, self.barlen, row['open'], row['high'], row['low'], \
    #                        row['close'], row['volume'])

    def isEnd(self):
        return self.counter >= self.df.shape[0]

    def reset(self):
        self.counter = 0
        
