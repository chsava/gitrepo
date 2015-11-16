#!/bin/env python

"""
Author:         Cristian Sava, Symantec Corp.
Date:           10-Nov-2015
Last modified:  12-Nov-2015

Retrieve items needed by Zabbix monitoring using trapper items
"""

import argparse
import httplib
import sys
from zbxsend import Metric, send_to_zabbix

args=None

def get_json(host, port, url, key_file, cert_file):
    try:
        cnn=httplib.HTTPSConnection(host, port, key_file=key_file, cert_file=cert_file)
        cnn.request("GET", url)
        resp=cnn.getresponse()
        if resp.status!=200:
            sys.stderr.write("error: status code=%d while opening url: https://%s:%d%s\n" % (resp.status, args.host, args.port, args.url))
            return None
        return eval(resp.read())
    except Exception,e:
        sys.stderr.write("caught exception: %s\n" % str(e))
        return None


def get_metric_value(m, jd):
    try:
        return reduce(lambda parent, child:parent.get(child, ''), m.split('/'), jd)
    except:
        return ""


def main():
    global args

    parser = argparse.ArgumentParser(description='Retrieve items for the etcd zabbix template')

    parser.add_argument('--host', default="localhost", help='host name')
    parser.add_argument('--zhost', default="-", help='host name as configured in Zabbix')
    parser.add_argument('--zserver', default="localhost", help='Zabbix server')
    parser.add_argument('--zport', type=int, default=10051, help='Zabbix server trap port')
    parser.add_argument('--port', type=int, default=4001, help="service port")
    parser.add_argument('--url', default="/v2/stats/store", help="base url to be retrieved")
    parser.add_argument('--cert', default="/etc/origin/master/master.etcd-client.crt", help="ssl certificate file")
    parser.add_argument('--key', default="/etc/origin/master/master.etcd-client.key", help="ssl key file")
    parser.add_argument('--metrics', nargs='+', help="list of metrics to be retrieved")
    parser.add_argument('--metricnames', nargs='+', help="names of metrics to be retrieved")
    parser.add_argument('--verbose', default=False, action='store_true', help='verbose output')

    args=parser.parse_args()

    n=min(len(args.metrics), len(args.metricnames))

    jd=get_json(args.host, args.port, args.url, args.key, args.cert)

    if jd is None:
        sys.exit(-1)

    if args.verbose:
        print jd

    metrics=args.metrics[:n]
    metricnames=args.metricnames[:n]
    values=[get_metric_value(m, jd) for m in metrics]

    mobjs=[Metric(args.zhost, tp[0], tp[1]) for tp in zip(metricnames, values) if tp[1]!=""]

    if args.verbose:
        for m in mobjs:
            print m.host, m.key, m.value

    if not send_to_zabbix(mobjs, args.zserver, args.zport):
        print "zabbix trapper error!"
        sys.exit(-1)

    print "%d metrics sent successfully!" % len(mobjs)


if __name__=="__main__":
    main()
