###############################################################################
## logger : log all events

import datetime, inspect, os
from functools import partial
from termcolor import colored
import re, sys


output = sys.stdout

def redirectToFile(file):
    sys.stdout = open(file, 'a')

def cancelRedirectFile():
    sys.stdout = output

def logbreif(level, calllevel, msg):
	print( '[{level} {dt}] {msg}'.format(\
		level=level,
		dt=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), \
	   	msg=msg))

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
    
    if color == None:
        print(content)
    else:
        print(colored(content, color))

debugger = partial(log, 'Debug',1)
infor    = partial(log, 'Infor',1)
err      = partial(log, 'Error',1, color='red')
vipinfor = partial(infor, color='green')
warning  = partial(infor, color='red')


#def pd_infor(msg):
#    pd.set_option('display.max_rows', len(msg))
#    partial(log, 'Infor', 2)(msg)
#    pd.reset_option('display.max_rows') 
