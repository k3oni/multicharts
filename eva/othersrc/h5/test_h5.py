#!/usr/bin/python

import pandas as pd
from datetime import datetime, time

filename = 'HC1_Index.h5'
maturity = '201510'
barSize  = 'm1' # m1 or h1 or d1

def dt_to_epoch(dt):
    return (dt - datetime(1970,1,1)).total_seconds()

def epoch_to_dt(epoch):
    return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

start = datetime(2015,10,21,0,0)
end = datetime(2013,10,28,0,0)

df = pd.read_hdf(filename, '/M' + maturity + '/' + barSize)
#df = pd.read_hdf(filename, '/M' + maturity + '/' + barSize, where = ['timestamp>{start} and timestamp<{end}'.format(start=dt_to_epoch(start), end=dt_to_epoch(end))])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
print df
