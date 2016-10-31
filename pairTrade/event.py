# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 11:34:52 2016

@author: gdpan
"""

from enum import Enum 

class EventType(Enum):
    Trade = 1
    SpreadTrade = 2

class Event:
    def __init__(self, type, content):
        self.type = type
        self.content = content
            