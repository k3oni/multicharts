#!/usr/bin/python
###############################################################################
## message factory creates msg according to datatype

from feed import dataType, feedType
from filefeed import fileFeed
from urlfeed import urlFeed
#from hdf5feed import hdf5Feed
from hdfbarfeed import hdfBarFeed
from tools.common import err

class feedFactory:

    def __init__(self):
        pass

    def createFeed(self, feedtype, src, datatype, timezone, **kwargs):

        if feedtype == feedType.UrlFeed:
            return urlFeed(datatype, src, timezone)

        if feedtype == feedType.FileFeed:
            return fileFeed(datatype, src, timezone)

        if feedtype == feedType.hdfBarFeed:
            if  'instrument' in kwargs.keys() and \
                'contract' in kwargs.keys() and \
                'expireYear' in kwargs.keys() and \
                'expireMonth' in kwargs.keys() and\
                'barlen' in kwargs.keys(): \
                return hdfBarFeed(datatype, src, timezone,\
                                kwargs.get('instrument'),\
                                kwargs.get('contract'),\
                                kwargs.get('expireYear'),\
                                kwargs.get('expireMonth'),\
                                kwargs.get('barlen'))
            else:
                err("Fail to create hdf bar feed.")


        err("Unsupport feed type yet.")
        return False
    
