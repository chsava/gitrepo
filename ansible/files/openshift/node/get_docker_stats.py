#!/bin/env python

"""
Author:         Cristian Sava, Symantec Corp.
Date:           12-Nov-2015
Last modified:  12-Nov-2015

Retrieve stats about given docker container
"""

import docker
import time
import argparse
import sys
from zbxsend import Metric, send_to_zabbix

args=None

def get_x_cpu_kernel(st0, st1):
    kernel_mode0=get_metric_from_dict("cpu_stats/cpu_usage/usage_in_kernelmode", st0)
    kernel_mode1=get_metric_from_dict("cpu_stats/cpu_usage/usage_in_kernelmode", st1)
    system0=get_metric_from_dict("cpu_stats/system_cpu_usage", st0)
    system1=get_metric_from_dict("cpu_stats/system_cpu_usage", st1)
    return round((kernel_mode1-kernel_mode0)*100.0/(system1-system0), 2)


def get_x_cpu_user(st0, st1):
    user_mode0=get_metric_from_dict("cpu_stats/cpu_usage/usage_in_usermode", st0)
    user_mode1=get_metric_from_dict("cpu_stats/cpu_usage/usage_in_usermode", st1)
    system0=get_metric_from_dict("cpu_stats/system_cpu_usage", st0)
    system1=get_metric_from_dict("cpu_stats/system_cpu_usage", st1)
    return round((user_mode1-user_mode0)*100.0/(system1-system0), 2)


composite_metrics={"_x_cpu_kernel":get_x_cpu_kernel, 
                   "_x_cpu_user":get_x_cpu_user}


def get_metric(m, st0, st1):
    if m in composite_metrics:
        return composite_metrics[m](st0, st1)
    return get_metric_from_dict(m, st1)


def get_metric_from_dict(m, jd):
    try:
        return reduce(lambda parent, child:parent.get(child, ''), m.split('/'), jd)
    except:
        return ""


def get_container_id(image):
    pass


def main():
    global args

    parser = argparse.ArgumentParser(description='Retrieve Zabbix stats about docker containers')

    parser.add_argument('--zhost', default="-", help='host name as configured in Zabbix')
    parser.add_argument('--zserver', default="localhost", help='Zabbix server')
    parser.add_argument('--zport', type=int, default=10051, help='Zabbix server trap port')
    parser.add_argument('--nozsend', default=False, action='store_true', help='do not send to Zabbix')
    parser.add_argument('--url', default="unix://var/run/docker.sock", help="base docker url")
    parser.add_argument('--metrics', nargs='+', help="list of metrics to be retrieved")
    parser.add_argument('--metricnames', nargs='+', help="names of metrics to be retrieved")
    parser.add_argument('--verbose', default=False, action='store_true', help='verbose output')
    parser.add_argument('--image', help='container image')

    args=parser.parse_args()

    n=min(len(args.metrics), len(args.metricnames))

    if not args.image:
        print "error: need container image name!"
        sys.exit(-1)

    dc=docker.Client(base_url=args.url)

    conts=filter(lambda cnt:cnt['Image']==args.image, dc.containers(quiet=False))

    if len(conts)!=1:
        print "error: could not identify container with image=%s" % args.image
        sys.exit(-1)

    cid=conts[0]['Id']
    stats=dc.stats(cid)

    st0=stats.next()
    time.sleep(1)
    st1=stats.next()

    if args.verbose:
        print "cid=%s" % cid
        print st0, st1

    env={'null': ''}

    metrics=args.metrics[:n]
    metricnames=args.metricnames[:n]
    values=[get_metric(m, eval(st0, env), eval(st1, env)) for m in metrics]

    zhost = "localhost" if args.zhost=='-' else args.zhost

    mobjs=[Metric(zhost, tp[0], tp[1]) for tp in zip(metricnames, values) if tp[1]!=""]

    if args.verbose or args.nozsend:
        for m in mobjs:
            print args.zhost, m.key, m.value

    if not args.nozsend and send_to_zabbix(mobjs, args.zserver, args.zport):
        print "%d metrics sent successfully!" % len(mobjs)


if __name__=="__main__":
    main()
