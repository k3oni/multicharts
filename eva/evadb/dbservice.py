#!/usr/bin/python
################################################################################

import dbtablename as dbn
from exchange import exchange
from instruments import instruments
from evacalendar import evaCalendar
from contract import contract
from activecontract import activeContract 
from tools.common import infor, err
from pprint import pprint
import zmq, sys

class dbservice:

    def __init__(self, dbname, username, passwd, ip, port):
        self.exch = exchange(dbname, username, passwd, dbn.exchangeTable)
        self.instr = instruments(dbname, username, passwd, \
                                    dbn.instrumentsTable, self.exch)
        self.calen = evaCalendar(dbname, username, passwd, \
                                    dbn.calendarTable, self.instr)
        self.contr = contract(dbname, username, passwd, \
                                    dbn.contractTable, self.instr)
        self.ac    = activeContract(dbname, username, passwd, \
                                    dbn.activecontractTable, self.instr)
        self.ctr   = contract(dbname, username, passwd, dbn.contractTable, self.instr)
        self.ip    = ip
        self.port  = port

    def getActiveContract(self, instruname, date):
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        sql = "select ctr.bbgname from \
                {activecontractTable} as ac \
                join {instrumentTable} as inst \
                on ac.instrid=inst.id \
                join {contractTable} as ctr\
                on ac.contractid = ctr.id \
                where ac.datetime='{dt}' and inst.bbgname='{instr}';".format(\
                contractTable = self.contr.tablename,
                activecontractTable = self.ac.tablename,
                instrumentTable = self.instr.tablename,
                dt = date,
                instr = instruname
                )
        name = self.ac.dbtool.fetch(sql)[0][0]
        if name is None:
            infor('Cannot find active contract name for {instr} on {dt}'\
                    .format(instr=instrument, dt=date))
        return name

    def getActiveContractGroup(self, instrument, start, end):
        sql = "select min(ac.datetime), max(ac.datetime), ctr.bbgname, ctr.expire \
                from {ac} as ac join {instr} as instr on ac.instrid = instr.id \
                join contract as ctr on ac.contractid = ctr.id\
                where instr.bbgname='{name}' and ac.datetime between '{start}' \
                and '{end}' group by ctr.bbgname, ctr.expire order by min(ac.datetime);".format(\
                ac = self.ac.tablename, instr = self.instr.tablename, name=instrument,\
                start = start, end = end)

        date_contract_list = self.ac.dbtool.fetch(sql)
        if len(date_contract_list) == 0 or date_contract_list[0][0] is None:
            infor('Cannot find active contract group for {instr} betweeen {start} and {end}'.format(\
                    instr=instrument, start=start, end=end))
        return date_contract_list
    
    def getExpireDate(self, contract):
        sql = "select expire from {ctr} as ctr where ctr.bbgname='{contr}';".\
                format(ctr=self.ctr.tablename, contr=contract)

        date = self.ac.dbtool.fetch(sql)

        if date[0][0] is None:
            infor('Cannot find expire date for contract %s' % contract)
        return date[0][0]

    def getPreviousOrAfterTradingDay(self, instrument, date, numberOfDays):
        if numberOfDays == 0:
            return (date)

        if numberOfDays > 0:
            sql = "select distinct datetime from activecontract ac \
                    join instruments instr \
                    on ac.instrid = instr.id \
                    where instr.bbgname = '{instrument}' \
                    and datetime > '{date}' \
                    order by datetime limit {top}".format( \
                    instrument = instrument, \
                    date = date, \
                    top = numberOfDays \
                    )
            dates = self.calen.dbtool.fetch(sql)
            if dates is None:
                infor("Cannot find trading days before or after {date}".format(\
                        date = date))
                return None
            return dates

        if numberOfDays < 0:
            sql = "select distinct datetime from activecontract ac \
                    join instruments instr \
                    on ac.instrid = instr.id \
                    where instr.bbgname = '{instrument}' \
                    and datetime < '{date}' \
                    order by datetime desc limit {top}".format( \
                    instrument = instrument, \
                    date = date, \
                    top = -numberOfDays \
                    )
            dates = self.calen.dbtool.fetch(sql)
            if dates is None:
                infor("Cannot find trading days before or after {date}".format(\
                        date = date))
                return None
            return list(reversed(dates))

    def getFirstTradingDayOfMonth(self, instrument, year, month):
        dt = year + month + "01";
        sql = "select datetime from calend join instruments as instr \
                on calend.instrid = instr.id \
                where instr.bbgname = '{instr}' \
                and calend.instrid = instr.id \
                and datetime >= '{date}' \
                and istradingday = true order by datetime limit 1;".format(\
                    instr = instrument,
                    date = dt
                )
        dates = self.calen.dbtool.fetch(sql)
        if dates is None:
            infor("Cannot find the first trading day of {year}, {month}".format(\
                    year = year, month = month))
            return None

        return dates[0]

    def getTradingHour(self, instruname, start, till):
        return self.calen.getTradingHour(instruname, start, till)

    def getTradingDate(self, instruname, start, till):
        return self.calen.getTradingDate(instruname, start, till)

    def getTradingDatePerContract(self, contract, since, till):
        sql = "select distinct calen.datetime from {contract} as ctr \
                join {calend} as calen on ctr.instrid=calen.instrid \
                where ctr.bbgname='{name}' and calen.datetime>='{since}' \
                and calen.datetime<='{till}' and calen.datetime>=ctr.start\
                and calen.datetime<=ctr.expire and calen.istradingday=True \
                order by calen.datetime".format(contract=self.ctr.tablename,\
                calend=self.calen.tablename, name=contract, since=since,\
                till=till)
        dates = self.calen.dbtool.fetch(sql)
        if dates is None:
            infor("Cannot find trading dates for {contract}".format(contract=contract))
        return dates

    def getIBNameFromBBGName(self, bbgname):
        return self.instr.getIBNameFromBBGName(bbgname)

    def getBBGNameFromIBName(self, ibname):
        return self.instr.getBBGNameFromIBName(ibname)

    def getNonspaceNameFromBBGName(self, name):
        if name <> None:
            return name.replace(" ", "_")
        return None

    def getTimezone(self, bbgname):
        sql = "select ex.timezone from {ex} as ex join {instr} as instr\
                on ex.id=instr.exchid where instr.bbgname='{name}';".format(\
                ex=self.exch.tablename, instr=self.instr.tablename, name=bbgname)
        tz = self.calen.dbtool.fetch(sql)[0][0]
        if tz is None:
            infor('Cannot find timezone for %s' % bbgname)
        return tz

    def getInstrumentFilePath(self, bbgname):
        return self.instr.getFilePath(bbgname)
    
    def checkMsgValid(self, msg):
        elems = msg.split('()')
   
    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        src = "tcp://{ip}:{port}".format(ip=self.ip, port=self.port)
        socket.bind(src)
        infor('Listen to %s' % src)
        while True:
            msg = socket.recv()
            infor('Received Msg: %s' % msg)
            try:
                if '(' in msg and ')' in msg:
                    cmd, arg = msg.split('(')
                    if hasattr(self, cmd):
                            result = eval('self.{func}'.format(func=msg))
                            if result <> None:
                                socket.send(str(result))
                            else:
                                errmsg = 'None'
                                socket.send(errmsg)
                    else:
                        infor('Not found: %s' % msg)
                        notfound = 'Cannot find your requested function. Please contract Delvin.'
                        socket.send(notfound)
                else:
                    invalidmsg = 'Invalid function: %s' % msg
                    infor(invalidmsg)
                    socket.send(invalidmsg)
            except:
                unexpected = 'Unexpected error: %s' % sys.exc_info()[0]
                infor(unexpected)
                socket.send(unexpected)
                continue

if __name__ == "__main__":
    dbs = dbservice('delvin','delvin','delvin123','192.168.0.47','40966')
    dates = dbs.getTradingDatePerContract('HCZ5 Index', '20150101', '20161201')
    dbs.run()
