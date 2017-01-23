#!/usr/bin/python

from __future__ import print_function
import sys
import zmq
import API_pb2
import time

def pstderr(*objs):
    print(*objs, file=sys.stderr)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.REQ)

pstderr("#Testing sending ZMQ msg...")
socket.connect("tcp://192.168.0.110:5678")
#socket.bind("tcp://*:20132")




reqID = 1

pl            = API_pb2.Payload()
pl.type       = API_pb2.Payload.REQ
pl.request_id = reqID

req         = pl.request
req.command = API_pb2.Payload.Request.LoadGateway 

gw              = req.load_gateway
gw.account_id   = 1
#ord.order_type   = API_pb2.MarketOrder
#ord.action       = API_pb2.Buy
#ord.quantity     = 3
#ord.exchange     = "HKFE"
#ord.product_code = "HHIX15"
#ord.security_type= API_pb2.Future
#ord.price        = 10000 
#ord.time_in_force= API_pb2.Day
#ord.security_type= API_pb2.Future
#ord.order_reference= "TEST_ORDER_API_%3d" % reqID
#
##while (True) :
##for i in range(10):
##  orderID = "%03d" % i
##  mb.order.orderRef =  "TestOrder_" + orderID
##socket.send_multipart( ["C01", "REQ", " ", " " ])
socket.send_multipart( ["C01", "REQ", pl.SerializeToString() ])
time.sleep(1)
#  
