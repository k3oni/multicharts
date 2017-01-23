#!/usr/bin/python

from __future__ import print_function
import sys
import zmq
import message_pb2

def pstderr(*objs):
    print(*objs, file=sys.stderr)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

pstderr("#Testing receiving ZMQ msg...")
#socket.connect("tcp://192.168.0.20:20132")
socket.connect("tcp://192.168.0.20:20131")
socket.setsockopt_string(zmq.SUBSCRIBE, "".decode('ascii'))	       

mb = message_pb2.MessageBase()

total_temp = 0
#for update_nbr in range(5):
while (True) :
  msg = socket.recv()
  print(msg)
  print(len(msg), msg.encode('hex'), len(msg.encode('hex')))
  mb.ParseFromString(msg)
  tm = mb.bar
  print(tm.seqnum, tm.ts, tm.contractID, message_pb2.MessageBase.PxType.Name(tm.pxType), tm.nbDec, tm.open, tm.high, tm.low, tm.close, tm.volume, tm.barcnt, tm.wap, tm.gap)
  print()
  #tm = mb.tickMsg
  #print tm.seqnum, tm.ts, tm.contractID, message_pb2.MessageBase.TickType.Name(tm.tickType), tm.msgStr
  #pstderr( tm.seqnum, tm.ts, tm.contractID, message_pb2.MessageBase.TickType.Name(tm.tickType), tm.msgStr)
  #print "[",msg,"]"
  #zipcode, temperature, relhumidity = string.split()
  #total_temp += 1 #int(temperature)
  #print total_temp
  
