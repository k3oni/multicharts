#!/usr/bin/python
###############################################################################
## a wrapper for zmq message

from othersrc import message_pb2
import datetime, abc
from msg import msg
import re

class zmqMsg(msg):
    
    def __init__(self, msg, msgtype):
        self.msg = msg
        self.contract = msg.contractID
        elems = re.split(r'[._]+', self.contract)
        self.instrument =  elems[0]
        self.msgtype = msgtype

    def getSeqNum(self):
        return self.seqnum

    def getContract(self):
        return self.contract

    def getInstrument(self):
        return self.instrument

    def display(self):
        print('%s, %s, %s, %s', 
               (self.getSeqNum(),\
                self.getTS(), 
                self.getCID(), 
                self.getInstrument()))

