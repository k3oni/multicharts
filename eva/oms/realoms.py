#!/usr/bin/python
###############################################################################

class realOMS(oms):

    def __init__(self, strat):
        oms.__init__(self, strat)
        self.initOMS()
    
    def initOMS(self):
        self.mq = strat.nonbinder.dealer
        omsip = self.strat.engine.getConfig().system['OMSUrl']
        self.strat.nonbinder.connectDealerTo(omsip)
        vipinfor('OMS is ready : connected to %s.' % omsip)
        pl = API_pb2.Payload()
        pl.type = API_pb2.Payload.REQ
        pl.request_id = 1
        pl.request.command = API_pb2.Payload.Request.LoadGateway 
        gw = pl.request.load_gateway
        gw.account_id = 1
        self.mq.send_multipart( ["", "C01", "REQ", pl.SerializeToString()])

    def sendOrder(self):
        reqID = 1
        pl = API_pb2.Payload()
        pl.type = API_pb2.Payload.REQ
        pl.request_id = reqID
        pl.request.command = API_pb2.Payload.Request.AddOrder 

        ord              = pl.request.add_order
        ord.account_id   = 1
        ord.order_type   = API_pb2.MarketOrder
        ord.action       = API_pb2.Buy
        ord.quantity     = 2
        ord.exchange     = "HKFE"
        ord.product_code = "HHIX15"
        ord.security_type= API_pb2.Future
        ord.price        = 10000 
        ord.time_in_force= API_pb2.GoodTillCancel
        ord.security_type= API_pb2.Future
        ord.order_reference= "TEST_ORDER_API_%3d" % reqID
        
        self.mq.send_multipart( ["", "C01", "REQ", pl.SerializeToString() ])
        infor("Send order ")

    
