#!/usr/bin/python
###############################################################################
# db class is used to read and write to postgresql database

import psycopg2
from tools.common import err
import engine.jsonconfig as jbase

class database:
    
    def __init__(self, dbname, user, passwd):
        self.dbname = dbname
        self.user = user
        self.passwd = passwd
        self.loadConfig()
    
    def loadConfig(self, filename='/home/delvin/prod/eva/engine/HC1_EP_paper.eva'):
        jcfg = jbase.jsonConfig()
        self.cfg =jcfg.load(filename)
        self.host = self.cfg.system['dbip']

    def connect(self):
        try:
            self.conn = psycopg2.connect("host='%s' dbname=%s user=%s password=%s" \
                % (self.host, self.dbname, self.user, self.passwd))
        except:
            err('Fail to connect postgresql database ...')
            err('Make sure your database name, user name and password are correct.')
            err('Database name: %s' % self.dbname)
            err('User name: %s' % self.user)
            err('Password: %s' % self.passwd)
        self.cur = self.conn.cursor()

    def execute(self,statement):
        self.cur.execute(statement)

    def fetch(self, statement):
        self.execute(statement)
        return self.cur.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()

# unit test

if __name__ == '__main__':
    db = database('delvin', 'delvin', 'delvin123')
    db.connect()
    db.execute('create table test (id int primary key, content varchar);')
    db.commit()
    db.close()
