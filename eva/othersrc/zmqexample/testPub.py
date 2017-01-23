#!/usr/bin/python

import zmq, random, sys, time

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)
while True:
    topic = random.randrange(9999, 10005)
    data = random.randrange(1, 215) - 80
    content = "%d %d" % (topic, data)
    print content
    socket.send(content)
    time.sleep(1)
