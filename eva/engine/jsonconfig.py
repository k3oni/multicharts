#!/usr/bin/python
################################################################################

import json, pprint, feed.feed, pytz, bar.bar as bar
from json import JSONEncoder, JSONDecoder
from tools.timezonemap import timeZoneMap as tzm
from strategy.strategymode import strategyMode
from datetime import datetime
from tools.common import infor

class configEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, jsonConfig):
            if '__type__' not in obj.__dict__.keys():
                obj.__dict__['__type__'] = 'jsonConfig'
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self, obj)

class configDecoder(JSONDecoder):
    def __init__(self, encoding='utf-8'):
        JSONDecoder.__init__(self, object_hook=self.dict_to_obj)

    def dict_to_obj(self, obj):
        if '__type__' in obj and obj['__type__'] == 'jsonConfig':
            inst = jsonConfig()
            inst.__dict__['system'] = obj['system']
            inst.__dict__['strats'] = obj['strats']
            inst.__dict__['datasrc'] = obj['datasrc']
            return inst
        return obj

class jsonConfig:
    def __init__(self):
        system = dict() 
        system['timezone'] = 'Asia/Hong_Kong'
        system['EvaDataPath'] = '/home/share/h5'
        system['EvaBarUrl'] = '192.168.0.45:20132' 
        system['EvaTickUrl'] = '192.168.0.45:20131'

        EvaBarLen = dict()
        EvaBarLen['60'] = '1m'
        EvaBarLen['3600'] = '1h'
        system['EvaBarLen'] = EvaBarLen

        system['dbname'] = 'delvin'
        system['dbuser'] = 'delvin'
        system['dbpasswd'] = 'delvin123'
        system['dbip'] = '192.168.0.47'
        system['dbport'] = 409684

        system['BBGServer'] = '192.168.0.216'
        system['BBGPort'] = 9090

        system['LogPath'] = '/home/delvin/code/python/eva/engine/log/'
        system['dataServerUrl'] = '192.168.0.47:409616'
        system['dataServerIP'] = '192.168.0.47'
        system['dataServerPub'] = '409617'
        system['OMSUrl'] = '192.168.0.110:5678'

        self.system = system
        self.strats = dict()
        self.datasrc = []

    def getSystemConfig(self):
        return self.system

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self, f, cls=configEncoder, indent=2)
            f.close()

    def load(self, filename):
        with open(filename, 'r') as f:
            inst = json.load(f,  cls=configDecoder)
            f.close()
            return inst

    def display(self):
        print(json.dumps(self, cls=configEncoder, indent=2, sort_keys=True))

    ###########################################################################
    #   strategy config
    def getStrategyKey(self, accountname, strategyname, strateId):
        return '%s_%s_%s' %(accountname, strategyname, strateId)

    #def addStrategy(self, accountname, strategyname, strateId, tradInstruments,\
    #                    start, starttimezone, end, endtimezone, mode):
    #    # a unique key
    #    key = self.getStrategyKey(accountname, strategyname, strateId)
    #    strat = dict()
    #    strat['strategyname'] = strategyname
    #    strat['accoutname'] = accountname
    #    strat['stratId'] = stratId
    #    strat['tradInstruments'] = tradInstruments
    #    strat['start'] = start
    #    strat['starttz'] = starttimezone
    #    strat['end'] = end
    #    strat['endtz'] = endtimezone
    #    strat['mode'] = mode
    #    self.strats[key] = strat

    def getStratCfg(self):
        cfgs = []
        for k in self.strats.keys():
            cfgs.append(stratConfig(self.strats[k]))
        return cfgs

    def addPaperTradingStrategy(self, accountname, strategyname, stratId,\
                                tradInstruments):
        key = self.getStrategyKey(accountname, strategyname, stratId)
        strat = dict()
        strat['strategyname'] = strategyname
        strat['accoutname'] = accountname
        strat['stratId'] = stratId
        strat['tradInstruments'] = tradInstruments
        strat['mode'] = strategyMode.paperTrading.name
        self.strats[key] = strat

    def addBacktestStrategy(self, accountname, strategyname, stratId, tradInstruments,\
                        start, starttimezone, end, endtimezone):
        key = self.getStrategyKey(accountname, strategyname, stratId)
        strat = dict()
        strat['strategyname'] = strategyname
        strat['accoutname'] = accountname
        strat['stratId'] = stratId
        strat['tradInstruments'] = tradInstruments
        strat['start'] = start
        strat['starttz'] = starttimezone
        strat['end'] = end
        strat['endtz'] = endtimezone
        strat['mode'] = strategyMode.backtest.name
        self.strats[key] = strat

    def addLiveTradingStrategy():
        key = self.getStrategyKey(accountname, strategyname, stratId)
        strat = dict()
        strat['strategyname'] = strategyname
        strat['accoutname'] = accountname
        strat['stratId'] = stratId
        strat['tradInstruments'] = tradInstruments
        strat['mode'] = strategyMode.liveTrading.name
        self.strats[key] = strat

    def addStrategyField(self, key, name, value):
        self.strats[key][name] = value    

    def appendStrategyField(self, key, name, value):
        if name not in self.strats[key].keys():
            self.strats[key][name] = []
        self.strats[key][name].append(value)


    ###########################################################################
    # specific fields
    def addStrategyPara(self, strategykey, value):
        self.addStrategyField(strategykey, 'para', value)

    def addStrategyViewer(self, strategykey, value):
        self.addStrategyField(strategykey, 'viewer', value)

    def addStrategyPostTrade(self, strategykey, value):
        self.addStrategyField(strategykey, 'posttrade', value)

    def addStrategyAccount(self, strategykey, value):
        self.addStrategyField(strategykey, 'account', value)

    ###########################################################################
    # data source config
    def addDataSrc(self, stratkey, **kwargs):
        src = dict()
        for key, value in kwargs.items():
            src[key] = value
        self.appendStrategyField(stratkey, 'data', src)

    def getDataSrc(self, stratkey):
        ds = self.strats[stratkey]['data'] 
        return ds

            

