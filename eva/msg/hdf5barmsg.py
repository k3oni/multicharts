###############################################################################
## messge generated by hdf5 file

import datetime
from msg import msg, msgType
from tools.timezonemap import timeZoneMap as tzm
from tools.common import infor

class hdf5BarMsg(msg):

    # Assume all data collected uses Hong Kong time zone
    def __init__(self, **kwargs):
        msg.__init__(self, msgType.barmsg)
        if 'record' in kwargs.keys() and \
            'instrument' in kwargs.keys() and \
            'contract' in kwargs.keys() and \
            'barlen' in kwargs.keys():
            self.instrument = kwargs['instrument']
            self.contract = kwargs['contract']
            self.barlen = kwargs['barlen']
            record = kwargs['record']
            self.dt = datetime.datetime.fromtimestamp(record[0])
            self.start = tzm.getDatetimeWithTimezone(self.dt, timezone)
            self.open = record[3]
            self.high = record[4]
            self.low = record[5]
            self.close = record[6]
            self.vol = record[9]
   
    @staticmethod 
    def createMsg(instr, contract, start, end, barlen, \
                    open, high, low, close, vol):
        msg = hdf5BarMsg()
        msg.instrument = instr
        msg.contract = contract
        msg.start = start
        msg.end = end
        msg.barlen = barlen
        msg.open = open
        msg.high = high
        msg.low = low
        msg.close = close
        msg.vol = vol 
        return msg

    def getContent(self):
        c = '%s: %s: open %f, high %f, low %f, close %f, volumn %f' %\
                        (self.start, self.contract, self.open,
                         self.high, self.low, self.close, self.vol)
        self.content = c
        return self.content

    def getContract(self):
        return self.contract

    def getBar(self):
        return (self.start, self.open, self.high, self.low, self.close) 

    def display(self):
        infor(self.getContent())
        
    def getBarStartTime(self):
        return self.start

    def getInstrument(self):
        return self.instrument
