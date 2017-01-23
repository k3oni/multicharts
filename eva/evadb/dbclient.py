#!/usr/bin/python

import zmq

ip = '192.168.0.47'
port = 40966
url='tcp://{ip}:{port}'.format(ip=ip, port=port)
context = zmq.Context()
print "Connecting to {ip}:{port}".format(ip=ip, port=port)
socket = context.socket(zmq.REQ)
socket.connect(url)

def query(msg):
    request = msg
    print "send request: %s" % request
    socket.send(request)
    message = socket.recv()
    print "receive message: %s " % message 

query("getInstrumentFilePath('HC1 Index')")
query("getTradingDatePerContract('HCV5 Index', '20150101', '20151116')")

#request = "getInstrumentFilePath('HC1 Index')"
#print "send request: %s" % request
#socket.send(request)
#message = socket.recv()
#
#print "receive message: %s " % message 
#request = "getTradingDatePerContract('HCV5 Index', '20150101', '20151116')"
#print "send request: %s" % request
#socket.send(request)
#message = socket.recv()
#print "receive message: %s " % message 
#
