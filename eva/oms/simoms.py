#!/usr/bin/python
###############################################################################
from oms import oms
from matchengine import matchEngine
from tools.common import vipinfor

class simoms(oms):
    def __init__(self, strat, matchEngine):
        oms.__init__(self, strat)
        self.me = matchEngine

    def sendOrder(self, order):
        vipinfor('Hello, I am in simoms.')
        self.me.receiveOrder(order)

    def queryOrder(self, order):
        self.me.queryOrder(order)

    def cancelOrder(self, order):
        self.me.cancelOrder(order)
