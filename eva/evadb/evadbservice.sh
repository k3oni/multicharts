#!/usr/bin/bash
LD_LIBRARY_PATH=/home/delvin/code/python/eva/othersrc/blpapi_cpp_3.8.18.1/Linux
export LD_LIBRARY_PATH
logpath=/home/delvin/code/python/eva/engine/log/
logfile=evadb.`date +"%Y%m%d"`
/home/delvin/code/python/eva/evadb/dbservice.py >  $logpath$logfile
