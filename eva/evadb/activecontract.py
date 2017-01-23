#/usr/bin/python
################################################################################
from tools.common import infor, err
from evadb.dbtool import dbtool
from contract import contract
from datetime import datetime

class activeContract(contract):

    def __init__(self, dbname, username, dbpasswd, tablename, instruTable):
        contract.__init__(self, dbname, username, dbpasswd, tablename, instruTable)

    def createTable(self):
        sql = 'create table activecontract (\
               instrid int,\
               update_ts timestamp with time zone,\
               datetime timestamp with time zone,\
               contractId int,\
               constraint activekey primary key (instrid, datetime));'
        self.dbtool.execute(sql)

    def getActiveContractFromBBG(self, instrument, bbg):
        return bbg.getFutureChain(instrument, True)

    def fillActiveContract(self, instrument, instruTable, contractTable, \
                            rollover, **kwargs):
        # fill active contract table
        instruId = instruTable.getInstrumentId(instrument)
        update_ts = datetime.today()
        # acs is a list of (date, contract)
        acs = rollover.getRolloverMethod('beforeExpireOneDay')(**kwargs)

        for ac in acs:
            cid = contractTable.getContractId(ac[1])
            sql = "insert into {tn} values ({instId}, '{ts}', '{dt}', {cid});".format(\
                    tn=self.tablename, instId=instruId, ts=update_ts, dt=ac[0][0], cid=cid)
            print sql
            self.dbtool.execute(sql)
