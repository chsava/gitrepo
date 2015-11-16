#!/bin/env bash

dirpath=$( dirname "$0" )

source "$dirpath/openshift.config.sh"

result=$( "$dirpath/create.app.py" | grep -v ^$ )

cmdargs="-z $ZABBIX_SERVER -p $ZABBIX_TRAP_PORT -s $ZABBIX_HOST -k openshift.master.create.app -o $result"

exec zabbix_sender $cmdargs
