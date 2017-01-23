#!/usr/bin/python
# This is an example of configuring a backtest strategy

from jsonconfig import jsonConfig
from feed.feed import dataType
from bar.bar import barLength as bl
import pprint

if __name__ == '__main__':

    jcfg = jsonConfig()
    filename = 'CI_backtest.eva'

    # create strategy config
    account = 'delvin'
    strategy = 'CI'
    stratId = 1
    stratStartDate = '2015-11-01'
    stratStartTZ = 'Asia/Hong_Kong'
    stratEndDate = '2015-11-06'
    stratEndTZ = 'Asia/Hong_Kong'
    tradInstruments = ['HC1 Index', 'HI1 Index']

    jcfg.addBacktestStrategy(account, strategy, stratId, tradInstruments, stratStartDate, \
                        stratStartTZ, stratEndDate, stratEndTZ)

    key = jcfg.getStrategyKey(account, strategy, stratId)

    # add data source
    jcfg.addDataSrc(key, instrument = 'HC1 Index', \
                    datatype = dataType.historicalBarData.value,\
                    barlen  = bl.min1,\
                    startdate = stratStartDate,\
                    tilldate = stratEndDate)

    jcfg.addDataSrc(key, instrument = 'HI1 Index', \
                    datatype = dataType.historicalBarData.value,\
                    barlen  = bl.min1,\
                    startdate = stratStartDate,\
                    tilldate = stratEndDate)

    # add strategy parameters
    para = dict()
    para['Instrument'] = tradInstruments
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
    tradsession = ['09:15:00-12:00:00', '13:00:00-23:10:00'] 
    para['tradSession'] = tradsession
    para['tradSessionTimeZone'] = 'Asia/Hong_Kong'
    para['EPBroadcast'] = '192.168.0.47:33170'
    para['stratDataMQUrl']  = '192.168.0.47:33620'

    jcfg.addStrategyPara(key, para)
    
    # save config
    jcfg.save(filename)

    # check config
    # load system and strategy config
    #j2 = jsonConfig()
    #j2 = j2.load(filename)
    #
    ## load strategy config
    #cfgs = j2.getStratCfg()
    #for c in cfgs:
    #    # get parameter
    #    p = c.getParameters()
    #    pprint.pprint(p)

    ## get data sources
    #ds = j2.getDataSrc(key)
    #pprint.pprint(ds)
