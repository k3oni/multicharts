#!/usr/bin/python
# generate a python template of a class

import getopt,sys

def help():
    print("Usage: genpy classname")

if len(sys.argv) < 2:
    help()
    exit()

classname = sys.argv[1]
f = open(classname + '.py', 'w')
f.write('#!/usr/bin/python\n')
f.write('#'*80)
f.write('\n\n')

f.write('class %s:\n\n' % classname)
f.write('    def __init__(self):\n')
f.close()


