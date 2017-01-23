#!/usr/bin/python
###############################################################################
## message base class

class msgType:
    tickmsg = 1
    barmsg  = 2 
    omsmsg  = 3

class msg:

    def __init__(self, msgtype):
        self.dt = 0
        self.content = ''
        self.msgtype = msgtype

    def getTS(self):
        return self.dt

    def getContent(self):
        return self.content

    def display(self):
        print self.getContent()
