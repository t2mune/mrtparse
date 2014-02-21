#!/usr/bin/env python
'''
exabgp_conf.py is a script to create a configuration file for exabgp using mrtparse.

See https://github.com/YoshiyukiYamauchi/mrtparse for more informations.
This script is published under a Apache License, Version 2.0.
Created by
    Tetsumune KISO <t2mune@gmail.com>,
    Yoshiyuki YAMAUCHI <info@greenhippo.co.jp>,
    Nobuhiro ITOU <js333123@gmail.com>.
Copyright (C) greenHippo, LLC. All rights reserved.
'''

from mrtparse import *
import sys, re

def make_exabgp_conf(d):
    router_id  = '192.168.0.20'
    local_addr = '192.168.1.20'
    neighbor   = '192.168.1.100'
    nexthop    = '192.168.1.254'
    local_as   = 65000
    peer_as    = 64512
    indent     = '    '
    
    print('''
    neighbor %s {
        router-id %s;
        local-address %s;
        local-as %d;
        peer-as %d;
        graceful-restart;
    
        static {'''
    % (neighbor, router_id, local_addr, local_as, peer_as))
    
    for m in d:
        if m.type == MSG_T['TABLE_DUMP_V2']:
            if m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']:
                line = '            route %s/%d' % (m.rib.prefix, m.rib.plen)
                for attr in m.rib.entry[0].attr:
                    line += get_bgp_attr(attr)
            if m.subtype == TD_V2_ST['RIB_IPV6_UNICAST']:
                pass
    print('%s next-hop %s;' % (line, nexthop))
    print('''
        }
    }
    ''')

def get_bgp_attr(attr):
    line = ''
    r = re.compile("([0-9]+)\.([0-9]+)")

    if attr.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
        line += ' atomic-aggregate'

    if attr.len == 0:
        return line

    if attr.type == BGP_ATTR_T['ORIGIN']:
        line += ' origin %s' % ORIGIN_T[attr.origin]

    elif attr.type == BGP_ATTR_T['AS_PATH']: 
        as_path = ''
        for path_seg in attr.as_path:
            if path_seg['type'] == AS_PATH_SEG_T['AS_SET']:
                as_path += '(%s) ' % path_seg['val']
            else:
                as_path += '%s ' % path_seg['val']
        line += ' as-path [%s]' % as_path

    elif attr.type == BGP_ATTR_T['NEXT_HOP']:
        pass

    elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
        line += ' med %d' % attr.med

    elif attr.type == BGP_ATTR_T['LOCAL_PREF']:
        line += ' local-preference %d' % attr.local_pref

    elif attr.type == BGP_ATTR_T['AGGREGATOR']:
        asn = attr.aggr['asn']
        m = r.search(asn)
        if m is not None:
            asn = int(m.group(1)) * 65536 + int(m.group(2))
        line += ' aggregator (%s:%s)' % (str(asn), attr.aggr['id'])

    elif attr.type == BGP_ATTR_T['COMMUNITY']:
        comm = ' '.join(attr.comm)
        line += ' community [%s]' % comm

    elif attr.type == BGP_ATTR_T['ORIGINATOR_ID']:
        line += ' originator-id %s' % attr.org_id

    elif attr.type == BGP_ATTR_T['CLUSTER_LIST']:
        line += ' cluster-list [%s]' % ' '.join(attr.cl_list)

    elif attr.type == BGP_ATTR_T['EXTENDED_COMMUNITIES']:
        ext_comm_list = []
        for ext_comm in attr.ext_comm:
            ext_comm_list.append('0x%016x' % ext_comm)
        line += ' extended-community [%s]' % ' '.join(ext_comm_list)

    elif attr.type == BGP_ATTR_T['AS4_PATH']:
        as_path = ''
        for path_seg in attr.as_path:
            if path_seg['type'] == AS_PATH_SEG_T['AS_SET']:
                as_path += '(%s) ' % path_seg['val']
            else:
                as_path += '%s ' % path_seg['val']
        line += ' as4-path [%s]' % as_path

    elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']:
        asn = attr.aggr['asn']
        m = r.search(asn)
        if m is not None:
            asn = int(m.group(1)) * 65536 + int(m.group(2))
        line += ' as4-aggregator (%s:%s)' % (str(asn), attr.aggr['id'])
    return line

def main():
    if len(sys.argv) != 2:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    d = Reader(sys.argv[1])
    make_exabgp_conf(d)

if __name__ == '__main__':
    main()
