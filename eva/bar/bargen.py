#!/usr/bin/python
################################################################################
# generate bars
from bar import barLength
from datetime import datetime, timedelta
from tools.common import infor
from threading import Timer
from othersrc import message_pb2
import threading
from tools.timezonemap import datetimeTool
from msg.zmqbarmsg import zmqBarMsg

class barGen:

    def __init__(self, feed):
        self.buf = []
        self.feed = feed
        # mutex
        self.triggerBarGen = False

    def now(self):
        return self.feed.now()
        
    def setTimeSlot(self, barlen, sessionBegin, sessionEnd):
        self.timeslot = datetimeTool.generateTimeSlot(barlen.toTimedelta(), \
                            sessionBegin, sessionEnd)
        for ts in self.timeslot:
            delay = (ts - self.now()).total_seconds()
            if delay >= 0:
                threading.Timer(delay, self.triggerBar, [ts, barlen, sessionEnd]).start()
                break

    # use 5 second live bar feed for buffering 

    def triggerBar(self, ts, barlen, sessionEnd):
        self.triggerBarGen = True
        self.ts = ts
        nextts = ts + barlen.toTimedelta()
        if nextts <= sessionEnd:
            delay = (nextts - self.now()).total_seconds()
            threading.Timer(delay, self.triggerBar, [nextts, barlen, sessionEnd]).start()
            
    def gen(self):
        if len(self.buf) == 0:
            infor("Warning: cannot generate bar less than 5 seconds," + \
                  " since bar generator use 5 second bar provided by zmq", color='red')
            return None
        
        #for m in self.buf:
        #    infor('Bar generator receives the following msg:', color='green')
        #    m.display()

        sortedbuf = sorted(self.buf, key=lambda msg: msg.dt)

        bar = zmqBarMsg()
        bar.copy(sortedbuf[-1])
        bar.dt = self.ts

        # no idea what they are and how to compute
        bar.nbDec = 0
        bar.barcnt = 0
        bar.wap = 0
        bar.gap = 0
        
        # open high low close volume
        bar.open = sortedbuf[0].open
        bar.close = sortedbuf[-1].close
        highmsg = max(sortedbuf, key=lambda x: x.high)
        bar.high = highmsg.high
        lowmsg = min(sortedbuf, key=lambda x: x.low)
        bar.low = lowmsg.low
        bar.volume = sum(m.volume for m in sortedbuf)
        
        # clear buff
        self.buf = []
        #infor('Bar generated: ', color='green')
        #bar.display()
        return bar

    def genBar(self, msg):
        self.buf.append(msg)
        if self.triggerBarGen:
            self.triggerBarGen = False
            barmsg = self.gen()
            return barmsg
        return None
                        
        
         
