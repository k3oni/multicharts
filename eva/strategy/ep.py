#!/usr/bin/python
################################################################################
from strategy import strategy
from tools.common import vipinfor, infor, err,  redirectToFile, cancelRedirectFile
from bar.bar import barField, barLength
from tools.timezonemap import timeZoneMap, datetimeTool
from datetime import datetime, timedelta
from feed.feed import dataType
from indicatorcontroller import indicatorController as ic
from indicator.bollingerband import BollingerBand as BB
from indicator.ma import SMA, EMA
from indicator.mstd import movingStd
from indicator.stochastic import stochastic2
from msg.msg import msgType
from tools.zmqwrapper import zmqWrapper, zmqType
from oms.oms import oms
from tools.bbg2IB import toIBContract
from oms.order import OrderType
from strategymode import strategyMode
from msg.msg import msgType

class EP(strategy):

    def __init__(self, engine, config):
        strategy.__init__(self, engine, config)
        self.para = self.getConfig().getParameters()
        self.doTrade = True
        self.epvalue = 0
        self.leveldiff = 10000
        self.isExtremeDay = False
        self.EPDataReady = True
        if self.getConfig().getMode() == strategyMode.paperTrading: 
            self.getBinder().bindPub(config.para['EPBroadcast'])
        self.ti = self.getConfig().getTradeInstruments()
        self.doTradeOnce = True
        
    def onStrategyInit(self):
        strategy.onStrategyInit(self)

    def onSessionInit(self, sessionStart, sessionEnd):
        strategy.onSessionInit(self, sessionStart, sessionEnd)        
        self.EPDone = False
        if True: #sessionStart.hour == 9:
            # initialize at day open
            self.doTrade = True
            self.state = dict()
            self.isExtremeDay = False

            instr  = self.getConfig().tradInstruments[0]
            start  = sessionStart + timedelta(days = -50) 
            end    = sessionStart + timedelta(days = -1)

            statusHr, self.hrbar  = self.barCtrl.getBlockData(instr, barLength.hourly, \
                              dataType.historicalBarData, start, end, [barField.open,\
                              barField.high, barField.low, barField.close])

            statusDay, self.daybar  = self.barCtrl.getBlockData(instr, barLength.daily, \
                               dataType.historicalBarData, start, end, [barField.open,\
                               barField.high, barField.low, barField.close])

            statusDC, self.daybarclose = self.barCtrl.getBlockData(instr, barLength.daily,\
                                    dataType.historicalBarData, start, end, \
                                    [barField.close])

            if statusHr == False or statusDay == False or statusDC == False:             
                raise Exception('Problem with daily data used by EP.')        

            self.EPDone = False
            today = sessionStart

            self.eptime = today.replace(hour=9, minute=15)
            self.epstop = self.eptime + timedelta(minutes=10)
            
            contract = self.barCtrl.dbs.getActiveContract(instr, today)
            self.contractIB = toIBContract(contract)

            #if instr == 'HC1 Index':
            #    self.computeEPandLevelDiff(10136, datetime.now())
            #    self.broadcast(datetime.now())
            #    self.oms.sendOrder()

            #elif instr == 'HI1 Index':
            #    self.computeEPandLevelDiff(22316, datetime.now())
            #    self.broadcast(datetime.now())
            #    self.oms.sendOrder()

    def onMsg(self, msg):
        strategy.onMsg(self, msg)

        if self.EPDone == False:
            reportTS = []
            if  msg.msgtype == msgType.barmsg and \
                msg.getBarStartTime() >= self.eptime and \
                msg.getContract() == self.contractIB: 

                infor("Datetime to compute EP: %s" % msg.getBarStartTime()) 
                self.EPDone = True
                reportTS = msg.getBarStartTime()
                self.computeEPandLevelDiff(msg.open, reportTS)

            if msg.msgtype == msgType.tickmsg and \
                msg.getTS() >= self.eptime and\
                msg.getContract() == self.contractIB and\
                msg.isTradePrice():
                
                infor("Datetime to compute EP: %s" % msg.getTS())
                reportTS = msg.getTS() 
                self.EPDone = True
                self.computeEPandLevelDiff(float(msg.getContent()), reportTS)

            if self.EPDone and self.getConfig().getMode() == strategyMode.paperTrading:
                self.broadcast(reportTS)

        #if self.doTradeOnce:
        #    self.getOMS().buy(self.ti[0], OrderType.market, 1, 0)
        #    vipinfor('Send market order buy.')
        #    self.getOMS().shortSell(self.ti[0], OrderType.limit, 2, 10030)
        #    vipinfor('Send limit order shortsell.')
        #    self.doTradeOnce = False

        if msg.msgtype == msgType.omsmsg:
            msg.order.display()

    def computeEPandLevelDiff(self, dayopen, reportTS):
            self.dayopen = dayopen
            # level diff
            self.leveldiff = self.getLevelDiff(self.para['BBLength'], \
                                    self.daybarclose[1],\
                                    dayopen, \
                                    self.para['levelDiffPercent'],\
                                    [1, 1.25, 1.5, 1.75, 2],\
                                    [1, 1, 1, 1, 1, 1.8])

            BBU2 = BB(self.para['BBLength'], 2)
            BBD2 = BB(self.para['BBLength'], -2)
            up2std = BBU2.getInitBB(self.daybar[4])
            down2std = BBD2.getInitBB(self.daybar[4])
 
            preDayHigh = self.daybar[2][-1]
            preDayLow  = self.daybar[3][-1]
            self.state['PreDayHigh'] = preDayHigh
            self.state['PreDayLow'] = preDayLow                

            # gap open in extreme days 
            if dayopen <= down2std or dayopen >= up2std:
 
                if dayopen - preDayHigh > preDayHigh * self.para['gapRatio']:
                    self.doTrade = False
                    self.isExtremeDay = True

                if preDayLow - dayopen > preDayLow * self.para['gapRatio']:
                    self.doTrade = False
                    self.isExtremeDay = True

            # extreme days
            if dayopen <= down2std or dayopen >= up2std:
                self.epvalue = self.epFormulaExtreme(self.para['BBLength'], dayopen)
                self.isExtremeDay = True

            # normal days
            if down2std < dayopen and dayopen < up2std:
                self.epvalue = self.epFormulaNormal(dayopen, self.leveldiff)
            
            
            statefile = "{name}.{ts}.state".format(name=self.getConfig().getStrategyName(),\
                                                    ts=reportTS)
            self.report()

    def report(self):
        infor(' ')            
        infor('*' * 80)
        infor('Report')
        
        infor('Instrument %s' % self.getConfig().tradInstruments[0])
        infor('Trading status : %s' % ('Trade' if self.doTrade else 'No Trade'))
        infor('Extreme Day : %s' % ('Yes' if self.isExtremeDay else 'No'))
        infor('EP : %s, LevelDiff : %s' % (self.epvalue, self.leveldiff))
        infor('Day Open %s' % self.dayopen)
        infor(' ')
        infor('Level Ratio %s' % self.state['levelRatio'])        
        infor('PreDayHigh %s' % self.state['PreDayHigh'])
        infor('PreDayLow %s' % self.state['PreDayLow'])
        infor(' ')
        if not self.isExtremeDay:
            infor('SMA %s' % self.state['sma'])
            infor('SMALength %s' % self.para['SMALength'])
            infor('EMA %s' % self.state['ema'])
            infor('EMALength %s' % self.para['EMALength'])
            infor('Mean %s' % self.state['mean'])
            infor('')
            infor('SDLength %s' % self.para['SDLength'])
            infor('StochLength %s' % self.para['stochLength'])
            infor('SmoothLen1 %s' % self.para['smoothLen1'])
            infor('SmoothLen2 %s' % self.para['smoothLen2'])
            infor('')
            infor('SDDay %s' % self.state['sdDay'])
            infor('constDay %s' % self.para['constDay'])
            infor('FactorDay %s' % self.state['factorDay'])

            infor('SDHr %s' % self.state['sdHr'])
            infor('constHr %s' % self.para['constHr'])
            infor('FactorHr %s' % self.state['factorHr'])

            infor('SlowKHr %s' % self.state['curSlowKHr'])
            infor('SlowDHr %s' % self.state['curSlowDHr'])
            infor('preSlowKHr %s' % self.state['preSlowKHr'])
            infor('preSlowDHr %s' % self.state['preSlowDHr'])
            infor('SlowKDay %s' % self.state['curSlowKDay'])
            infor('SlowDDay %s' % self.state['curSlowDDay'])
            infor('preSlowKDay %s' % self.state['preSlowKDay'])
            infor('preSlowDDay %s' % self.state['preSlowDDay'])
            infor('EP_prebound %s' % self.state['ep_prebound'])
            infor('EP %s' % self.epvalue)
        else:
            infor('Up2Std %s' %  self.state['up2std'])
            infor('Up3Std %s' %  self.state['up3std'])
            infor('Down2Std %s' %  self.state['down2std'])
            infor('Down3Std %s' %  self.state['down3std'])
            infor('BBLength %s' % self.para['BBLength'])

        infor('*' * 80)
        infor(' ')            

    def getLevelDiff(self, bbl, dayclose, open, leveldiffPercent, \
                        seperator, levelratiomap):
        # compute ratio
        if len(seperator) <> len(levelratiomap)-1:
            err("Inconsist level ratio map.")
            return

        stdup = []
        stddown = []
        for s in seperator:
            BBU = BB(bbl, s)
            BBD = BB(bbl, -s)
            stdup.append(BBU.getInitBB(dayclose))
            stddown.append(BBD.getInitBB(dayclose))
    
        levels = sorted(stddown) + sorted(stdup)
        rev = list(reversed(levelratiomap))
        ratios = rev[0:len(rev)-1]+ levelratiomap
        count = 0

        if open > levels[0]:
            for i in range(0, len(levels)-1):
                if  levels[i] <= open and open < levels[i+1]:
                    count = i+1
                    break
        levelRatio = ratios[count]

        # keep record of states
        self.state['levels'] = levels
        self.state['levelRatio'] = levelRatio

        return open * leveldiffPercent *  levelRatio

    def epFormulaExtreme(self, bbl, dayopen):
        BBU2 = BB(bbl, 2)
        BBD2 = BB(bbl, -2)
        dayclose = self.daybar[4][-self.para['BBLength']:]

        up2std = BBU2.getInitBB(dayclose)
        down2std = BBD2.getInitBB(dayclose)

        BBU3 = BB(bbl, 3)
        BBD3 = BB(bbl, -3)
        up3std = BBU3.getInitBB(dayclose)
        down3std = BBD3.getInitBB(dayclose)

        # keep record of states
        self.state['up2std'] = up2std
        self.state['up3std'] = up3std
        self.state['down2std'] = down2std
        self.state['down3std'] = down3std

        if dayopen < down2std:
            return (down2std + down3std)/2

        if dayopen > up2std:
            return (up2std + up3std)/2 

    def epFormulaNormal(self, dayopen, leveldiff):
        # mean

        sma = SMA(self.para['SMALength'])
        ema = EMA(self.para['EMALength'])
        daybarWithOpen = self.daybar[4][-max(self.para['SMALength'], self.para['EMALength']):]
        daybarWithOpen[-1] = dayopen
        smaval = sma.initSMA(daybarWithOpen[-self.para['SMALength']:])
        emaval = ema.initEMA(daybarWithOpen[-self.para['EMALength']:])
        mean = (smaval + emaval)/2

        # stochastic
        factorHr, self.state['curSlowKHr'], self.state['curSlowDHr'], \
        self.state['preSlowKHr'], self.state['preSlowDHr']\
                      = self.EPDirection(dayopen, self.hrbar[2], \
                        self.hrbar[3], self.hrbar[4],\
                        self.para['SDLength'], self.para['f1'], \
                        self.para['f6'], self.para['constHr'], \
                        self.para['stochLength'], self.para['smoothLen1'],\
                        self.para['smoothLen2'])

        factorDay, self.state['curSlowKDay'], self.state['curSlowDDay'], \
        self.state['preSlowKDay'], self.state['preSlowDDay']\
                      = self.EPDirection(dayopen, self.daybar[2],\
                        self.daybar[3], self.daybar[4],\
                        self.para['SDLength'], self.para['f1'], \
                        self.para['f6'], self.para['constDay'], \
                        self.para['stochLength'], self.para['smoothLen1'],\
                        self.para['smoothLen2'])
       
        mstdHr = movingStd(self.para['SDLength'])
        hrbarWithOpen = self.hrbar[4][-self.para['SDLength']:]
        hrbarWithOpen[-1] = dayopen
        sdHr = mstdHr.initMovingStd(hrbarWithOpen)

        mstdDay = movingStd(self.para['SDLength'])
        sdbarWithOpen = self.daybar[4][-self.para['SDLength']:]
        sdbarWithOpen[-1] = dayopen
        sdDay = mstdDay.initMovingStd(sdbarWithOpen)

        ep_prebound = mean + sdDay * self.para['constDay'] * factorDay +\
                        sdHr * self.para['constHr'] * factorHr
        
        ep = ep_prebound

        if ep > dayopen + leveldiff * self.para['levelRisk']:
            ep = dayopen + leveldiff * self.para['levelRisk']

        if ep < dayopen - leveldiff * self.para['levelRisk']:
            ep = dayopen - leveldiff * self.para['levelRisk']

        self.state['sma'] = smaval
        self.state['ema'] = emaval
        self.state['mean'] = mean
        self.state['factorHr'] = factorHr
        self.state['factorDay'] = factorDay
        self.state['sdHr'] = sdHr
        self.state['sdDay'] = sdDay
        self.state['ep_prebound'] = ep_prebound
     
        return ep

    def EPDirection(self, currentOpen, preHigh, preLow, preClose, sdLength, \
                    f1, f6, const, stochLength, smoothLen1, smoothLen2):

        # standard deviation with openning price
        barWithOpen = preClose[-sdLength:]

        mstd = movingStd(sdLength)
        sd = mstd.initMovingStd(barWithOpen)

        stc = stochastic2(stochLength, smoothLen1, smoothLen2) 
        fastKs, fastDs, slowKs, slowDs = stc.initData(preHigh, preLow, preClose)

        curFastK = fastKs[-1]
        preFastK = fastKs[-2]

        curFastD = fastDs[-1]
        preFastD = fastDs[-2]

        curSlowK = slowKs[-1]
        preSlowK = slowKs[-2]

        curSlowD = slowDs[-1]
        preSlowD = slowDs[-2]

        slowKAbove80 = curSlowK > 80
        slowKBelow20 = curSlowK < 20
        slowKBetween2080 = curSlowK >= 20 and curSlowK <= 80
        
        slowKAboveSlowD = curSlowK >= curSlowD
        slowKBelowSlowD = curSlowK < curSlowD
        
        slowKIncreasing = curSlowK >= preSlowK
        slowKDecreasing = curSlowK < preSlowK
        
        factor = 0

        if slowKAbove80:
            factor = f1

        if slowKBelow20:
            factor = -f1

        if slowKBetween2080:
            if slowKAboveSlowD:
                if slowKIncreasing:
                    factor = f1
                else:
                    factor = f6

            if slowKBelowSlowD:
                if slowKDecreasing:
                    factor = -f1
                else:
                    factor = -f6

        return factor, curSlowK, curSlowD, preSlowK, preSlowD
            
    def broadcast(self, ts):
        instr  =  "# Instrument: %s\n" % self.getConfig().tradInstruments[0] 
        msg =   "# EP file \n\n" +\
                instr +\
                "# Update time: \n" +\
                "#   Daily after market open + 1 min\n\n" +\
                "# General:\n" +\
                "#   VERSION=<Version name>\n" +\
                "#   LAST_UPDATE=<1yyMMdd.00, hmm.00>\n\n"+\
                "#Extrem Day Gap Open Format:\n" +\
                "#  DO_TRADE=<YES/NO>\n" +\
                "#  EP=<number>\n" +\
                "#  Interval= <number>\n" +\
                "#\n" +\
                "VERSION=2\n" +\
                "LAST_UPDATE=%s\n" % ts + \
                "DO_TRADE=%s\n" % ("YES" if self.doTrade else "NO") +\
                "EP=%d\n" % self.epvalue +\
                "Interval= %d\n" % self.leveldiff 

        self.getBinder().getPub().send_string(msg)

             
        
