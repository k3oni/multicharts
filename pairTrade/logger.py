# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 11:37:05 2016

@author: delvin
"""

import os, inspect, datetime, re
from functools import partial

def log(level, calllevel, msg, color=None):
     fmt = '{0:{1}}'
     filename = os.path.basename(inspect.stack()[calllevel][1])
     filename = re.sub('\.py$', '', filename)
 
     content = '[{level} {dt} {filename:6} {line:3}] {msg}'.format(\
         level=level,
         dt=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), \
         filename=filename[0:6],\
         line=str(inspect.stack()[calllevel][2])[0:3],\
         msg=msg)
 
     print(content)

 
debugger = partial(log, 'Debug',1)
infor    = partial(log, 'Infor',1)
err      = partial(log, 'Error',1)
