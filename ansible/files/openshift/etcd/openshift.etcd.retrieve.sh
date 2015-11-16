#!/bin/env bash

#retrieve zabbix etcd trapper values

dirpath=`dirname $0`

source "$dirpath/openshift.config.sh"

mprefix=dummy
metrics=()

if [ "$1" == "store" ]
then
    mprefix=etcd.store
    metrics=(compareAndDeleteFail compareAndDeleteSuccess compareAndSwapFail compareAndSwapSuccess createFail createSuccess deleteFail deleteSuccess setsFail setsSuccess updateFail updateSuccess getsFail getsSuccess watchers)
fi

if [ "$1" == "self" ]
then
    mprefix=etcd.self
    metrics=(recvAppendRequestCnt sendAppendRequestCnt state)
fi

if [ $mprefix == "dummy" ]
then
    exit 1
fi

metricnames=()
for m in "${metrics[@]}"
do
    metricnames+=( "${mprefix}[$m]" )
done


cmd="$dirpath/get_etcd_values.py"
cmdargs="--url /v2/stats/$1 --metrics ${metrics[@]} --metricnames ${metricnames[@]} --zhost $ZABBIX_HOST --zserver $ZABBIX_SERVER --zport $ZABBIX_TRAP_PORT"

#echo "$cmd $cmdargs"

exec "$cmd" $cmdargs
