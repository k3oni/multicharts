#!/usr/bin/python
###############################################################################
from enum import Enum
from datetime import timedelta

class barLength:
    sec5    = 's5'
    sec10   = 's10'
    min1    = 'm1'
    min3    = 'm3'
    min8    = 'm8'
    hourly  = 'h1'
    daily   = 'd1' 
    weekly  = 'w1'
    monthly = 'mon1'

    def __init__(self, barlen):
        self.barlen = barlen
        bm = dict()
        bm[self.sec5]    = timedelta(seconds=5)
        bm[self.sec10]   = timedelta(seconds=10)
        bm[self.min1]    = timedelta(minutes=1)
        bm[self.min3]    = timedelta(minutes=3)
        bm[self.min8]    = timedelta(minutes=8)
        bm[self.hourly]  = timedelta(hours=1)
        bm[self.daily]   = timedelta(days=1)
        bm[self.weekly]  = timedelta(weeks=1)
        self.bm = bm

    def toTimedelta(self):
        return self.bm[self.barlen]

class barField(Enum):
    open    = 'open'
    high    = 'high'
    low     = 'low'
    close   = 'close'        

if __name__ == "__main__":
    bl = barLength.min1
    print bl.toTimedelta
