#!/usr/bin/python
################################################################################

# a wrapper of oms of Hoffman oms module
# each strategy has a wrapper

import zmq, time
from proto import API_pb2
from tools.common import infor, err, vipinfor
from strategy.strategymode import strategyMode
from order import order, ActionType, EntryExitType, OrderType, TimeInForce, \
                OrderStatus, OrderReply

class oms:

    def __init__(self, strat):
        self.strat = strat
        self.orderId = 0

    # interface for derivde class
    def sendOrder(self, order):
        vipinfor('Hello, I am in oms.')
        pass

    def queryOrder(self, order):
        pass

    def cancelOrder(self, order):
        pass

    def receiveReply(self):
        pass

    # basic operation
    def buy(self, contract, orderType, quant, price, timeInForce = TimeInForce.day):
        oid = self.getOrderId()
        o = order(oid, contract, quant, price, ActionType.buy, EntryExitType.entry, \
                    orderType, timeInForce)
        self.sendOrder(o)

    def sell(self, contract, orderType, quant, price, timeInForce = TimeInForce.day):
        oid = self.getOrderId()
        o = order(oid, contract, quant, price, ActionType.sell, EntryExitType.exit, \
                    orderType, timeInForce)
        self.sendOrder(o)

    def shortSell(self, contract, orderType, quant, price, timeInForce = TimeInForce.day):
        oid = self.getOrderId()
        o = order(oid, contract, quant, price, ActionType.sell, EntryExitType.entry, \
                    orderType, timeInForce)
        self.sendOrder(o)

    def buyToCover(self, contract, orderType, quant, price, timeInForce = TimeInForce.day):
        oid = self.getOrderId()
        o = order(oid, contract, quant, price, ActionType.buy, EntryExitType.exit, \
                    orderType, timeInForce)
        self.sendOrder(o)
    
    # order management
    def getOrderId(self):
        self.orderId = self.orderId + 1
        return self.orderId - 1

    # real pnl

