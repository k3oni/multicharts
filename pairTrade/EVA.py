# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 13:28:15 2016

@author: delvin
"""
from datasrc import datasrc
from oms import OMS
from strategy import GoldArb
from PnLSystem import pairTradeManager
from view import View as vi
from logger import infor
import datetime
from instrument import Instrument 

if __name__ == "__main__":    
    # configure
    instruments = [
        Instrument('AUAA', 'RMB', 1000),
        Instrument('GC', 'USD', 100)
    ]    
    syms = [i.name for i in instruments]
    contractSize = [3, 1]
    
    # data
    dataPath = r"C:\Users\delvin\Desktop\code\pairTrade\data"
    ds = datasrc()
    dataDict = ds.loadDataDir(dataPath)
    alignedData, dataSyms = ds.alignData(dataDict)
    
    allClosePrice = ds.getDailyClosePrice(alignedData, dataSyms)
    dailyClosePrice = {sym : allClosePrice[sym] for sym in allClosePrice.keys() if sym in syms}
    
    # tradeManager
    tm = pairTradeManager(instruments[0], instruments[1], 
                              contractSize[0], contractSize[1])

    # oms
    oms = OMS(syms)
    oms.setTradeManager(tm)

    strat = GoldArb("GoldArb", syms, contractSize)
    strat.setOMS(oms)
    strat.setTradeManager(tm)
    strat.setSession(list(alignedData.keys()))
    
    tsRange = [datetime.datetime(2016, 9, 1), datetime.datetime(2016, 10, 25)]
    rangeData, rangeDataSyms = ds.getRangeData(alignedData, dataSyms, tsRange)    
    #vi.plotData(rangeData, rangeDataSyms, 60)
    
    strat.training(rangeDataSyms, rangeData)
    strat.plotTrades(tsRange)
    #strat.showAllTrades()
    
    strat.computePnL(dailyClosePrice)
    strat.showPnL()
    strat.showTotalPnL()
