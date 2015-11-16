#!/usr/local/bin/python

"""
Author: Cristian Sava, Symantec Corp.
Date: 28-Oct-2015
Last modified: 28-Oct-2015

Add one host to the given Zabbix server
"""

import zabbix_api
import sys
import argparse


def get_hostgroup_id(z, hostgroup):
    group=z.hostgroup.get({'output':'extend', 
                           'filter': {'name': hostgroup}})

    return group[0]['groupid'] if len(group)==1 else None

def get_template_id(z, template):
    lst=z.template.get({'output':'extend', 
                          'filter': {'name': template}})

    return lst[0]['templateid'] if len(lst)==1 else None

def add_host(z, host, ip, hostgroups, templates):
    gids=[{"groupid": str(g[1]) for g in hostgroups}]
    tids=[{"templateid": str(t[1]) for t in templates}]
    req = {'host': host,
           'interfaces': [{ 'type': 1,
                            'main': 1,
                            'useip': 1,
                            'ip': ip,
                            'dns': '',
                            'port': '10050'}],
            'groups': gids,
            'templates': tids}
    print req
    z.host.create(req)


def main():
    parser = argparse.ArgumentParser(description='Add host to given Zabbix server')

    parser.add_argument('--zabbix', help='Zabbix server url')
    parser.add_argument('--zlogin', help='Zabbix login')
    parser.add_argument('--zpwd', help='Zabbix password')
    parser.add_argument('--hostname', help='Host name to be added')
    parser.add_argument('--hostip', help='Host ip address')
    parser.add_argument('--hostgroups', nargs='+', help='Host group list')
    parser.add_argument('--templates', nargs='+', help='Templates to be linked to given host')

    args = parser.parse_args()

    try:
        z=zabbix_api.ZabbixAPI("http://%s/zabbix" % args.zabbix)
        z.login(args.zlogin, args.zpwd)
    except Exception,e:
        print "Could not login! Caught exception: %s" % str(e)
        sys.exit(-1)

    try:
        hostgroups=[(x, get_hostgroup_id(z, x)) for x in args.hostgroups]
        templates=[(x, get_template_id(z, x)) for x in args.templates]

        add_host(z, args.hostname, args.hostip, hostgroups, templates)
    except Exception,e:
        print "Could not add host! Caught exception: %s" % str(e)
        sys.exit(-1)


if __name__=="__main__":
    main()
