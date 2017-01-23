#!/usr/bin/python

from __future__ import print_function
import sys
import zmq
import message_pb2
import time

def pstderr(*objs):
    print(*objs, file=sys.stderr)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.PUB)

pstderr("#Testing sending ZMQ msg...")
socket.bind("tcp://*:20132")

mb      = message_pb2.MessageBase()
mb.type = message_pb2.MessageBase.ORDER
ord     = mb.order

ord.contractID = "HHI201510"
ord.side       = message_pb2.MessageBase.SIDE_BUY
ord.qty        = 3
ord.orderType  = message_pb2.MessageBase.OrderType_LMT
ord.price      = 10412
ord.acctID     = "DU1234567"
#ord.orderRef   = "TestOrder_"

#while (True) :
for i in range(10):
  orderID = "%03d" % i
  mb.order.orderRef =  "TestOrder_" + orderID
  socket.send(mb.SerializeToString())
  time.sleep(1)
  
