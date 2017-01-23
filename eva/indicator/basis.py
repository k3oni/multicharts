#!/usr/bin/python
###############################################################################
# basis

import math

def average(s):
    return sum(s) * 1.0 / len(s)

def bias_variance(s):
    total = map(lambda x: (x - average(s))**2, s)
    return sum(total)/(len(total))

def variance(s):
    total = map(lambda x: (x - average(s))**2, s)
    return sum(total)/(len(total)-1)

def std(s):
    return math.sqrt(bias_variance(s))
