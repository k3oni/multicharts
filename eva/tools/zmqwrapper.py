#!/usr/bin/python
################################################################################
import zmq, time
import othersrc.message_pb2
from enum import Enum
from tools.common import infor
from zmq.eventloop import ioloop, zmqstream
from othersrc import message_pb2
from msg import zmqtickmsg, zmqbarmsg
from pprint import pprint
from proto import API_pb2

class zmqType(Enum):
    pub  = zmq.PUB
    sub  = zmq.SUB
    push = zmq.PUSH
    pull = zmq.PULL    
    rep  = zmq.REP
    req  = zmq.REQ
    dealer = zmq.DEALER

class zmqWrapper:

    def __init__(self, zmqtype):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmqtype.value)

    def bind(self, url):
        self.ipport = "tcp://{url}".format(url=url)
        #infor("bind to %s" % self.ipport)
        ret = self.socket.bind(self.ipport)
        time.sleep(1) # wait for initialization finished

    def unbind(self, url):
        self.ipport = "tcp://{url}".format(url=url)
        infor("unbind to %s" % self.ipport)
        self.socket.unbind(self.ipport)
        time.sleep(1)
    
    def connect(self, url):
        self.ipport = "tcp://{url}".format(url=url)
        self.socket.connect(self.ipport)

    def disconnect(self, url):
        self.ipport = "tcp://{url}".format(url=url)
        self.socket.disconnect(self.ipport)
    
    def send(self, msg):
        #infor("Send to %s" % (self.ipport))
        self.socket.send(msg)

    def recv(self):
        msg = self.socket.recv()
        infor('Received msg: %s' % msg)
        return msg

    def send_string(self, msg):
        infor("Send to %s" % self.ipport)
        self.socket.send_string(msg)

    def send_multipart(self, strlist):
        self.socket.send_multipart(strlist) 

    def recv_multipart(self):
        return self.socket.recv_multipart()
    
    def getSocket(self):
        return self.socket

class zmqNonBinder:

    def __init__(self):
        self.msgbase = message_pb2.MessageBase()
        self.poller = zmq.Poller()
        self.client = zmqWrapper(zmqType.req)
        self.pull = zmqWrapper(zmqType.pull)
        self.sub = zmqWrapper(zmqType.sub)
        self.dealer = zmqWrapper(zmqType.dealer)

    def connectClientTo(self, url):
        self.client.connect(url)
        self.poller.register(self.client.getSocket(), zmq.POLLIN)

    def disconnectClient(self, url):
        self.client.disconnect(url)
        self.poller.unregister(url)

    def connectPullTo(self, url):
        self.pull.connect(url)
        self.poller.register(self.pull.getSocket(), zmq.POLLIN)

    def disconnectPull(self, url):
        self.pull.disconnect(url)
        self.poller.unregister(url)

    def connectSubTo(self, url, topic):
        self.sub.connect(url)
        self.sub.getSocket().setsockopt(zmq.SUBSCRIBE, topic)
        self.poller.register(self.sub.getSocket(), zmq.POLLIN)
    
    def disconnectSub(self, url):
        self.sub.disconnect(url)
        self.poller.unregister(url)

    def connectDealerTo(self, url):
        self.dealer.connect(url)
        self.poller.register(self.dealer.getSocket(), zmq.POLLIN)

    def disconnectDealer(self, url):
        self.dealer.disconnect(url)
        self.poller.unregister(url)

    def getClient(self):
        return self.client

    def getClientSocket(self):
        return self.client.socket

    def getPull(self):
        return self.pull

    def getPullSocket(self):
        return self.pull.socket

    def getSub(self):
        return self.sub

    def getSubSocket(self):
        return self.sub.socket    

    def zmqMsgToEvaMsg(self, buf):
        self.msgbase.ParseFromString(buf)
        datatype = self.msgbase.type
        if datatype == self.msgbase.TICKMSG:
            msg = zmqtickmsg.zmqTickMsg(self.msgbase.tickMsg)
            return msg
        if datatype == self.msgbase.BAR:
            msg = zmqbarmsg.zmqBarMsg(self.msgbase.bar)
            return msg

    def nextMsg(self):
        msgs = []
        sockets = dict(self.poller.poll())

        if self.client.getSocket() in sockets and \
                sockets[self.client.getSocket()] == zmq.POLLIN:
            msgs.append(self.zmqMsgToEvaMsg(self.client.recv()))

        if self.pull.getSocket() in sockets and \
                sockets[self.pull.getSocket()] == zmq.POLLIN:
            msgs.append(self.zmqMsgToEvaMsg(self.pull.recv()))

        if self.sub.getSocket() in sockets and \
                sockets[self.sub.getSocket()] == zmq.POLLIN:

            topic, buf = self.sub.socket.recv_multipart()
            msg = self.zmqMsgToEvaMsg(buf)   
            msg.display()
            msgs.append(msg)

        if self.dealer.getSocket() in sockets and \
                sockets[self.dealer.getSocket()] == zmq.POLLIN:
            rep = self.dealer.getSocket().recv_multipart()
            pl = API_pb2.Payload()
            pl.ParseFromString(rep[3])
            if pl.type == API_pb2.Payload.ACK:
                ack = pl.acknowledge.add_order
                infor( "Rcvd Ack: " + str(ack.account_id) + " " + ack.order_reference)

        return msgs

class zmqBinder:
    
    def __init__(self):
        self.server = zmqWrapper(zmqType.rep)
        self.push   = zmqWrapper(zmqType.push)
        self.pub    = zmqWrapper(zmqType.pub)

    def bindServer(self, url):
        self.server.bind(url)

    def bindPush(self, url):
        self.push.bind(url)

    def bindPub(self, url):
        self.pub.bind(url)

    def unbindServer(self, url):
        self.server.unbind(url)

    def unbindPush(self, url):
        self.push.unbind(url)

    def unbindPub(self, url):
        self.pub.unbind(url)

    def getServer(self):
        return server

    def getPub(self):
        return self.pub

    def getPush(self):
        return self.push

    def getServerSocket(self):
        return self.server.socket

    def getPushSocket(self):
        return self.push.socket

    def getPubSocket(self):
        return self.pub.socket
