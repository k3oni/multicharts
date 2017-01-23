#!/usr/bin/python

import sys, zmq

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.SUB)
print "Collect data"
socket.connect("tcp://localhost:%s" % port)
topicfilter = "10001"
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)
while True:
    string = socket.recv()
    print string
