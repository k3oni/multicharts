#!/usr/bin/python
###############################################################################
# This script is to analysis bollinger band sar effectiveness

import csv
from indicator.bollingerband import BollingerBand
from pprint import pprint
from tools.common import vipinfor, infor
from view import view

class dayInfor:
    def __init__(self, d, open, close, sar, spread):
        self.d = d
        self.op = open
        self.cl = close
        self.sar = sar
        self.spread = spread

    def display(self):
        print('{d}: open {op}, close {cl}, diff {diff}, spread {spread}, sar {sar}'.\
            format(d=self.d, op = self.op, cl = self.cl, diff = self.cl-self.op,\
                spread=self.spread, sar=self.sar))
class SAR:
    def __init__(self):
        pass

    def run(self, filename, BBLength, sdList):
        self.loadDayBar(filename)
        if  isinstance(BBLength, int):
            BBCloseMap = self.genBBCloseMap(self.d, self.o, self.c, BBLength, sdList)
            firstTouchDays = self.SARFirstTouch(self.d, self.o, self.h, self.l, self.c, self.BBCloseMap, 'crossLine') 
        elif len(BBLength) > 1:
            BBOpenRegionMap = self.genBBOpenRegion(self.d, self.o, self.c, BBLength, sdList)
            #self.BBCloseRegionMap = self.genBBCloseRegion(self.d, self.o, self.c, BBLength, sdList)
            firstTouchDays = self.SARFirstTouch(self.d, self.o, self.h, self.l, self.c, self.BBOpenRegionMap, 'touchRegion') 

    def loadDayBar(self, filename):
        self.d = []
        self.o = []
        self.h = []
        self.l = []
        self.c = []

        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for r in reader:
                data = map(float, r)
                self.d.append(data[0])
                self.o.append(data[1])
                self.h.append(data[2])
                self.l.append(data[3])
                self.c.append(data[4])
        
    def getOpen(self, date):
        return self.o[self.d.index(date)]

    def getHigh(self, date):
        return self.h[self.d.index(date)]

    def getLow(self, date):
        return self.l[self.d.index(date)]

    def getClose(self, date):
        return self.c[self.d.index(date)]

    def getBBWithOpen(self, date, open, close, BBLength, sd):
        BB = BollingerBand(BBLength, sd)
        BBopen = dict()
    
        for i in range(BBLength-1, len(date)-1):
            sampleWithOpen = close[i-(BBLength-1):i+1]
            sampleWithOpen.append(open[i+1]) 
            v1 = BB.getInitBB(sampleWithOpen) 
            BBopen[date[i+1]] = v1
        
        return BBopen
    # generate BB using close for a list of days 
    def getBBWithClose(self, date, open, close, BBLength, sd):
        BB = BollingerBand(BBLength, sd)
        BBclose = dict()

        for i in range(BBLength, len(date)):
            sampleWithClose = close[i-BBLength:i]
            v2 = BB.getInitBB(sampleWithClose) 
            BBclose[date[i]] = v2
        return BBclose

    def genSARMap(self):
        pass

    def genBBCloseMap(self, date, open, close, BBLength, sdList):
        BBCloseMap = dict()
        for sd in sdList:
            BBClose = self.getBBWithClose(date, open, close, BBLength, sd)
            BBCloseMap[sd] = BBClose
        return BBCloseMap

    def genBBOpenMap(self, date, open, close, BBLength, sdList):
        BBOpenMap = dict()
        for sd in sdList:
            BBOpen = self.getBBWithOpen(date, open, close, BBLength, sd)
            BBOpenMap[sd] = BBOpen
        return BBOpenMap
    
    def genBBCloseRegion(self, date, open, close, BBLengths, sdList):
        BBCloseRegion = dict()
        for sd in sdList:
            bblist = dict()
            for bl in BBLengths:
                bb = self.getBBWithClose(date, open, close, bl, sd)
                bblist[bl] = bb

            BBCloseRegion[sd] = dict()
            for d in date:
                tmp = []
                for bl in BBLengths:
                    if d in bblist[bl].keys():
                        tmp.append(bblist[bl][d])
                if len(tmp) == len(BBLengths):
                    BBCloseRegion[sd][d] = [min(tmp), max(tmp)]
        return BBCloseRegion

    def genBBOpenRegion(self, date, open, close, BBLengths, sdList):
        BBOpenRegion = dict()
        for sd in sdList:
            bblist = dict()
            for bl in BBLengths:
                bb = self.getBBWithOpen(date, open, close, bl, sd)
                bblist[bl] = bb

            BBOpenRegion[sd] = dict()
            for d in date:
                tmp = []
                for bl in BBLengths:
                    if d in bblist[bl].keys():
                        tmp.append(bblist[bl][d])
                if len(tmp) == len(BBLengths):
                    BBOpenRegion[sd][d] = [min(tmp), max(tmp)]
        return BBOpenRegion

    ############################################################################
    # First touch of SAR
    def SARFirstTouch(self, date, open, high, low, close, sarMap, methodname):
        touchDayLabel = self.checkTouchDate(sarMap, date, open, high, low, \
                                                close, methodname)
        touchDays = self.getTouchDays(touchDayLabel)        
        firstTouchDays = self.genFirstTouchDays(touchDays) 
        category = self.categorize(self.firstTouchDays)
        self.statisticOnCategory(category, sarMap, methodname)
        return firstTouchDays

    def categorize(self, touchDays):
        sample =  touchDays[touchDays.keys()[0]]
        subs = [{d:l} for d in touchDays.keys() for l in touchDays[d].keys()\
                             if touchDays[d][l] == 1]
        category = dict((u, v) for u in sample.keys() for v in \
                    [dict((d, l) for sub in subs for (d, l) in sub.items() if l==u)])
        return category

    # statistics
    def statMethod(self, methodname):
        if methodname == 'crossLine':

            def crossLineStat(category, sarMap):
                for level in sorted(category.keys()):
                    datelist = category[level]
                    counter = 0.0
                    for d in sorted(datelist.keys()):
                        sar = sarMap[level][d]
                        open = self.getOpen(d)
                        close = self.getClose(d)
                        if (open-sar)*(close-sar) >= 0:
                            print('level %s date %s is SARed with open %s close %s sar %s' \
                                    % (level, d, open, close, sar))
                            counter = counter + 1
                        else:
                            print('level %s date %s is not SARed with open %s close %s sar %s' \
                                    % (level, d, open, close, sar))

                    print('For level %s %s of %s (%s) are SARed .' % \
                            (level, counter, len(datelist), counter/len(datelist)))
                    print('')

            return crossLineStat
        elif methodname == 'touchRegion':
            def touchRegionStat(category, sarMap):
                for level in sorted(category.keys()):
                    datelist = category[level]
                    counter = 0.0
                    for d in sorted(datelist.keys()):
                        region = sarMap[level][d]
                        regionDown = region[0]
                        regionUp = region[1]
                        open = self.getOpen(d)
                        close = self.getClose(d)

                        if open <= regionUp and close <= regionUp:
                            print('level %s date %s is SARed with open %s close %s by regionUp %s' \
                                    % (level, d, open, close, regionUp))
                            counter = counter + 1
                        elif open >= regionDown and close >= regionDown:
                            print('level %s date %s is SARed with open %s close %s by regionDown %s' \
                                    % (level, d, open, close, regionUp))
                            counter = counter + 1
                        else:
                            print('level %s date %s is not SARed with open %s close %s regionUp %s regionDown %s' \
                                    % (level, d, open, close, regionUp, regionDown))

                    print('For level %s %s of %s (%s) are SARed .' % \
                            (level, counter, len(datelist), counter/len(datelist)))
                    print('')
            return touchRegionStat
        else:
            print('Unsupport method name.')
            return None 


    def statisticOnCategory(self, category, sarMap, methodname):
        statmethod = self.statMethod(methodname)
        statmethod(category, sarMap)

    def genFirstTouchDays(self, touchDays):
        firstTouch = dict()
        orderedDate = sorted(touchDays.keys())
        for index in range(1, len(orderedDate)):
            yest = orderedDate[index-1]
            today = orderedDate[index]
            if self.isFirstTouch(touchDays[yest], touchDays[today]):
                firstTouch[today] = touchDays[today]        
        return firstTouch

    def labelMethod(self, methodName):
        if methodName == 'crossLine':
            def crossLine(op, hi, lo, cl, sarline):
                return hi >= sarline and lo <= sarline
            return crossLine
        elif methodName == 'touchRegion':
            def touchRegion(op, hi, lo, cl, sarRegion):
                regionUp = sarRegion[1]
                regionDown = sarRegion[0]
                if op >= regionUp:
                    return lo < regionUp
                if op <= regionDown:
                    return hi > regionDown
            return touchRegion
        else:
            print('Unsupport method %s.' % methodName)
            return None
        
    def checkTouchDate(self, sarMap, date, open, high, low, close, methodname):    
        checkMethod = self.labelMethod(methodname)
        if checkMethod == None:
            return None

        label = dict()
        for i in date:
            label[i] = dict()
        startdate = min(sarMap[sarMap.keys()[0]])

        for i in range(0, len(date)):
            d = date[i]

            if d < startdate:
                label[d] = dict()
                for level in sarMap.keys():
                    label[d][level] = 0
                continue

            op = open[i]
            hi = high[i]
            lo = low[i]
            cl = close[i]
            
            label[d] = dict()
            for level in sarMap.keys():
                if checkMethod(op, hi, lo, cl, sarMap[level][d]):
                    label[d][level] = 1
                else:
                    label[d][level] = 0
        return label

    def getTouchDays(self, checkDays):
        return dict((k, v) for k, v in checkDays.items() if any(v[x] for x in v))
     
    def isFirstTouch(self, lastTouch, thisTouch):
        for i in thisTouch.keys():
            if thisTouch[i] <> 0:
                noPreviousTouch = lastTouch[i] == 0
                if not noPreviousTouch:
                    continue
                existOtherTouch = any(v for k, v in lastTouch.items() if k <> i)
                if noPreviousTouch and existOtherTouch:
                    return True

    
    def displayDict(self, dic):
        for k in sorted(dic.keys()):
            infor('{k} : {v}'.format(k=k, v=dic[k]))    

    def displayDict2D(self, dic2):
        print('*'*80)
        for k in sorted(dic2.keys()):
            ls = '%s :: ' % k
            for l in sorted(dic2[k].keys()):
                ls = ls + '{l}:{v}'.format(l=l, v=dic2[k][l]) + '\t'
            print(ls)
        print('*'*80)
    
    def displayFirstTouch(self, firstTouch, label):
        def sarString(dic):
            s = ""
            for k in sorted(dic.keys()):
                s = s + '%s : %s\t' % (k, dic[k])
            return s

        for d in sorted(label.keys()):
            if d in firstTouch.keys():
                vipinfor('date {d} : {c}'.format(d=d, c=sarString(firstTouch[d])))
                continue
            else:
                infor('date {d} : {c}'.format(d=d, c=sarString(label[d])))
   
    ###########################################################################
    # measure sar hardness
    def sarHardness(self, plist):
        if len(plist) == 0:
            return

        hardness = 0.0
        softness = 0.0

        for p in plist:
            if (p.op - p.sar) * (p.cl - p.sar) >= 0:
                hardness = hardness + 1
            else:
                softness = softness + 1
    
        print('Hardness %f softness %f' % (hardness, softness))
        hardness = hardness / len(plist)
        softness = softness / len(plist)
        print('Hardness %f softness %f' % (hardness, softness))

    def SAREffective(self, date, open, close, sarMap, spread):
        outUp   = sarMap[3]
        inUp    = sarMap[2]
        mid     = sarMap[0]
        inDown  = sarMap[-2]
        outDown = sarMap[-3]
        
        desp = ['out of 3 std', \
                'below close to 3 std',\
                'above close to 2 std',\
                'below close to 2 std',\
                'above close to mid',\
                'below close to mid',\
                'above close to -2 std',\
                'below close to -2 std',\
                'above close to -3 std',\
                'out of -3 std']

        ptable = dict()
        for i in range(0, 10):
            ptable[i] = []

        startdate = max(min(outUp.keys()), \
                        min(inUp.keys()), \
                        min(mid.keys()),\
                        min(inDown.keys()),\
                        min(outDown.keys()))

        for i in range(0, len(date)):
            d = date[i]

            if d < startdate:
                continue

            op = open[i]
            cl = close[i]
            if op >= outUp[d]:
                ptable[0].append(dayInfor(d, op, cl, outUp[d], spread)) 
            if op >= inUp[d] and op < outUp[d] and op >= outUp[d]-spread:
                ptable[1].append(dayInfor(d, op, cl, outUp[d], spread)) 
            if op >= inUp[d] and op < outUp[d] and op <= inUp[d]+spread:
                ptable[2].append(dayInfor(d, op, cl, inUp[d], spread)) 
            if op >= mid[d] and op < inUp[d] and op >= inUp[d]-spread:
                ptable[3].append(dayInfor(d, op, cl, inUp[d], spread)) 
            if op >= mid[d] and op < inUp[d] and op <= mid[d]+spread:
                ptable[4].append(dayInfor(d, op, cl, mid[d], spread)) 
            if op >= inDown[d] and op < mid[d] and op > mid[d]-spread:
                ptable[5].append(dayInfor(d, op, cl, mid[d], spread)) 
            if op >= inDown[d] and op < mid[d] and op < inDown[d]+spread:
                ptable[6].append(dayInfor(d, op, cl, inDown[d], spread)) 
            if op >= outDown[d] and op < inDown[d] and op > inDown[d]-spread:
                ptable[7].append(dayInfor(d, op, cl, inDown[d], spread)) 
            if op >= outDown[d] and op < inDown[d] and op < outDown[d]+spread:
                ptable[8].append(dayInfor(d, op, cl, outDown[d], spread)) 
            if op < outDown[d]:
                ptable[9].append(dayInfor(d, op, cl, outDown[d], spread)) 

        for i in range(0, 10):
            print(desp[i])
            self.sarHardness(ptable[i])

    def display(self, firstTouchDays, regionMap):

        v = view.view()
        colors = dict()
        colors[-3] = 'r'
        colors[-2] = 'b'
        colors[0] = 'w'
        colors[2] = 'b'
        colors[3] = 'r'

        specialDates = dict()
        dates = sorted(firstTouchDays.keys())
        op = []
        hi = []
        lo = []
        cl = []
        for d in dates: 
            op.append(self.getOpen(d))
            hi.append(self.getHigh(d))
            lo.append(self.getLow(d))
            cl.append(self.getClose(d))
        specialDates['dates'] = dates
        specialDates['open'] = op
        specialDates['high'] = hi
        specialDates['low'] = lo
        specialDates['close'] = cl

        v.draw('HHI', self.d, self.o, self.h, self.l, self.c, \
                savefile='sar.png', figsize=(48, 12), region = regionMap, colors = colors, \
                specialDay = specialDates)

if __name__ == "__main__":
    sar = SAR()
    BBLength = range(19, 22)
    sdList = [3, 2, 0, -2, -3]
    sar.run('hhi_daily_bar.csv', BBLength, sdList)
    sar.display()
