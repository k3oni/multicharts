#!/usr/bin/python
###############################################################################
# moving standard deviation

from collections import deque
import basis

class movingStd:
    
    def __init__(self, period):
        self.period = period
        self.deque = []
        self.maxlen = period
        self.std = []

    def initMovingStd(self, initdata):
        self.deque = deque(initdata[0:self.period], self.maxlen)
        self.std.append(basis.std(self.deque))
        for i in range(self.period, len(initdata)):
            self.deque.append(initdata[i]) 
            self.std.append(basis.std(self.deque))
        return self.std[-1]

    def update(self, datapoint):
        self.deque.append(datapoint)
        self.std.append(basis.std(self.deque))
        return self.std[-1]

    def getStd(self):
        return self.std

        
