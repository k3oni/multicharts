# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 20:00:34 2016

@author: delvin
"""
import datetime

class tools:
    def __init__(self):
        pass
    
    @staticmethod
    def getDateFromDatetime(ts):
        return datetime.date(ts.year, ts.month, ts.day)