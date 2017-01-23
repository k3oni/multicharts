#!/usr/bin/python
################################################################################
from tools.timezonemap import datetimeTool
import Queue
from oms.matchengine import matchEngine
from oms.simoms import simoms
from msg.msg import msgType

class backtestMode:

    def __init__(self, strategy):
        self.strategy = strategy
        self.msgqueue = Queue.Queue()
        self.me = matchEngine()
        self.oms = simoms(strategy, self.me) 

    def run(self):
        config = self.strategy.getConfig()
        datasrcs = config.getDataSources()
        msgstream = self.strategy.barCtrl.getMessageStream(datasrcs, \
                        config.getStartDate(), config.getEndDate())

         # which trading hour should be used?        
        tradhour = self.strategy.dbs.getTradingHour(config.getTradeInstruments()[0],\
                        config.getStartDate(), config.getEndDate())
        #try:
        for session in tradhour:
            mux = msgstream[session]
            msgs = mux.getMsg()
            self.strategy.onSessionInit(session[0], session[1])
            msg = msgs.next()
            self.msgqueue.put(msg)
            while not self.msgqueue.empty():
                # dispatch 
                m = self.msgqueue.get()

                # order message
                if m.msgtype == msgType.barmsg or m.msgtype == msgType.tickmsg:
                    replylist = self.me.matchOrder(m)
                    if replylist <> None:
                        for reply in replylist:
                            self.msgqueue.put(reply)
                
                self.strategy.onMsg(m)

                # data message
                try:                
                    m = msgs.next()
                    if m <> None:
                        self.msgqueue.put(m)
                except StopIteration:
                    pass

            self.strategy.onSessionClear(session[0], session[1])

        #except Exception as inst:
        #    err('Exit strategy %s' % self.config.getStrategyName())
        #    infor(inst)

    def getOMS(self):
        return self.oms
