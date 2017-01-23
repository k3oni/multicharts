#!/usr/bin/python
###############################################################################
# This script is to analysis bollinger band sar effectiveness

import csv
from indicator.bollingerband import BollingerBand
from pprint import pprint
from tools.common import vipinfor, infor

def createDataList(filename):
    d = []
    o = []
    h = []
    l = []
    c = []

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for r in reader:
            data = map(float, r)
            d.append(data[0])
            o.append(data[1])
            h.append(data[2])
            l.append(data[3])
            c.append(data[4])

    return d, o, h, l, c

def getBB(date, open, close, BBLength, sd):
    BB = BollingerBand(BBLength, sd)
    BBopen = dict()
    BBclose = dict()
    dataNum = len(date)

    for i in range(BBLength-1, dataNum-1):
        sampleWithOpen = close[i-(BBLength-1):i+1]
        sampleWithOpen.append(open[i+1]) # using day open to estimate BB
        v1 = BB.getInitBB(sampleWithOpen) 
        BBopen[date[i+1]] = v1

    for i in range(BBLength, dataNum):
        sampleWithClose = close[i-BBLength:i]
        v2 = BB.getInitBB(sampleWithClose) 
        BBclose[date[i]] = v2
    
    return BBopen, BBclose

class dayInfor:
    def __init__(self, d, open, close, sar, spread):
        self.d = d
        self.op = open
        self.cl = close
        self.sar = sar
        self.spread = spread

    def display(self):
        print('{d}: open {op}, close {cl}, diff {diff}, spread {spread}, sar {sar}'.format(\
                d=self.d, op = self.op, cl = self.cl, diff = self.cl-self.op,\
                spread=self.spread, sar=self.sar))

def SAREffective(date, open, close, dsMap, spread):
    outUp   = dsMap[3]
    inUp    = dsMap[2]
    mid     = dsMap[0]
    inDown  = dsMap[-2]
    outDown = dsMap[-3]
    
    desp = ['out of 3 std', 'below close to 3 std', 'above close to 2 std',\
            'below close to 2 std', 'above close to mid', 'below close to mid',\
            'above close to -2 std', 'below close to -2 std', 'above close to -3 std',\
            'out of -3 std']

    ptable = dict()
    for i in range(0, 10):
        ptable[i] = []

    startdate = max(min(outUp.keys()), min(inUp.keys()), min(mid.keys()),\
                     min(inDown.keys()), min(outDown.keys()))

    for i in range(0, len(date)):
        d = date[i]
        if d < startdate:
            continue

        op = open[i]
        cl = close[i]

        if op >= outUp[d]:
            #print("Date: %s open %s out of 3 std %s" % (d, op, outUp[d]))  
            ptable[0].append(dayInfor(d, op, cl, outUp[d], spread)) 

        if op >= inUp[d] and op < outUp[d] and op >= outUp[d]-spread:
            #print("Date: %s open %s 2 - 3 std, close to 3 std" % (d, op))  
            ptable[1].append(dayInfor(d, op, cl, outUp[d], spread)) 

        if op >= inUp[d] and op < outUp[d] and op <= inUp[d]+spread:
            #print("Date: %s open %s 2 - 3 std, close to 2 std" % (d, op))  
            ptable[2].append(dayInfor(d, op, cl, inUp[d], spread)) 

        if op >= mid[d] and op < inUp[d] and op >= inUp[d]-spread:
            #print("Date: %s open %s mid - 2 std, close to 2 std" % (d, op))  
            ptable[3].append(dayInfor(d, op, cl, inUp[d], spread)) 

        if op >= mid[d] and op < inUp[d] and op <= mid[d]+spread:
            #print("Date: %s open %s mid - 2 std, close to mid" % (d, op))  
            ptable[4].append(dayInfor(d, op, cl, mid[d], spread)) 

        if op >= inDown[d] and op < mid[d] and op > mid[d]-spread:
            #print("Date: %s open %s -2 std - mid, close to mid" % (d, op))  
            ptable[5].append(dayInfor(d, op, cl, mid[d], spread)) 

        if op >= inDown[d] and op < mid[d] and op < inDown[d]+spread:
            #print("Date: %s open %s -2 std - mid, close to -2 std" % (d, op))  
            ptable[6].append(dayInfor(d, op, cl, inDown[d], spread)) 

        if op >= outDown[d] and op < inDown[d] and op > inDown[d]-spread:
            #print("Date: %s open %s -3 std - -2 std, close to -2 std" % (d, op))  
            ptable[7].append(dayInfor(d, op, cl, inDown[d], spread)) 

        if op >= outDown[d] and op < inDown[d] and op < outDown[d]+spread:
            #print("Date: %s open %s -3 std - -2 std, close to -3 std" % (d, op))  
            ptable[8].append(dayInfor(d, op, cl, outDown[d], spread)) 

        if op < outDown[d]:
            #print("Date: %s open %s out of -3 std %s" % (d, op, outDown[d]))  
            ptable[9].append(dayInfor(d, op, cl, outDown[d], spread)) 

    for i in range(0, 10):
        print(desp[i])
        sarHardness(ptable[i])

