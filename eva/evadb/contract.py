#!/usr/bin/python
###############################################################################
import blpapi
from bbg.bbg import bbg
from tools.common import infor, err
from evadb.dbtool import dbtool
from dbentity import dbEntity
from datetime import datetime
import pytz
from tools.timezonemap import timeZoneMap

class contract(dbEntity):

    def __init__(self, dbname, username, dbpasswd, tablename, instruTable):
        dbEntity.__init__(self, dbname, username, dbpasswd, tablename)
        self.instruTable = instruTable

    def createTable(self):
        sql = 'create table {tn} (\
              id serial primary key,\
              update_ts timestamp with time zone,\
              instrid int,\
              bbgname varchar,\
              othername varchar,\
              start timestamp with time zone,\
              expire timestamp with time zone\
              );'.format(tn=self.tablename)
        self.dbtool.execute(sql)

    def insertContract(self, instrument, bbgname, othername,\
                         start, expire):

        underlyid = self.instruTable.getInstrumentId(instrument)
        sql = "insert into %s values(default, '%s', %d, '%s', \
                '%s', '%s', '%s');"\
                 % (self.tablename, datetime.today(), underlyid, bbgname, \
                     othername, start, expire)
        self.dbtool.execute(sql)

        check = "select count(*) from %s where instrid=%d and\
                bbgname='%s' and othername='%s' and start='%s' and expire='%s';"\
                % (self.tablename, underlyid, bbgname, othername, start, expire)
        self.dbtool.checkInserted(check, sql)        

    def deleteContractsForInstrument(self, instrument):
        underlyid = self.instruTable.getInstrumentId(instrument)
        sql = "delete from %s where underlying='%s';" % (self.tablename, underlyid)
        self.dbtool.execute(sql)

        check = "select count(*) from %s where underlying='%s';" % (self.tablename, underlyid)
        self.dbtool.checkDeleted(check, sql)

    def fillContract(self, instrument, acs, bbg):
        tz = self.instruTable.getInstrumentTimezone(instrument)
        contractname, contractInfor = bbg.requestContractsStartAndExpire(instrument, \
                                        tz, acs)
        # fill contract table
        for name, ci in zip(contractname, contractInfor):
            self.insertContract(instrument, name, '', ci[0], ci[1])        

    def getContractId(self, contractname):
        sql = "select id from {tn} where bbgname='{name}'".format(tn=self.tablename, \
               name=contractname)
        id = self.dbtool.fetch(sql)
        if len(id) > 0:
            return id[0][0]
        else:
            return None

if __name__ == "__main__":
    from engine.config import EPConfig
    conf = EPConfig()
    ac = activeContract(conf) 
    ac.insertContract('HC1 Index')

