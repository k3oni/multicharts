#/usr/bin/python
################################################################################
# rollover class provides all kinds of roll methods
from tools.common import infor, err
from evadb.dbtool import dbtool
from tools.timezonemap import timeZoneMap

class rollover():

    def __init__(self, instrument, calenTable):
        self.calen = calenTable
        self.instr = instrument

    def getRolloverMethod(self, method):
        return getattr(self, method)

    def beforeExpireOneDay(self, **kwargs):
        if 'contracts' not in kwargs.keys():
            infor('No start date of contracts')
            return None, None
        if 'periods' not in kwargs.keys():
            infor('No expire date of contracts')
            return None, None

        contracts = kwargs['contracts']
        periods = kwargs['periods']
        
        if len(contracts) == 0 or len(periods) == 0:
            return None, None

        pair = zip(contracts, periods)
        def cmp(p1, p2):
            return p1[1][1] < p2[1][1]

        pairOrdered = sorted(pair, cmp)
        nextStart = pairOrdered[0][1][1]
        
        activeContract = []
        activeDates = []

        for p in pairOrdered[1:]:
            nextExpire = self.calen.getPreviousNTradingDate(self.instr, p[1][1], 1)
            print "start %s expire %s" % (nextStart, nextExpire)
            if nextExpire is not None:
                td = self.calen.getTradingDate(self.instr, nextStart, nextExpire)
                for d in td:
                    activeContract.append((d, p[0]))
            nextStart = p[1][1]
                        
        
        # remove repeated item
        activeContract = list(set(activeContract))
        activeContract = sorted(activeContract, key=lambda ac: ac[0])
        return activeContract 
