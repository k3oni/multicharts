#!/usr/bin/python
################################################################################
from indicator.bollingerband import BollingerBand as BB
from indicator.ma import SMA, EMA
from indicator.mstd import movingStd
from indicator.stochastic import stochastic2
from tools.common import infor, err,  redirectToFile, cancelRedirectFile

class EP:

    def __init__(self, para):
        self.para = para
        self.state = dict()
        self.doTrade = True
        self.isExtremeDay = False
        self.epvalue = None
        self.leveldiff = None
        self.EPDone = False

    def computeEPandLevelDiff(self, dayopen, reportTS):
            self.dayopen = dayopen
            # level diff
            self.leveldiff = self.getLevelDiff(self.para['BBLength'], \
                                    self.daybarclose[1],\
                                    dayopen, \
                                    self.para['levelDiffPercent'],\
                                    self.para['levelDiffSeparator'],\
                                    self.para['levelScale'])

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
            
            self.report()

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
 
    def report(self):
        infor(' ')            
        infor('*' * 80)
        infor('Report')
        
        infor('Instrument %s' % self.para['Instrument'])
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
