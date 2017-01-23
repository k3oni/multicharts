#!/usr/bin/python
###############################################################################

from __future__ import print_function
import sys
import zmq
import message_pb2

def pstderr(*objs):
    print(*objs, file=sys.stderr)


# Socket to talk to server
serverurl = '192.168.0.20:20123'
context = zmq.Context()
socket = context.socket(zmq.SUB)

pstderr("#Testing receiving ZMQ msg...")
socket.setsockopt_string(zmq.SUBSCRIBE, "".decode('ascii'))	       
socket.connect("tcp://%s" % serverurl)
mb = message_pb2.MessageBase()

while (True) :
  msg = socket.recv()
  mb.ParseFromString(msg)
  tm = mb.tickMsg
  pstderr( tm.seqnum, tm.ts, tm.contractID, \
    message_pb2.MessageBase.TickType.Name(tm.tickType), tm.msgStr)
  
