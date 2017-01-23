#!/usr/bin/python
###############################################################################

from proto import dataserver_pb2 as dsp
from datetime import datetime
import feed.feed
from bar.bar import barLength
from tools.common import infor
import dateutil.parser

class LiveDataRequest:
    def __init__(self):
        self.instrument = None
        self.datatype   = None
        self.today      = None
        self.sb         = None
        self.se         = None    
        self.barLength  = None

class HistoricalDataRequest:
    def __init__(self):
        self.instrument  = None   
        self.expireYear  = None   
        self.expireMonth = None  
        self.typeCode    = None  
        self.dataType    = None  
        self.barLength   = None  
        self.startDate   = None  
        self.endDate     = None  
        self.sessions    = None

class dataserverProto:

    def __init__(self):
        pass

    def liveDataRequestEncode(self, requestId, ds, today, sessionBeg, \
                                sessionEnd):

        msg                         = dsp.MessageBase()
        msg.type                    = dsp.MessageBase.requestLiveData
        msg.requestId               = requestId

        req                         = msg.ldr
        req.instrument              = ds.getInstrument()
        req.dataType                = ds.getDataType().value
        req.today                   = today.isoformat()
        req.session.sessionBegin    = sessionBeg.isoformat()              
        req.session.sessionEnd      = sessionEnd.isoformat()              

        if ds.getDataType() == feed.feed.dataType.liveBarData:
            req.barLength = ds.getBarLength().barlen
        return msg

    def liveDataRequestDecode(self, msg):
        m = dsp.MessageBase()
        m.ParseFromString(msg)
        self.rawmsg = m
        self.requestId  = m.requestId
        self.type = m.type

        ldr = m.ldr
        req = LiveDataRequest()
        req.instrument = ldr.instrument
        req.dataType = feed.feed.dataType(ldr.dataType)
        req.today  = dateutil.parser.parse(ldr.today)        
        req.sb     = dateutil.parser.parse(ldr.session.sessionBegin)
        req.se     = dateutil.parser.parse(ldr.session.sessionEnd)

        if req.dataType == feed.feed.dataType.liveBarData:
            req.barLength = barLength(ldr.barLength)
        self.req = req

    def historicalDataRequestEncode(self, requestId, ds, start, end, tradSessions):
        msg                         = dsp.MessageBase()
        msg.type                    = dsp.MessageBase.requestHistoricalData
        msg.requestId               = requestId

        req                         = msg.hdr
        req.instrument              = ds.getInstrument()
        req.expireYear              = ds.getExpireYear()
        req.expireMonth             = ds.getExpireMonth()
        req.typeCode                = ds.getTypeCode()
        req.dataType                = ds.getDataType().value
        req.barLength               = ds.getBarLength()
        req.startDate               = start
        req.endDate                 = end

        for sess in tradSessions:
            session = msg.hdr.sessions.Add()
            session.sessionBegin    = sessionBeg.isoformat()              
            session.sessionEnd      = sessionEnd.isoformat()              

    def historicalDataRequestDecode(self, msg):
        m = dsp.MessageBase()
        m.ParseFromString(msg)
        self.rawmsg = m
        self.requestId = m.requestId
        self.type = m.type

        hdr = m.hdr
        req = HistoricalDataRequest()        
