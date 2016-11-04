# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 13:24:18 2016

@author: delvin
"""

from PnLSystem import TradeAction, pairTradeManager
import EVATools

class OMS:
    def __init__(self, instruments):
        self.tm = None
        self.currentPrice = dict()
        for ins in instruments:
            self.currentPrice[ins] = None
                
    def setTradeManager(self, tradeManager):
        self.tm = tradeManager
        
    def updateCurrentPrice(self, instrument, price):
        self.currentPrice[instrument] = price
    
    def marketBuyPair(self, ts, instrument, spread, spreadSize, spreadInfor):
        p0 = self.currentPrice[instrument[0]]
        p1 = self.currentPrice[instrument[1]]
        
        self.tm.addPairTradeRecord( EVATools.tools.getDateFromDatetime(ts), 
                                    ts, TradeAction.Long, 
                                    p0, p1, 
                                    spreadSize)
                                    
        if isinstance(self.tm, pairTradeManager):
            self.tm.addSpreadTradeRecord(ts, TradeAction.Long, spread, spreadSize, spreadInfor)            
            
        return p0, p1
    
    def marketSellPair(self, ts, instrument, spread, spreadSize, spreadInfor):
        p0 = self.currentPrice[instrument[0]]
        p1 = self.currentPrice[instrument[1]]
        self.tm.addPairTradeRecord( EVATools.tools.getDateFromDatetime(ts), 
                                    ts, TradeAction.Short, 
                                    p0, p1,
                                    spreadSize)                                    
        if isinstance(self.tm, pairTradeManager):
            self.tm.addSpreadTradeRecord(ts, TradeAction.Short, spread, spreadSize, spreadInfor)
                             
        return p0, p1

    def limitBuy(self, ts, instrument, price, contractSz):
        print("Error: limitBuy not implemented")
        

    def limitSell(self, ts, instrument, price, contractSz):
        print("Error: limitSell not implemented") 
        
    
    def stopBuy(self, ts, instrument, price, contractSz):
        print("Error: stopBuy not implemented")
        
    
    def stopSell(self, ts, instrument, price, contractSz):
        print("Error: stopSell not implemented")
        