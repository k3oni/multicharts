#!/usr/bin/python
###############################################################################
## urlfeed provide data from url

from __future__ import print_function
import sys, zmq, abc
from othersrc import message_pb2
from feed import feed, dataType
from msg.zmqbarmsg import zmqBarMsg
from msg.zmqtickmsg import zmqTickMsg
from tools.common import infor
from bar.bargen import barGen

class urlFeed(feed):

    def __init__(self, datatype, url, timezone):
        feed.__init__(self, datatype, timezone)
        self.setDataSrc(url)
        self.timezone = timezone

    # set data source
    def setDataSrc(self, serverurl):
    #   Configure zmq server connection options
        self.serverurl  = serverurl
        self.context    = zmq.Context()
        self.socket     = self.context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, ''.decode('ascii'))
        self.socket.connect("tcp://%s" % self.serverurl)
        self.msgbase = message_pb2.MessageBase()

    # if we want to generate live bar    
    def setBarGenerator(self, barlen, sessionBegin, sessionEnd):
        self.bargen = barGen(self)
        self.bargen.setTimeSlot(barlen, sessionBegin, sessionEnd) 

    def getRawMsg(self):
        self.msgbase.ParseFromString(self.socket.recv())

        if self.dataType == dataType.liveTickData:
            msg = zmqTickMsg(self.msgbase.tickMsg)
            self.lastMsgTS = msg.dt
            return msg
        elif self.dataType == dataType.liveBarData:
            msg = zmqBarMsg(self.msgbase.bar)
            self.lastMsgTS = msg.dt
            return msg
        else:
            err("Unsopport message format", color='red')

    def postProcess(self, msg):
        if self.dataType == dataType.liveBarData:
            barmsg = self.bargen.genBar(msg)  
            return barmsg
        else:
            return msg

    def getNextZMQMsg(self):
        return self.socket.recv()
    
    def isEnd(self):
        return False

