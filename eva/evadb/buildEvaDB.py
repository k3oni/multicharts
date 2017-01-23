#!/usr/bin/python
###############################################################################
# This module will build EvaDB system

from engine.jsonconfig import jsonConfig
from evadb.dbtool import dbtool
import dbtablename as dbn

from bbg.bbg import bbg
from exchange import exchange
from instruments import instruments
from evacalendar import evaCalendar
from contract import contract
from activecontract import activeContract
from rollover import rollover

# load configure
cfgfile = '../engine/HC1_EP_paper.eva'
cfg = jsonConfig()
cfg.load(cfgfile)
syscfg = cfg.getSystemConfig()
dbname = syscfg['dbname']
username = syscfg['dbuser']
passwd = syscfg['dbpasswd']

dbt = dbtool(dbname, username, passwd)

# connect bbg
bbgserver = syscfg['BBGServer']
bbgport = syscfg['BBGPort']
BBG = bbg(bbgserver, bbgport) 

# build DB
# create tables

exch = exchange(dbname, username, passwd, dbn.exchangeTable)
if dbt.isTableExisted(exch.tablename):
    dbt.dropTable(exch.tablename)
exch.createTable()

instr = instruments(dbname, username, passwd, dbn.instrumentsTable, exch) 
if dbt.isTableExisted(instr.tablename):
    dbt.dropTable(instr.tablename)
instr.createTable()

calen = evaCalendar(dbname, username, passwd, dbn.calendarTable, instr)
if dbt.isTableExisted(calen.tablename):
    dbt.dropTable(calen.tablename)
calen.createTable()

contr = contract(dbname, username, passwd, dbn.contractTable, instr)
if dbt.isTableExisted(contr.tablename):
    dbt.dropTable(contr.tablename)
contr.createTable()

ac = activeContract(dbname, username, passwd, dbn.activecontractTable, instr)
if dbt.isTableExisted(ac.tablename):
    dbt.dropTable(ac.tablename)
ac.createTable()

# fill exchange data
exch.fill()

# fill instrument data
instr.fill()

# fill data per instrument
instrnames = instr.getAllInstruments()

for name in instrnames:
    # fill calendar
    calen.fill(name)
    # get active contracts
    contracts = ac.getActiveContractFromBBG(name, BBG)
    # store contracts into contract table
    contr.fillContract(name, contracts, BBG)
    # get rollover method
    r = rollover(name, calen)
    # get start and expire date per contract
    contract, period = BBG.requestContractsStartAndExpire(name, \
                instr.getInstrumentTimezone(name), contracts)
    # set active contract for each day
    ac.fillActiveContract(name, instr, contr, r, \
                            contracts = contract, periods = period)
    
