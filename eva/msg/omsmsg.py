#!/usr/bin/python
###############################################################################
from msg import msgType, msg
from tools.common import infor, vipinfor

class omsMsg(msg):

    def __init__(self, msgtype = msgType.omsmsg):
        msg.__init__(self, msgtype)
    
    def setOrder(self, order):
        self.order = order

    def display(self):
        self.order.display()  
