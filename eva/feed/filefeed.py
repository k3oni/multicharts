#!/usr/bin/python
###############################################################################
## filefeed provide data from file

from __future__ import print_function
import sys, zmq, abc
from othersrc import message_pb2
from feed import feed

class fileFeed(feed):

    def __init__(self, datatype, filename, timezone):
        feed.__init__(self, datatype, timezone)
        self.setDataSrc(filename)

    def setDataSrc(self, filename):
        pass

    def getNextMsg(self, msg):
        pass

    def isEnd(self):
        pass
