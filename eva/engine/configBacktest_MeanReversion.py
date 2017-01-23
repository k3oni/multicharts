#!/usr/bin/python
# This is an example of configuring a backtest strategy

from jsonconfig import jsonConfig
from feed.feed import dataType
from bar.bar import barLength as bl
import pprint

if __name__ == '__main__':

    jcfg = jsonConfig()
    filename = 'HC1_MR_backtest.eva'

    # create strategy config
    account = 'delvin'
    strategy = 'meanReversion'
    stratId = 1
    stratStartDate = '2015-11-12'
    stratEndDate = '2015-11-16'
    timezone = 'Asia/Hong_Kong'
    tradInstruments = ['HC1 Index']

    jcfg.addBacktestStrategy(account, strategy, stratId, tradInstruments, stratStartDate, \
                        timezone, stratEndDate, timezone)

    key = jcfg.getStrategyKey(account, strategy, stratId)

    # add data source
    jcfg.addDataSrc(key, instrument = 'HC1 Index', \
                    datatype = dataType.historicalBarData.value,\
                    barlen  = bl.min1,\
                    startdate = stratStartDate,\
                    tilldate = stratEndDate)

    # add strategy parameters
    para = dict()
    para['Instrument'] = tradInstruments[0]
    para['SMALength'] = 14
    para['EMALength'] = 6
    para['SDLength']= 20
    para['f1'] = 0.8
    para['f6'] = 0
    para['stochLength'] = 6
    para['smoothLen1'] = 7
    para['smoothLen2'] = 3
    para['BBLength'] = 20
    para['inSD'] = 2
    para['outSD'] = 3
    para['filterSD'] = 3
    para['levelDiffPercent'] = 0.004
    para['levelRisk'] = 3
    para['gapRatio'] = 0.015
    para['levelRatio'] = 1.8
    para['constHr'] = 2
    para['constDay'] = 1

    # variable level difference
    para['levelDiffSeparator'] = [1, 1.25, 1.5, 1.75, 2]
    para['levelScale'] = [1, 1, 1, 1, 1, 1.8]
    para['preDayNum'] = 50
    para['eptime'] = '09:15:00'    

    para['tradSession'] = ['09:15:00-12:00:00', '13:00:00-23:10:00']  
    para['tradSessionTimeZone'] = 'Asia/Hong_Kong'
    para['EPBroadcast'] = '192.168.0.47:33170'
    para['stratDataMQUrl']  = '192.168.0.47:33620'

    # mean reversion parameters
    para['levelNum'] = 7
    para['positionPerPositiveLevel'] = [1, 1, 1, 1, 1, 1, 1]
    para['positionPerNegativeLevel'] = [1, 1, 1, 1, 1, 1, 1]

    jcfg.addStrategyPara(key, para)
    
    # save config
    jcfg.save(filename)