def sarHardness(plist):
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

def SARPiecing(date, open, high, low, close, dsMap):

    outUp   = dsMap[3]
    inUp    = dsMap[2]
    mid     = dsMap[0]
    inDown  = dsMap[-2]
    outDown = dsMap[-3]
    counters = dict()

    for i in range(0, 5):
        counters[i] = dict()
    
    startdate = max(min(outUp.keys()), min(inUp.keys()), min(mid.keys()),\
                     min(inDown.keys()), min(outDown.keys()))

    for i in range(0, len(date)):
        d = date[i]
        if d < startdate:
            continue

        op = open[i]
        hi = high[i]
        lo = low[i]
        cl = close[i]

        sars = []
        sars.append(outUp[d])
        sars.append(inUp[d])
        sars.append(mid[d])
        sars.append(inDown[d])
        sars.append(outDown[d])

        for level in range(0, 5):
            if hi >= sars[level] and lo <= sars[level]:
                counters[level][d] = 1
            else:
                counters[level][d] = 0
    

    # find out only touch days
    touchDays = dict()
    for d in counters[0].keys():
        cross = []
        for level in range(0, 5):
            cross.append(counters[level][d])
        if cross <> [0, 0, 0, 0, 0]:
            touchDays[d] = cross 

    #displayDict(touchDays)
    

    # filter first touch days
    firstTouch = dict()
    orderedDate = sorted(touchDays.keys())
    for index in range(1, len(orderedDate)):
        yest = orderedDate[index-1]
        today = orderedDate[index]
        if isFirstTouch(touchDays[yest], touchDays[today]):
            firstTouch[today] = touchDays[today]        

    # categroized
    category = categorizeFirstTouch(firstTouch, open, high, low, close)

    # statistic
    
    

def categorizeFirstTouch(firstTouch, open, high, low, close):
    category = dict()
    for i in range(0, 5):
        category[i] = dict()

    for d in firstTouch.keys():
        tl = firstTouch[d]
        for j in range(0, len(tl)):
            if tl[j] == 1:
                category[j][d] = (open[d], high[d], low[d], close[d])
                        
    return category

def displayDict(dic):
    for k in sorted(dic.keys()):
        infor('{k} : {v}'.format(k=k, v=dic[k]))    

def displayFirstTouch(firstTouch, counters):
    for d in sorted(counters[0].keys()):
        if d in firstTouch.keys():
            vipinfor('date {d} : {c}'.format(d=d, c=firstTouch[d]))
            continue
        cross = []
        for level in range(0, 5):
            cross.append(counters[level][d])
        infor('date {d} : {c}'.format(d=d, c=cross))

def isFirstTouch(lastTouch, thisTouch):
    for i in range(0, len(thisTouch)):
        if thisTouch[i] <> 0:
            noPreviousTouch = lastTouch[i] == 0
            existOtherTouch = False
            for j in range(0, len(lastTouch)):
                if j <> i and lastTouch[j] == 1:
                    existOtherTouch = True
                    break
            if noPreviousTouch and existOtherTouch:
                return True
                    
                

if __name__ == "__main__":
    date, open , high, low, close = createDataList('hhi_daily_bar.csv')
    BBLength = 20
    spread = 50
    dsMap = dict()

    for sd in (-3, -2, 0, 2, 3):
        BBopen, BBclose = getBB(date, open, close, BBLength, sd)
        dsMap[sd] = BBclose

    SARPiecing(date, open, high, low, close, dsMap)

    #for spread in range(10, 200, 10):
    #    print('*'*80)
    #    print('spread %s' % spread)
    #    SAREffective(date, open, close, dsMap, spread) 
