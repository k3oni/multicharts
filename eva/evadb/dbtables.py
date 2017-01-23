#!/usr/bin/python
################################################################################
# create tables in db

from evadb.dbtool import dbtool

class dbtables:

    def __init__(self, dbname, dbuser, dbpasswd):
        self.dbtool = dbtool(dbname, dbuser, dbpasswd)
        
    def createTable(self, tablename):
        tables = dict()
        tables['exchange'] = 'create table exchange (\
                    id int primary key, \
                    name varchar, \
                    location varchar);'
        
        tables['instrument'] = 'create table instrument (\
                        id int primary key,\
                        bbgname varchar,\
                        ibname varchar,\
                        type varchar\
                        );'
        
        tables['contract'] = 'create table contract (\
                            id serial primary key,\
                            update_ts timestamp with time zone,\
                            instrument int,\
                            bbgname varchar,\
                            ibname varchar,\
                            othername varchar,\
                            start timestamp with time zone,\
                            expire timestamp with time zone\
                            );'
        
        tables['activecontract'] = 'create table activecontract (\
                            instId int,\
                            update_ts timestamp with time zone,\
                            datetime timestamp with time zone,\
                            contractId int,\
                            constraint activekey primary key (instId, datetime)\
                        );'
        
        tables['calendar'] = 'create table calendar(\
                        instruId int,\
                        update_ts timestamp with time zone,\
                        datetime timestamp with time zone,\
                        isTradingDay bool,\
                        sessionStart timestamp with time zone,\
                        sessionEnd  timestamp with time zone,\
                        primary key (instruId, datetime, sessionStart, sessionEnd)\
                        );'

        if tablename == 'all':
            for k in tables.keys():
                self.dbtool.execute(tables[k])
        else:
            if tablename in tables.keys():
                self.dbtool.execute(tables[tablename])
            else:
                print('Cannot find function to create table %s' % tablename)

###############################################################################
# unit test

if __name__ == '__main__':
    dt = dbtables('delvin', 'delvin', 'delvin123')
    dt.createTable('all')
