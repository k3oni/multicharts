# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 13:47:17 2015

@author: sancho.chan
"""

import sys
import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta

global msg
msg = str(dt.datetime.now()) + "\n" 

def resampleBars(secName, hdf, expiryYYYYMM, timeRes, resampledPeriod):
    hdfKey ='/M' + expiryYYYYMM + '/' + timeRes 

    if timeRes == 'm1':
        bars = hdf.get(hdfKey)
	bars['timestamp'] = hdf.get(hdfKey)['timestamp'].astype('datetime64[s]')
        bars.set_index(pd.DatetimeIndex(bars['timestamp']), inplace=True)
	bars = bars.resample(resampledPeriod)
        return bars


# ==== Main ====
if len(sys.argv) < 4:
  print "./" + sys.argv[0], './HC1_Index.h5 HC1_Index 20151012'
  exit(1)
fileName          = sys.argv[1]
secName           = sys.argv[2]    
checkDateYYYYMMDD = sys.argv[3]
msg              += "\nChecking " + fileName + " ...\n"

hdf = pd.HDFStore(fileName, mode='r')
allKeys = hdf.keys()
allKeys.sort()
expiryYYYYMM = allKeys[-1].split('/')[1][1:]   # '/M20151011/m1' => 'M20151011' => '20151011'

m3Bars = resampleBars(secName, hdf, expiryYYYYMM, 'm1', '3T')
print m3Bars

hdf.close()    


