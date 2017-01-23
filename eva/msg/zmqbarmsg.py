#!/usr/bin/python
###############################################################################
## a wrapper for zmq message

from othersrc import message_pb2
from zmqmsg import zmqMsg
import datetime
from msg import msgType
from tools.common import infor
from tools.timezonemap import datetimeTool as dtt

class zmqBarMsg(zmqMsg):
    
    def __init__(self, msg = None): #msg is message_pb2 message
        self.mb = message_pb2.MessageBase()
        if msg <> None:
            zmqMsg.__init__(self, msg, msgType.barmsg)
            self.dt = dtt.epoch_to_dt(msg.ts, 1)   
            self.type   = message_pb2.MessageBase.PxType.Name(msg.pxType)     
            self.seqnum = msg.seqnum
            self.nbDec  = msg.nbDec
            self.open   = msg.open
            self.high   = msg.high
            self.low    = msg.low
            self.close  = msg.close
            self.volume = msg.volume
            self.barcnt = msg.barcnt
            self.wap    = msg.wap
            self.gap    = msg.gap

    def copy(self, zbm):
        self.msg        = zbm.msg
        self.contract   = zbm.contract
        self.instrument = zbm.instrument
        self.msgtype    = zbm.msgtype
        self.dt         = zbm.dt 
        self.type       = zbm.type     
        self.seqnum     = zbm.seqnum
        self.nbDec      = zbm.nbDec
        self.open       = zbm.open
        self.high       = zbm.high
        self.low        = zbm.low
        self.close      = zbm.close
        self.volume     = zbm.volume
        self.barcnt     = zbm.barcnt
        self.wap        = zbm.wap
        self.gap        = zbm.gap

    def getSeqNum(self):
        return self.seqnum

    def getTS(self):
        return self.dt

    def getTSStr(self):
        return self.dt.strftime('%Y-%m-%d %H:%M:%S.%f')        

    def getType(self):
        return self.type 

    def getOpen(self):
        return self.open
    
    def getHigh(self):
        return self.high
    
    def getLow(self):
        return self.low
    
    def getClose(self):
        return self.close

    def getVolumn(self):
        return self.volume

    def getTOHLC(self):
        return (self.dt, self.open, self.high, self.low, self.close)

    def getBarStartTime(self):
        return self.dt

    def display(self):
        infor('%s, %s, %s, %s, %f, %f, %f, %f, %f' % (self.getSeqNum(),\
                self.getTSStr(),   self.getContract(), self.getType(), 
                self.getOpen(), self.getHigh(),
                self.getLow(),  self.getClose(), self.getVolumn()))

    def toZmqBuffer(self):
        mb = self.mb
        mb.type = message_pb2.MessageBase.BAR
        bar = mb.bar
        bar.pxType = self.msg.pxType
        bar.contractID = self.msg.contractID
        bar.ts     = dtt.dt_to_epoch(self.dt,1)
        bar.seqnum = self.seqnum
        bar.nbDec  = self.nbDec
        bar.open   = self.open
        bar.high   = self.high
        bar.low    = self.low
        bar.close  = self.close
        bar.volume = self.volume
        bar.barcnt = self.barcnt
        bar.wap    = self.wap
        bar.gap    = self.gap
        return mb.SerializeToString()   

