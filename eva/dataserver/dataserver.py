#!/usr/bin/python
################################################################################
import sys, os, time
sys.path.append('/home/delvin/code/python/eva')
from tools.common import infor, err, vipinfor, warning
from engine.jsonconfig import jsonConfig
import engine.barcontroller
from evadb.dbservice import dbservice
from tools.zmqwrapper import zmqWrapper, zmqType, zmqNonBinder, zmqBinder
from datetime import datetime
from multiprocessing import Process, Pool
from proto import dataserver_pb2 as dsp
import feed.feed
from bar.bar import barLength
import dataserverproto

class dataServer:

    def __init__(self, cfgfile, today):
        self.today = today
        jcfg = jsonConfig()
        self.cfg = jcfg.load(cfgfile)
        self.dbs = self.getDBService()
        self.binder = zmqBinder()
        self.binder.bindServer(self.cfg.system['dataServerUrl'])
        self.serverIP = self.cfg.system['dataServerIP']
        url = self.getPublishUrl()
        self.pgroup = []
        self.topic_2_url = dict()
        self.portInUse = []
        infor('Hello, today is %s.' % today)
        infor('Data server listens ot %s' % self.cfg.system['dataServerUrl'])
        infor("Data server publish data to %s." % url)

    def getAvailablePort(self):
        # manage port for data stream
        port_basis = 93600
        for i in range(1, 10000):
            if port_basis + i not in self.portInUse:
                self.portInUse.append(port_basis+i)
                return port_basis + i
        return 0

    def releasePort(self, port):
        # give back ports for future use
        if port in self.portInUse:
            self.portInUse.remove(port)
        else:
            err('Port %s is not in use.' % port)

    def getDBService(self):
        return dbservice(self.cfg.system['dbname'], \
                         self.cfg.system['dbuser'], \
                         self.cfg.system['dbpasswd'],\
                         self.cfg.system['dbip'],\
                         self.cfg.system['dbport'])

    def getPublishUrl(self):
        return "{IP}:{Port}".format(IP=self.serverIP, \
                Port=self.cfg.system['dataServerPub'])

    def getAvailableUrl(self):
        return "{IP}:{Port}".format(IP=self.serverIP, \
                Port=self.getAvailablePort())
        

    def liveStream(self, msg, url, topic):
        # each data stream has a bar controller
        bc = engine.barcontroller.barController(self.dbs, \
                    self.cfg.getSystemConfig(), self.today)
        
        # extract request
        m = dataserverproto.dataserverProto()
        m.liveDataRequestDecode(msg)
        req = m.req
        
        # zmq does not support multiple threading read/write
        # generate live stream per port
        binder = zmqBinder()
        binder.bindPub(url)

        # prepare data
        if req.dataType == feed.feed.dataType.liveTickData:
            infor('Request live tick stream for topic %s' % topic)
            bc.prepareLiveData(req.instrument, req.dataType, req.today,\
                                     req.sb, req.se)
        elif req.dataType == feed.feed.dataType.liveBarData:
            infor('Request live bar stream for topic %s' % topic)
            bc.prepareLiveData(req.instrument, req.dataType, req.today,\
                                     req.sb, req.se, req.barLength)
        else:
            err('Cannot tell live stream data type')
            return

        bc.liveStreamTo(binder.getPubSocket(), req.sb, req.se, topic)
        binder.unbind(url)

    def handle(self, msg):
        m = dataserverproto.dataserverProto()
        m.liveDataRequestDecode(msg)

        if m.type == dsp.MessageBase.requestLiveData: # if msg is requesting data
            topic = self.generateTopic(m)

            # check if topic is already available
            if topic in self.topic_2_url.keys():
                url = self.topic_2_url[topic]
                vipinfor('Reuse data stream with url:%s' % url)
                vipinfor('Data spec : %s' % topic)
            else: # otherwise start a new process to supply data
                url = self.getAvailableUrl()
                vipinfor('A new data stream is generated using url:%s' % url)
                vipinfor('Data spec : %s' % topic)
                self.topic_2_url[topic] = url
                p = Process(target=dataServer.liveStream, args=(self, msg, url, topic))
                self.pgroup.append(p)
                p.start()
            self.binder.server.socket.send_multipart([topic, url])

    def generateTopic(self, msg):
        topic = None
        if msg.type == dsp.MessageBase.requestLiveData:
            ldr = msg.rawmsg.ldr
            if msg.req.dataType == feed.feed.dataType.liveBarData:
                topic = "{instrument}-{datatype}-{barlen}-{start}-{end}".format(\
                    instrument = ldr.instrument,\
                    datatype = ldr.dataType,\
                    barlen = ldr.barLength,\
                    start = ldr.session.sessionBegin,
                    end = ldr.session.sessionEnd)
            elif msg.req.dataType == feed.feed.dataType.liveTickData: 
                topic = "{instrument}-{datatype}-{start}-{end}".format(\
                    instrument = ldr.instrument,\
                    datatype = ldr.dataType,\
                    start = ldr.session.sessionBegin,
                    end = ldr.session.sessionEnd)
            else:
                err('Unsupport message type to generate topic', color='red')
        
        return topic    
    
    def run(self):
        while True:
            msg = self.binder.server.socket.recv()
            self.handle(msg)

        for p in pgroup:
            if p.is_alive():
                p.join()


if __name__ == "__main__":
    today = datetime.today()
    cfg = '/home/delvin/code/python/eva/engine/HC1_EP_paper.eva'
    ds = dataServer(cfg, today)
    ds.run()
