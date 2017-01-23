#!/usr/bin/python
###############################################################################
## order book class shows up to date data such as ask price, asksize, bid price,
## bidsize and trade price

from feed.feedfactory import feedFactory, feedType
from feed.feed import dataType
from msg.zmqtickmsg import zmqTickMsg

class orderBook:
    askpxName = 'ASKPX'
    askszName = 'ASKSZ'
    bidpxName = 'BIDPX'
    bidszName = 'BIDSZ'
    trdpxName = 'LSTPX'
    trdszName = 'LSTSZ'

    
    def __init__(self, instr):
        self.datetime = ''
        self.askpx = 0
        self.asksz = 0
        self.trdpx = 0
        self.trdsz = 0
        self.bidpx = 0
        self.bidsz = 0
        self.andConstrain = []
        self.orConstrain = []
        self.valid = False        

        self.addAndConstrain(self.instrumentConstrain(instr))
        self.addOrConstrain(self.typeConstrain('ASKPX'))
        self.addOrConstrain(self.typeConstrain('ASKSZ'))
        self.addOrConstrain(self.typeConstrain('BIDPX'))
        self.addOrConstrain(self.typeConstrain('BIDSZ'))
        self.addOrConstrain(self.typeConstrain('LSTPX'))
        self.addOrConstrain(self.typeConstrain('LSTSZ'))
        
        self.dispatch = { 
            orderBook.askpxName : self._updateAskpx,
            orderBook.askszName : self._updateAsksz,
            orderBook.bidpxName : self._updateBidpx,
            orderBook.bidszName : self._updateBidsz,
            orderBook.trdpxName : self._updateTrdpx,
            orderBook.trdszName : self._updateTrdsz
        }

    ###########################################################################
    '''Interface''' 
    def addAndConstrain(self, constrain):
        '''and constrain is a function on (orderbook, zmqMsg) and must be
            satisfied by all messages
        '''
        self.andConstrain.append(constrain)

    def addOrConstrain(self, constrain):
        self.orConstrain.append(constrain)

    def instrumentConstrain(self, instr): 
        def constrain(ob, msg):
            return not msg.getInstrument() == instr
        return constrain

    def typeConstrain(self, type):
        def constrain(ob, msg):
            return msg.getType() == type
        return constrain
    
    def update(self, msg):
        for c in self.andConstrain:
            if c(self, msg):
                return 0

        passed = False 
        for c in self.orConstrain:
            if c(self, msg):
                passed = True
                break 

        if passed:
            message = 'Inside message: %s, %s, %s, %s, %s, %s' % (msg.getSeqNum(),\
                msg.getTS(), msg.getCID(), msg.getType(), msg.getContent(), 
                msg.getInstrument())
            #print message
            self.dispatch[msg.getType()](msg)
            self.display()
    
    def display(self):
        print '%s : %s : bidpx %f bidsz %f trdpx %f trdsz %f askpx %f asksz %f' % \
                (self.datetime, ('valid ' if self.valid else 'invalid'), 
                 self.bidpx, self.bidsz, self.trdpx, self.trdsz, self.askpx, self.asksz)


    ###########################################################################
    '''Inside update'''
    def _updateAskpx(self, msg):
        self.datetime = msg.getTS()
        self.askpx = float(msg.getContent())
        if self.askpx > self.bidpx:
            self.valid = True

    def _updateAsksz(self, msg):
        self.datetime = msg.getTS() 
        self.asksz = float(msg.getContent())

    def _updateBidpx(self, msg):
        self.datetime = msg.getTS() 
        self.bidpx = float(msg.getContent())

    def _updateBidsz(self, msg):
        self.datetime = msg.getTS() 
        self.bidsz = float(msg.getContent())
        if self.askpx > self.bidpx:
            self.valid = True

    def _updateTrdpx(self, msg):
        self.datetime = msg.getTS() 
        self.trdpx = float(msg.getContent())

    def _updateTrdsz(self, msg):
        self.datetime = msg.getTS() 
        self.trdsz = float(msg.getContent())



#unit test

if __name__ == '__main__':
    serverurl = '192.168.0.20:20123'
    ff = feedFactory()
    tf = ff.createFeed(feedType.UrlFeed, serverurl, dataType.liveTickData)
    ob = orderBook('HHI')

    while (True):
        msg = zmqTickMsg(tf.getNextMsg())
        message = '%s, %s, %s, %s, %s, %s' % (msg.getSeqNum(),\
                msg.getTS(), msg.getCID(), msg.getType(), msg.getContent(), 
                msg.getInstrument())
        #print message
        ob.update(msg)
