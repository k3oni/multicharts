#/usr/bin/python
################################################################################
import blpapi
from collections import deque
from tools.common import infor, err
from tools.timezonemap import timeZoneMap

class bbg:

    def __init__(self, server, port):
        self.valid = False
        # Fill SessionOptions
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost(server)
        sessionOptions.setServerPort(port)
        print "Bloomberg: Connecting to %s:%d" % (server, port)
    
        # Create a Session
        self.session = blpapi.Session(sessionOptions)
    
        # Start a Session
        if not self.session.start():
            err("Bloomberg: Failed to start session.")
            return

        if not self.session.openService("//blp/refdata"):
            err("Bloomberg: Failed to open //blp/refdata")
            return

        # reference data service
        self.refDataService = self.session.getService("//blp/refdata")
        self.valid = True

    def __exit__(self): 
        self.session.stop()

    # check if Bloomberg cannot find result and send back error message
    def checkError(self, event):
        for msg in event:
            if msg.hasElement("securityData"):
                sda = msg.getElement("securityData")
                for i in range(0, sda.numValues()):
                    sec = sda.getValueAsElement(i)
                    if sec.hasElement("securityError"):
                        err("Error sent by bloomberg.") 
                        print msg

    # parse returned message for field data
    def getFieldData(self, event):
        fds = deque()
        secs = [] 
        for msg in event:
            if msg.hasElement("securityData"):
                sda = msg.getElement("securityData")
                for i in range(0, sda.numValues()):
                    sec = sda.getValueAsElement(i)
                    secs.append(sec.getElementAsString("security"))
                    fds.append(sec.getElement("fieldData"))
        return fds, secs

    # get timezone for an instruement
    #def getTimeZone(self, instrument):
    #    req = self.refDataService.createRequest("ReferenceDataRequest")
    #    req.append("securities", instrument)
    #    req.append("fields", "TIME_ZONE_NUM")
    #    self.session.sendRequest(req)
    #    while(True):
    #        ev = self.session.nextEvent(500)
    #        fdlist, secs = self.getFieldData(ev)
    #        if fdlist:
    #            for fd in fdlist:
    #                return float(fd.getElementAsString('TIME_ZONE_NUM'))

    #        if ev.eventType() == blpapi.Event.RESPONSE:
    #            break
    #    return None
 
    ###########################################################################
    # get all contracts with the same underlying instrument
    # if withExpired is true, expired contracts will also be returned
    # otherwise, only unexpired contracts are returned

    def getFutureChain(self, instrument, withExpired): 
        # future chain
        request = self.refDataService.createRequest("ReferenceDataRequest")    
        request.append("securities", instrument)
        request.append("fields", "FUT_CHAIN")

        if withExpired:
            overrides = request.getElement("overrides")
            override1 = overrides.appendElement()
            override1.setElement("fieldId", "INCLUDE_EXPIRED_CONTRACTS")
            override1.setElement("value", "Y")

        self.session.sendRequest(request)
    
        while(True):
            ev = self.session.nextEvent(500)
            self.checkError(ev)
            fds, secs = self.getFieldData(ev)
            if fds:
                return self.handleActiveContract(fds)
                          
            # Response completly received, so we could exit
            if ev.eventType() == blpapi.Event.RESPONSE:
                break

    
    def handleActiveContract(self, fds):
        def appendFD(fd):
            acs = deque()
            fcs = fd.getElement('FUT_CHAIN')
            for i in range(0, fcs.numValues()):
                acs.append(fcs.getValueAsElement(i).\
                            getElementAsString('Security Description'))
            return acs
        return map(appendFD, fds)[0]

    ###########################################################################
    # get information of a contract
    # currently only support start and end date of this contract
    def requestContractsStartAndExpire(self, instrument, tz, contracts):
        batchsize = 256
        ci = [] # contract start and expire date
        cn = [] # contract name
        for i in xrange(0, len(contracts), batchsize):
            subset = []
            for j in range(i, min(i+batchsize,len(contracts))):
                subset.append(contracts[j]) 
            req = self.refDataService.createRequest("ReferenceDataRequest")
            for contract in subset:
                req.append("securities", contract)
            req.append("fields", "FUT_FIRST_TRADE_DT")
            req.append("fields", "FUT_LAST_TRADE_DT")    
            overrides = req.getElement("overrides")
            override1 = overrides.appendElement()
            override1.setElement("fieldId", "INCLUDE_EXPIRED_CONTRACTS")
            override1.setElement("value", "Y")
            
            #print "Sending Request:", req
            self.session.sendRequest(req)
            
            while(True):
                # We provide timeout to give the chance to Ctrl+C handling:
                ev = self.session.nextEvent(500)
                self.checkError(ev)
                fds, secs = self.getFieldData(ev)

                if fds:
                    ci = ci + self.handleContractInfor(fds)
                    cn = cn + secs
                # Response completly received, so we could exit
                if ev.eventType() == blpapi.Event.RESPONSE:
                    break   

        # convert date from string to date object
        def pairDate(p):
            return (timeZoneMap.datestr2Date(p[0], tz), timeZoneMap.datestr2Date(p[1], tz))        

        ci = map(pairDate, ci)
        contracts = sorted(zip(cn, ci), key=lambda item: item[1][1])
        cn = [c[0] for c in contracts]
        ci = [c[1] for c in contracts] 
        return cn, ci

    def handleContractInfor(self, fds):
        def handleFD(fd):
            if fd.hasElement("FUT_FIRST_TRADE_DT") \
                and fd.hasElement("FUT_LAST_TRADE_DT"):
                return (fd.getElementAsString("FUT_FIRST_TRADE_DT"),\
                      fd.getElementAsString("FUT_LAST_TRADE_DT"))
            else:
                return None
        return map(handleFD, fds)


