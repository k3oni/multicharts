#!/usr/bin/python
#
#   Hello OMS client in Python
#   Connects REQ socket to 192.168.0.110:5678
#   Sends "LOAD" to server, expects "Ack" back
#   Sends "ADD_ORDER" to server, expects "Ack" back
#
# Author: Hoffman TSUI
# Date: 2015-11-04

import zmq
import sys

context = zmq.Context()

raw_input("Press enter to START")

#  Socket to talk to server
print("Connecting to OMS server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.0.110:5678")

print("Connected.")

raw_input("Press enter to start IB gateway")

# Connect to IB
request = [b"Strategy1", b"REQ", b"LOAD", b"IBconn1", b"192.168.0.201", b"7496", b"", b"1"]
# client name, request, requesting action, connection name, gateway ib, gateway port, transaction account, ibclientid

socket.send_multipart(request)
message = socket.recv()
print("Received reply %s [ %s ]" % (request, message))

raw_input("Press enter to ADD Sell ORDER")

# Add Order
request = [b"Strategy1", b"REQ", b"ADD_ORDER", \
	b"IBconn1", b"192.168.0.201", b"7496", b"", b"1", \
	b"MarketOrder", b"Sell", b"1", b"HKFE", b"MHIX15", b"Future", b"12345", b"GoodTillCancel", b"OrderReference"]
# ordertype, action, quant, exchange, symbol, security type, limit price, timing force(detail), order name idused for query order status(detailed)

socket.send_multipart(request)
message = socket.recv()
print("Received reply %s [ %s ]" % (request, message))

raw_input("Press enter to ADD Buy ORDER")

# Add Order
request = [b"Strategy1", b"REQ", b"ADD_ORDER", \
	b"IBconn1", b"192.168.0.201", b"7496", b"", b"1", \
	b"MarketOrder", b"Buy", b"1", b"HKFE", b"MHIX15", b"Future", b"12345", b"GoodTillCancel", b"OrderReference"]

socket.send_multipart(request)
message = socket.recv()
print("Received reply %s [ %s ]" % (request, message))

