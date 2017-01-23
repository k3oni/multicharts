#!/usr/bin/python
################################################################################
import dataserver.dataserverproto 
from tools.zmqwrapper import zmqNonBinder, zmqBinder
from tools.timezonemap import datetimeTool
from tools.common import vipinfor, infor, err
from datetime import timedelta

class papertradeMode:

    def __init__(self, strategy):
        self.strategy = strategy
        self.config = strategy.getConfig()
        self.nonbinder = zmqNonBinder()
        self.binder = zmqBinder()

    def requestLiveMsgs(self, ds, session):
        # live data request message
        dsp = dataserver.dataserverproto.dataserverProto() 
        req = dsp.liveDataRequestEncode(1, ds, self.strategy.getToday(), session[0], session[1])

        # send message
        client = self.nonbinder.getClient()
        self.nonbinder.connectClientTo(self.strategy.engine.getConfig().system['dataServerUrl'])
        client.send(req.SerializeToString())
        [topic, url] = client.socket.recv_multipart()
        vipinfor('Strategy will receive data from %s.' % url)
        vipinfor('Data spec: %s' % topic)
        self.nonbinder.connectSubTo(url, topic)

    def run(self):
        tradhour = self.config.getTradSession()
        today = self.strategy.getToday()
        sessions = datetimeTool.bindDateSession([today], tradhour)
        datasrcs = self.config.getDataSources()

        for session in sessions:
            beg = session[0]
            end = session[1]

            if self.strategy.now() > end:
                continue
            
            # require session live data
            for ds in datasrcs:
                self.requestLiveMsgs(ds, session)

            self.strategy.onSessionInit(beg, end)

            # here uses non-timezone datetime for speed
            infor("Start trading between %s and %s" % (beg,end))

            while self.strategy.now() < beg - timedelta(seconds = 60*3):
                time.sleep(10)
                infor("sleeping ...")
            
            while self.strategy.now() <= end:
                msgs = self.nonbinder.nextMsg()
                for m in msgs:
                    self.strategy.onMsg(m)
            infor("End trading between %s and %s" % (beg,end))
            self.strategy.onSessionClear(beg, end)

       # except Exception as inst:
       #     err('Exit strategy %s' % self.config.getStrategyName())
       #     infor(inst)
