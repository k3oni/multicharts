#!/usr/bin/python
###############################################################################
# dbtools provides basic content services

import time, pytz
from tools.logger import  infor, err
from tools.timezonemap import timeZoneMap
from datetime import datetime
from evadb.db import database

class dbtool:
    
    def __init__(self, dbname, user, passwd):
        self.db = database(dbname, user, passwd)
        self.db.connect()

    def __exit__(self):
        self.db.commit()
        self.db.close()
    
    def execute(self, statement):
        self.db.execute(statement)
        self.db.commit()

    def fetch(self, statement):
        return self.db.fetch(statement) 

    ###########################################################################
    # dbms function

    def updateTimeZone(self, timezone):
        self.db.execute("set time zone '%s'" % timezone)
        self.db.commit()
        
        check = "show timezone;"
        updated = self.fetch(check)[0][0]

        if updated == timezone:
            infor("Update timezone to %s." % timezone)
        else:
            err("Cannot update timezone from %s to %s" % (timezone, updated))
    

    def isTableExisted(self, tablename):
        sql = "select count(*) from pg_tables where tablename='%s'" % tablename
        num = self.fetch(sql)[0][0]
        return num > 0

    def deleteTable(self, tablename):
        sql = "delete from %s;" % tablename
        self.db.execute(sql)
        self.db.commit()
        
        check = "select count(*) from %s;" % tablename
        remain = self.fetch(check)[0][0]

        if remain == 0:
            infor("Table %s are deleted." % tablename)
        else:
            err("Table %s are not deleted." % tablename)

    def dropTable(self, tablename):
        sql = 'drop table %s;' % tablename;
        self.execute(sql)
        infor('Drop table %s' % tablename)
                
    def checkInserted(self, check, record):
        remain = self.fetch(check)[0][0]
        if remain == 1:
            infor("Record inserted: %s" % record)
        if remain == 0:
            err("Record not inserted: %s. Error code: %d" % (record, remain))
            err("check %s" % check)
        if remain > 1:
            err("Multiple records with %s. Error code: %d" % (record, remain))
            err("check %s" % check)

    def checkDeleted(self, check, record):
        remain = self.fetch(check)[0][0]
        if remain == 0:
            infor("Delete by SQL %s" % record)
        else:
            err("Fail to delete by SQl %s." % record)

# unit test
if __name__ == "__main__":
    dbt = dbtool('delvin', 'delvin', 'delvin123')
    dbt.deleteContractForInstrument('HC1 Index')
