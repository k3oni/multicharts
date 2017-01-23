#!/usr/bin/python
################################################################################
from tools.bbg2IB import toIBContract
from tools.common import infor
class constrainFactory:

    def __init__(self, dbservice):
        self.dbs = dbservice

    def createInstrumentConstrain(self, instr, date):
        contract = self.dbs.getActiveContract(instr, date)
        contractIB = toIBContract(contract)
        def isInstrument(zmqmsg):
            return zmqmsg.getContract() == contractIB
        return isInstrument


