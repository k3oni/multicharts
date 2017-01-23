#/usr/bin/python
################################################################################
# every data stord in database is a subclass of dbEntity

from tools.common import infor, err
from evadb.dbtool import dbtool

class dbEntity:

    def __init__(self, dbname, dbuser, dbpasswd, tablename):
        self.dbtool = dbtool(dbname, dbuser, dbpasswd)
        self.tablename = tablename
    
    def createTable(self):
        pass

    def fill(self):
        pass 
