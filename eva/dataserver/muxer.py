#/usr/bin/python
################################################################################
# muxing combines multiple messages into a stream

from tools.common import infor, err
import pprint

class muxer:

    def __init__(self, streams, session):
        self.__muxing__(streams, session)

    def __muxing__(self, streams, session):
        msgset = []
        for ds in streams.keys():
            stream = streams[ds]
            if session in stream.keys():
                msgset.append(stream[session])
            else:
                infor('Data Source %s do not provide data' % ds.getId())
        msgsort = [m for s in msgset for m in s]
        msgsort.sort(key=lambda m: m.getBarStartTime())
        self.streams = msgsort

    def getMsg(self):
        for m in self.streams:
            yield m
        yield None
        
