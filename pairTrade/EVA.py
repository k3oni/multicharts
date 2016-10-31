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
import datetime 

if __name__ == "__main__":    
    # configure
    instruments = ['GC', 'AUAA']
    contractSize = [10, 31]
    
    # data
    dataPath = "C:\Users\delvin\Desktop\code\pairTrade\data"
    ds = datasrc()
    dataDict = ds.loadDataDir(dataPath)
    alignedData, dataSyms = ds.alignData(dataDict)
    #vi.plotData(alignedData, dataSyms, 60)
    
    # tradeManager
    tm = pairTradeManager(instruments[0], instruments[1], contractSize[0],\
                            contractSize[1])
    # oms
    oms = OMS(instruments)
    oms.setTradeManager(tm)

    strat = GoldArb("GoldArb", instruments, contractSize)
    strat.setOMS(oms)
    strat.setTradeManager(tm)
    tsRange = [datetime.datetime(2016, 10, 1), datetime.datetime(2016, 10, 25)]
    rangeData, rangeDataSyms = ds.getRangeData(alignedData, dataSyms, tsRange)    
    
    strat.training(rangeDataSyms, rangeData)
    strat.showTrades(tsRange)
    print("Finish")