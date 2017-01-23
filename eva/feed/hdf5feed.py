#!/usr/bin/python
###############################################################################
## filefeed provide data from hdr5 file
from __future__ import print_function
import sys, zmq, abc
from othersrc import message_pb2
from feed import feed, dataType
from msg.hdf5barmsg import hdf5BarMsg
from tools.common import infor, err

try:
    import h5py
except ImportError:
    print('Please install h5py')
    exit() 

class hdf5Feed(feed):

    def __init__(self, datatype, filename, instru, contract, barlen = None):
        feed.__init__(self, datatype)
        self.setDataSrc(filename)
        self.instru = instru;
        self.contract = contract;
        self.barlen = barlen

    def setDataSrc(self, filename):
        self.f = h5py.File(filename, 'r')
        self.trd = self.f['TRADES']
        self.counter = 0

    def getNextMsg(self):
        row = self.trd[self.counter]
        self.counter = self.counter + 1
        return hdf5BarMsg(instrument = self.instru, 
                            contract = self.contract,
                            barlen = self.barlen, 
                            record = row)

    def isEnd(self):
        return self.counter >= len(self.trd)

    def reset(self):
        self.counter = 0

    def __exit__(self):
        self.f.close()        