class stratConfig:

    def __init__(self, content = None):
        if content <> None:
            self.__dict__ = content
    
    def getStrategyName(self):
        return self.strategyname

    def getAccount(self):
        return self.accountname

    def getStratId(self):
        return self.stratId

    def getDataSources(self):
        dss = []
        for d in self.data:
            dss.append(DataSource.createFromDict(d))
        return dss

    def getDataSource(self, instru, barlen):
        for d in self.data:
            ds = DataSource.createFromDict(d)
            if ds.getInstrument() == instru and ds.getBarLength() == barlen:
                return ds
        return None 

    def getStartDate(self):
        return tzm.datestr2Date(self.start, self.starttz) 

    def getEndDate(self):
        return tzm.datestr2Date(self.end, self.endtz) 

    def getParameters(self):
        return self.para

    def getMode(self):
        return strategyMode[self.mode]

    def getTradeInstruments(self):
        return self.tradInstruments        

    def getTradSession(self):
        field = 'tradSession'
        fieldTZ = 'tradSessionTimeZone'
        if field in self.para.keys() and fieldTZ in self.para.keys():
            session = []
            ss = self.para[field]
            tz = self.para[fieldTZ]
            localtz = pytz.timezone(tz)
            for s in ss:
                beg, end = s.split('-')
                b = datetime.strptime(beg, '%H:%M:%S')
                b = localtz.localize(b)        
                e = datetime.strptime(end, '%H:%M:%S')
                e = localtz.localize(e)
                session.append((b, e))
            return session        
        else:
            return None

    def displayDataSource(self, ds):
        print('#'*80)
        print('Data Source')
        for s in ds:
           pprint.pprint(s) 
 
    def display(self):
        print('#'*80)
        print('Strategy Configuration')
        pprint.pprint(vars(self))         

class DataSource:
    def __init__(self):
        pass

    @staticmethod
    def createFromField(instrument, expireYear, expireMonth, typecode, \
                    datatype, barlength, startdate, tilldate):
        self = DataSource()        
        self.instrument = instrument 
        self.expireYear = expireYear
        self.expireMonth = expireMonth
        self.typecode = typecode
        self.datatype = datatype
        self.barlen = barlength
        self.startdate = startdate
        self.tilldate = tilldate
        return self

    @staticmethod
    def createFromDict(content=None):
        self = DataSource()
        if content <> None:
            self.__dict__ = content
        return self

    def display(self):
        print('#'*80)
        print('Strategy Data Source')
        pprint.pprint(vars(self))

    def getId(self):
        return '{instru}-{barlen}'.format(instru=self.instrument, barlen=self.barlen)

    def getInstrument(self):
        return self.instrument

    def getTypeCode(self):
        return self.typecode
   
    def getDataType(self):
        return feed.feed.dataType(self.datatype)

    def getBarLength(self):
        return bar.barLength(self.barlen)

    def getStartDate(self):
        return self.startdate

    def getTillDate(self):
        return self.tilldate

    def getExpireYear(self):
        return self.expireYear

    def getExpireMonth(self):
        return self.expireMonth

if __name__ == '__main__':
    jcfg = jsonConfig()
    filename = 'ep4.eva'

    # create strategy config
    account = 'delvin'
    strategy = 'EP'
    stratId = 1
    stratStartDate = '2015-10-01'
    stratStartTZ = 'Asia/Hong_Kong'
    stratEndDate = '2015-11-16'
    stratEndTZ = 'Asia/Hong_Kong'
    tradInstruments = ['HC1 Index']
    mode = strategyMode.backtest.name

    jcfg.addStrategy(account, strategy, stratId, tradInstruments, stratStartDate, \
                        stratStartTZ, stratEndDate, stratEndTZ, mode)

    key = jcfg.getStrategyKey(account, strategy, stratId)

#    jcfg.addDataSrc(key, instrument = 'HC1 Index', \
#                    datatype = dataType.liveTickData.value)
#
#    jcfg.addDataSrc(key, instrument = 'HI1 Index', \
#                    datatype = dataType.liveBarData.value,\
#                    barlen  = bl.min1.value)

    jcfg.addDataSrc(key, instrument = 'HC1 Index', \
                    datatype = dataType.historicalBarData.value,\
                    barlen  = bar.barLength.min1.value,\
                    startdate = stratStartDate,\
                    tilldate = stratEndDate)

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

    jcfg.addStrategyPara(key, para)
    
    # save config
    jcfg.save(filename)

    # load system and strategy config
    j2 = jsonConfig()
    j2 = j2.load(filename)
    
    # load all strategy config
    cfgs = j2.getStratCfg()
    for c in cfgs:
        # get parameter
        p = c.getParameters()
        pprint.pprint(p)
        c.getTradSession()

    # get data sources
    ds = j2.getDataSrc(key)
