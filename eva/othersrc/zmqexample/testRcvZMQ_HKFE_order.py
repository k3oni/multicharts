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
socket.connect("tcp://localhost:20132")
socket.setsockopt_string(zmq.SUBSCRIBE, "".decode('ascii'))	       

mb = message_pb2.MessageBase()

total_temp = 0
#for update_nbr in range(5):
while (True) :
  #pstderr("Recv Msg")
  msg = socket.recv()
  #pstderr("Recved Msg")

  mb.ParseFromString(msg)
  ord = mb.order
  #pstderr(ord.orderRef)
  pstderr( ord.contractID, 
           message_pb2.MessageBase.Side.Name(ord.side), 
           ord.qty,
           message_pb2.MessageBase.OrderType.Name(ord.orderType), 
           ord.price,
           ord.acctID,
           ord.orderRef)
  
