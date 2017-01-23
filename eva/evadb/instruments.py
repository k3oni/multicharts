#!/usr/bin/python
################################################################################
from tools.common import infor, err
from evadb.dbtool import dbtool
from dbentity import dbEntity
from enum import Enum

class instrumentType(Enum):
    future = 1
    equity = 2
    forex = 3

class instruments(dbEntity):

    def __init__(self, dbname, dbuser, dbpasswd, tablename, exchTable):
        dbEntity.__init__(self, dbname, dbuser, dbpasswd, tablename)
        self.exchange = exchTable

    def createTable(self):
        sql = 'create table {tn} (\
                        id int primary key,\
                        bbgname varchar,\
                        ibname varchar,\
                        exchid int,\
                        typeid int,\
                        filepath varchar);'.format(tn=self.tablename)

        self.dbtool.execute(sql)

    def fill(self):        
        instruPrefix = 'insert into {tn} values ('.format(tn=self.tablename)
        instruSuffix = ');'
        
        instru = dict()
        instru[1] = ['HI1 Index','HSI', 1, instrumentType.future.value, \
                        '/home/share/h5/HI1_Index.h5']
        instru[2] = ['HC1 Index', 'HHI.HK', 1, instrumentType.future.value,\
                         '/home/share/h5/HC1_Index.h5']
        instru[3] = ['FVSA Index','', 2, instrumentType.future.value, '']
        instru[4] = ['UX1 Index','', 3, instrumentType.future.value,'']
        
        for k in instru.keys():
            c = "%d, '%s', '%s', %d, %d, '%s'" % (k, instru[k][0], \
                    instru[k][1], instru[k][2], instru[k][3], instru[k][4])
            sql = instruPrefix + c + instruSuffix
            self.dbtool.execute(sql)
            
            check = "select count(*) from %s where bbgname='%s' and ibname='%s'\
                        and exchid=%d and typeid=%d and filepath='%s';"\
                        % (self.tablename, instru[k][0], instru[k][1], instru[k][2],\
                            instru[k][3], instru[k][4])
            self.dbtool.checkInserted(check, c)

    def getInstrumentId(self, bbgname):
        sql = "select id from {tn} where bbgname='{bbg}';".format(tn=self.tablename, bbg=bbgname)
        id = self.dbtool.fetch(sql)
        if not id:
            err('Database could not find instrument: %s' % bbgname)
            return None

        return id[0][0]

    def getInstrumentTimezone(self, bbgname):
        sql = "select timezone from {exch} join {instru} on {exch}.id = {instru}.exchid\
                 where bbgname='{bbg}';".format(exch=self.exchange.tablename, \
                    instru=self.tablename, bbg=bbgname)
        tz = self.dbtool.fetch(sql)
        if not tz:
            err('Database could not find timezone for instrument: %s' % bbgname)
            return None

        return tz[0][0]

    def getIBNameFromBBGName(self, bbgname):
        sql = "select ibname from instruments where bbgname='{bbg}';".format(bbg=bbgname)
        ibname = self.dbtool.fetch(sql)
        if not ibname:
            infor("Cannot find ib name for bloomberg name %s" % (bbgname))
            return None
        else:
            return ibname[0][0]

    def getBBGNameFromIBName(self, ibname):
        sql = "select bbgname from instruments where ibname='{ibname}';".format(ibname=ibname)
        name = self.dbtool.fetch(sql)
        if not name:
            infor("Cannot find bloomberg name for ib name %s" % (ibname))
            return None
        else:
            return name[0][0]

    def getAllInstruments(self):
        sql = "select bbgname from {tn};".format(tn=self.tablename)
        instrus = self.dbtool.fetch(sql)
        if not instrus:
            infor('Database has no instruments')
            return None
        names = map(lambda x: x[0], instrus)
        return names

    def getFilePath(self, bbgname):
        sql = "select filepath from {tn} where bbgname='{bbgname}';"\
                .format(tn=self.tablename, bbgname=bbgname)
        fp = self.dbtool.fetch(sql)
        if not fp:
            infor("No file path found for {name}.".format(name=bbgname))
        else:
            return fp[0][0]

if __name__ == "__main__":
    it = instruments('delvin', 'delvin', 'delvin123', 'instruments', 'exchange')
    it.createTable()
    it.fill()

     
