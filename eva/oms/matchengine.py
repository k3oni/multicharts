#!/usr/bin/python
###############################################################################

from tools.common import infor, vipinfor, err
from Queue import Queue
from order import OrderType, OrderReply, OrderStatus, ActionType
from msg.msg import msgType
from msg.omsmsg import omsMsg

class matchEngine:

    def __init__(self):
        self.waitQueue = []

    def receiveOrder(self, order):
        self.waitQueue.append(order)
    
    def removeOrder(self, order):
        self.waitQueue.remove(order)

    def queryOrder(self, order):
        pass

    def cancelOrder(self, order):
        pass

    def matchOrder(self, msg):
        if len(self.waitQueue) == 0:
            return None

        reply = []
        for order in self.waitQueue:
            if order.orderType == OrderType.market:
                orderReply = self.fillMarketOrder(order, msg)
                if orderReply <> None:
                    reply.append(orderReply)
            elif order.orderType == OrderType.limit:
                orderReply = self.fillLimitOrder(order, msg)
                if orderReply <> None:
                    reply.append(orderReply)
            else:
                err('Unsupport order type to fill with order Id %s' % order.oid)        

        if len(reply) == 0:
            return None
        else:
            return reply

    def fillMarketOrder(self, order, msg):
        if msg.msgtype == msgType.barmsg:
            order.rep = OrderReply(OrderStatus.fullExecute, order.quant, msg.open)
            ordermsg = omsMsg()
            ordermsg.setOrder(order)
            return ordermsg
        else:
            err('Unsupport message type to fill market order.')
            msg.display()
            return None

    def fillLimitOrder(self, order, msg):
        if msg.msgtype == msgType.barmsg:
            if order.actionType == ActionType.buy and order.price <= msg.high:
                order.setReply(OrderReply(OrderStatus.fullExecute, order.quant, order.price))
                ordermsg = omsMsg()
                ordermsg.setOrder(order)
                return ordermsg

            if order.actionType == ActionType.sell and order.price <= msg.high:
                order.setReply(OrderReply(OrderStatus.fullExecute, order.quant, order.price))
                ordermsg = omsMsg()
                ordermsg.setOrder(order)
                return ordermsg
        else:
            err('Unsupport message type to fill limit order.')
            msg.display()
            return None



