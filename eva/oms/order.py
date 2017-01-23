#!/usr/bin/python
################################################################################
from enum import Enum
from tools.common import infor, vipinfor

class ActionType(Enum):
    buy = 'buy'
    sell  = 'sell'

class EntryExitType(Enum):
    entry = 'entry'
    exit = 'exit'

class OrderType(Enum):
    market = 1
    limit  = 2

class TimeInForce(Enum):
    day = 'day'

class OrderStatus(Enum):
    fullExecute = 'fullExecute'
    partialExecute = 'partialExecute'
    reject = 'reject'

class OrderReply:
    def __init__(self, status, quant, price):
        self.status = status
        self.quant = quant
        self.price = price

class order:
    def __init__(self, oid, contractCode, quant, price, actionType, entryExitType, \
                        orderType, timeInForce):
        self.oid = oid
        self.contractCode = contractCode
        self.price = price
        self.quant = quant
        self.actionType = actionType
        self.entryExitType = entryExitType
        self.orderType = orderType
        self.timeInForce = timeInForce
        self.orderReply = None

    def display(self):
        c = '{contract} {action} {quant} @ {price} as {eet} with a {orderType} order.\
                 TimeInForce: {timeInForce}'. format( 
                    contract = self.contractCode, \
                    action = self.actionType.value,\
                    quant = self.quant, \
                    price = self.price, \
                    eet = self.entryExitType,\
                    orderType = self.orderType,\
                    timeInForce = self.timeInForce)
        vipinfor(c)
        if self.orderReply == None:
            vipinfor('Order has not been replied.')
        else:
            c = 'Order status {status}, quantity {quant}, price {price}'.format(\
                status = self.orderReply.status,\
                quant = self.orderReply.quant,\
                price = self.orderReply.price)
            vipinfor(c)

    def setReply(self, reply):
        self.orderReply = reply
