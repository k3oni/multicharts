#!/usr/bin/python
# This is an example of configuring a paper trading strategy

from jsonconfig import jsonConfig
from feed.feed import dataType
from bar.bar import barLength 
import pprint

if __name__ == '__main__':
    jcfg = jsonConfig()
    filename = 'HI1_EP_paper.eva'

    # create strategy config
    account = 'delvin'
    strategy = 'EP'
    stratId = 2
    tradInstruments = ['HI1 Index']

    jcfg.addPaperTradingStrategy(account, strategy, stratId, tradInstruments)
    key = jcfg.getStrategyKey(account, strategy, stratId)

    jcfg.addDataSrc(key, instrument = 'HI1 Index', \
                    datatype = dataType.liveTickData.value)
    #jcfg.addDataSrc(key, instrument = 'HI1 Index', \
    #                datatype = dataType.liveBarData.value)

    # set strategy parameters
    para = dict()
    para['SMALength'] = 20
    para['EMALength'] = 6
    para['SDLength']= 20
    para['f1'] = 0.3
    para['f6'] = 0
    para['stochLength'] = 5
    para['smoothLen1'] = 8
    para['smoothLen2'] = 3
    para['BBLength'] = 20
    para['inSD'] = 2
    para['outSD'] = 3
    para['filterSD'] = 3
    para['levelDiffPercent'] = 0.0038
    para['levelRisk'] = 3
    para['gapRatio'] = 0.015
    para['levelRatio'] = 1.6
    para['constHr'] = 2
    para['constDay'] = 1
    para['tradSession'] = ['09:15:00-12:00:00', '13:00:00-23:10:00'] 
    para['tradSessionTimeZone'] = 'Asia/Hong_Kong'
    para['EPBroadcast'] = '192.168.0.47:33170'
    para['stratDataMQUrl']  = '192.168.0.47:33519'
    #para['stratCmdMQUrl']   = '192.168.0.47:33520'
    #para['DataMQUrl']       = '192.168.0.47:33521'
    #para['OmsMQUrl']        = '192.168.0.47:33522'

    jcfg.addStrategyPara(key, para)
    
    # save config
    jcfg.save(filename)

    # load system and strategy config
    #j2 = jsonConfig()
    #j2 = j2.load(filename)
   
    #pprint.pprint(j2.system)
 
    ## load all strategy config
    #cfgs = j2.getStratCfg()
    #for c in cfgs:
    #    # get parameter
    #    p = c.getParameters()
    #    pprint.pprint(p)
    #    c.getTradSession()

    ## get data sources
    #ds = j2.getDataSrc(key)

    ###########################################################################
    # HSI Paper Trading
    jcfg = jsonConfig()
    filename = 'HC1_EP_paper_tick.eva'

    # create strategy config
    account = 'delvin'
    strategy = 'EP'
    stratId = 2
    tradInstruments = ['HC1 Index']

    jcfg.addPaperTradingStrategy(account, strategy, stratId, tradInstruments)
    key = jcfg.getStrategyKey(account, strategy, stratId)

    jcfg.addDataSrc(key, instrument = 'HC1 Index', \
                    datatype = dataType.liveTickData.value)

    #jcfg.addDataSrc(key, instrument = 'HC1 Index', \
    #                datatype = dataType.liveBarData.value, \
    #                barlen = barLength.min3)

    # set strategy parameters
    para = dict()
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
    #para['stratCmdMQUrl']   = '192.168.0.47:33620'
    #para['DataMQUrl']       = '192.168.0.47:33621'
    #para['OmsMQUrl']        = '192.168.0.47:33622'

    jcfg.addStrategyPara(key, para)
    
    # save config
    jcfg.save(filename)
