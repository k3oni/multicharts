#!/usr/bin/python
###############################################################################
## message factory creates msg according to datatype

from feed import dataType
from zmqtickmsg import zmqTickMsg
from zmqBarmsg import zmqBarMsg

class msgType:
    zmqTickMsg = 1
    zmqBarMsg = 2
    hdf5TickMsg = 3
    hdf5BarMsg = 4

class msgFactory:

    def __init__(self):
        pass

    def createMsg(self, type, rawmsg):

        if type == msgType.zmqTickMsg:
            return zmqTickMsg(rawmsg)

        if type == msgType.zmqBarMsg:
            return zmqBarMsg(rawmsg)

        if type == msgType.hdf5BarMsg:
            return hdf5BarMsg(rawmsg)

        print("Error: Unsupport message type yet")
        return False

