#!/usr/bin/python
###############################################################################
## a wrapper for zmq message

from othersrc import message_pb2
from zmqmsg import zmqMsg
from tools.timezonemap import datetimeTool
from msg import msgType
from tools.common import infor
from pytz import timezone
import datetime

class zmqTickMsg(zmqMsg):
    
    def __init__(self, msg):
        zmqMsg.__init__(self, msg, msgType.tickmsg)
        self.dt = datetimeTool.epoch_to_dt(msg.ts)
        self.type = message_pb2.MessageBase.TickType.Name(self.msg.tickType)     
        self.content = self.msg.msgStr
        self.seqnum = msg.seqnum
        self.mb = message_pb2.MessageBase()
        
        # tick msg to zmq message
        self.tickTypeMap = dict()
        TickType = message_pb2.MessageBase

        self.tickTypeMap['UNKNOWN_TICKTYPE']    = TickType.UNKNOWN_TICKTYPE
        self.tickTypeMap['BIDPX']               = TickType.BIDPX
        self.tickTypeMap['ASKPX']               = TickType.ASKPX
        self.tickTypeMap['BIDSZ']               = TickType.BIDSZ
        self.tickTypeMap['ASKSZ']               = TickType.ASKSZ
        self.tickTypeMap['LSTPX']               = TickType.LSTPX
        self.tickTypeMap['LSTSZ']               = TickType.LSTSZ
        self.tickTypeMap['LSTTS']               = TickType.LSTTS
        self.tickTypeMap['VOLUME']              = TickType.VOLUME
        self.tickTypeMap['OPEN']                = TickType.OPEN
        self.tickTypeMap['HIGH']                = TickType.HIGH
        self.tickTypeMap['LOW']                 = TickType.LOW
        self.tickTypeMap['CLOSE']               = TickType.CLOSE
        self.tickTypeMap['RT_VOLUME']           = TickType.RT_VOLUME
    

    def getTS(self):
        return self.dt

    def getTSStr(self):
        return self.dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    def getType(self):
        return self.type

    def isTradePrice(self):
        return self.type == 'LSTPX'

    def getContent(self):
        return self.content

    def display(self):
        infor('%s, %s, %s, %s, %s' % 
               (self.getTSStr(),
                self.getContract(), 
                self.getType(), 
                self.getContent(), 
                self.getInstrument()))

    def toZmqBuffer(self):
        mb = self.mb
        mb.type = message_pb2.MessageBase.TICKMSG
        tm = mb.tickMsg
        tm.seqnum = self.seqnum
        tm.tickType = self.tickTypeMap[self.type]
        tm.ts = datetimeTool.dt_to_epoch(self.dt)
        tm.contractID = self.contract 
        tm.msgStr = self.content
        return mb.SerializeToString()


