#/usr/bin/python
################################################################################
from dbtables import dbtables
from tools.common import infor, err
from evadb.dbtool import dbtool
from dbentity import dbEntity

class exchange(dbEntity):

    def __init__(self, dbname, dbuser, dbpasswd, tablename):
        dbEntity.__init__(self, dbname, dbuser, dbpasswd, tablename)

    def createTable(self):
        sql = 'create table {tn} (\
                    id int primary key, \
                    name varchar, \
                    location varchar,\
                    timezone varchar);'.format(tn = self.tablename)
        self.dbtool.execute(sql)
    

    def fill(self):
        exch = dict()
        exch[1] = ['EPRX HKG', 'Hong Kong', 'Asia/Hong_Kong']
        exch[2] = ['EPRX EUX', 'Germany', 'CET']
        exch[3] = ['EPRX CBF', 'United States', 'CST6CDT']
        Prefix = 'insert into {tn} values ('.format(tn = self.tablename)
        Suffix = ');'
        
        for k in exch.keys():
            c = "%d, '%s', '%s', '%s'" % (k, exch[k][0], exch[k][1], exch[k][2])
            sql = Prefix + c + Suffix
            self.dbtool.execute(sql)
            
            check = "select count(*) from %s where name='%s' and location='%s'\
                        and timezone='%s'" % (self.tablename, exch[k][0], \
                        exch[k][1], exch[k][2])
            self.dbtool.checkInserted(check, c)
        
             
