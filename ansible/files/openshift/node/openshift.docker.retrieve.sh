#!/bin/env bash

#retrieve zabbix docker trapper values

dirpath=`dirname $0`

source "$dirpath/openshift.config.sh"

mprefix=dummy
metrics=()
names=()

metrics+=( 'memory_stats/stats/total_cache' )
names+=( 'memory.cache' )

metrics+=( 'memory_stats/stats/total_pgfault' )
names+=( 'memory.pgfault' )

metrics+=( 'memory_stats/stats/total_pgmajfault' )
names+=( 'memory.pgmajfault' )

metrics+=( 'memory_stats/stats/total_pgpgin' )
names+=( 'memory.pgpgin' )

metrics+=( 'memory_stats/stats/total_pgpgout' )
names+=( 'memory.pgpgout' )

metrics+=( 'memory_stats/stats/total_rss' )
names+=( 'memory.rss' )

metrics+=( 'memory_stats/stats/total_swap' )
names+=( 'memory.swap' )

metrics+=( 'memory_stats/usage' )
names+=( 'memory.usage' )

metrics+=( 'network/rx_bytes' )
names+=( 'network.rx.bytes' )

metrics+=( 'network/rx_packets' )
names+=( 'network.rx.packets' )

metrics+=( 'network/rx_dropped' )
names+=( 'network.rx.dropped' )

metrics+=( 'network/rx_errors' )
names+=( 'network.rx.errors' )

metrics+=( 'network/tx_bytes' )
names+=( 'network.tx.bytes' )

metrics+=( 'network/tx_packets' )
names+=( 'network.tx.packets' )

metrics+=( 'network/tx_dropped' )
names+=( 'network.tx.dropped' )

metrics+=( 'network/tx_errors' )
names+=( 'network.tx.errors' )

metrics+=( '_x_cpu_kernel' )
names+=( 'cpu.kernel' )

metrics+=( '_x_cpu_user' )
names+=( 'cpu.user' )

if [ "$1" == "registry" ]
then
    cimage="openshift/origin-docker-registry"
    mprefix="docker.registry"
fi

if [ "$1" == "router" ]
then
    cimage="openshift/origin-haproxy-router"
    mprefix="docker.router"
fi

if [ $mprefix == "dummy" ]
then
    exit 1
fi

metricnames=()
for m in "${names[@]}"
do
    metricnames+=( "${mprefix}.${m}" )
done


cmd="$dirpath/get_docker_stats.py"
cmdargs="--image $cimage --metrics ${metrics[@]} --metricnames ${metricnames[@]} --zhost $ZABBIX_HOST --zserver $ZABBIX_SERVER --zport $ZABBIX_TRAP_PORT"

#echo "$cmd $cmdargs"

exec "$cmd" $cmdargs
