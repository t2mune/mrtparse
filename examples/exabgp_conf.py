#!/usr/bin/env python
'''
exabgp_conf.py - a script to create a configuration file for exabgp using mrtparse.

Copyright (C) 2015 greenHippo, LLC.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Authors:
    Tetsumune KISO <t2mune@gmail.com>
    Yoshiyuki YAMAUCHI <info@greenhippo.co.jp>
    Nobuhiro ITOU <js333123@gmail.com>
'''

from mrtparse import *
import sys, re, argparse

flags = 0x00
FLAG_T = {
    'IPv4': 0x01,
    'IPv6': 0x02,
}

def parse_args():
    global flags

    if ('-4' or '--ipv4') in sys.argv:
        flags |= FLAG_T['IPv4']
    if ('-6' or '--ipv6') in sys.argv:
        flags |= FLAG_T['IPv6']
    if not ('-4' or '--ipv4' or '-6' or '--ipv6' in sys.argv):
        flags = FLAG_T['IPv4'] | FLAG_T['IPv6']

    p = argparse.ArgumentParser(
        description='This script converts to ExaBGP-formatted config.')
    p.add_argument('path_to_file',
        help='specify path to MRT-fomatted file')
    p.add_argument(
        '-r', '--router-id', type=str, default='192.168.0.1',
        help='specify router-id')
    p.add_argument(
        '-l', '--local-as', type=int, default=64512,
        help='specify local AS number')
    p.add_argument(
        '-p', '--peer-as', type=int, default=65000,
        help='specify peer AS number')
    p.add_argument(
        '-L', '--local-addr', type=str, default='192.168.1.1',
        help='specify local address')
    p.add_argument(
        '-n', '--neighbor', type=str, default='192.168.1.100',
        help='specify neighbor address')
    p.add_argument(
        '-4', '--ipv4', type=str, default='192.168.1.254',
        metavar='NEXT_HOP', dest='next_hop',
        help='convert IPv4 entries and specify IPv4 next-hop if exists')
    p.add_argument(
        '-6', '--ipv6', type=str, default='2001:db8::1',
        metavar='NEXT_HOP', dest='next_hop6',
        help='convert IPv6 entries and specify IPv6 next-hop if exists''')
    p.add_argument(
        '-a', '--all-entries', default=False, action='store_true',
        help='convert all entries \
            (default: convert only first entry per one prefix)')

    return p.parse_args()

def conv_exabgp_conf(args, d):
    print('''
    neighbor %s {
        router-id %s;
        local-address %s;
        local-as %d;
        peer-as %d;
        graceful-restart;

        static {'''
    % (args.neighbor, args.router_id, args.local_addr, args.local_as, args.peer_as))

    for m in d:
        m = m.mrt

        if m.type != MSG_T['TABLE_DUMP_V2']:
            continue

        if (    m.subtype != TD_V2_ST['RIB_IPV4_UNICAST']
            and m.subtype != TD_V2_ST['RIB_IPV6_UNICAST']):
            continue

        if (m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
            and not (flags & FLAG_T['IPv4'])):
            continue

        if (m.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
            and not (flags & FLAG_T['IPv6'])):
            continue

        route = '            route %s/%d' % (m.rib.prefix, m.rib.plen)

        entry = []
        if args.all_entries is True:
            entry = m.rib.entry
        else:
            entry.append(m.rib.entry[0])

        print_entry(args, entry, m.subtype, route)

    print('''
        }
    }
    ''')

def print_entry(args, entry, subtype, route):
    for e in entry:
        line = route
        for attr in e.attr:
            line += get_bgp_attr(attr)

        if subtype == TD_V2_ST['RIB_IPV4_UNICAST']:
            print('%s next-hop %s;' % (line, args.next_hop))
        elif subtype == TD_V2_ST['RIB_IPV6_UNICAST']:
            print('%s next-hop %s;' % (line, args.next_hop6))

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
        as4_path = ''
        for path_seg in attr.as4_path:
            if path_seg['type'] == AS_PATH_SEG_T['AS_SET']:
                as4_path += '(%s) ' % path_seg['val']
            else:
                as4_path += '%s ' % path_seg['val']
        line += ' as4-path [%s]' % as4_path

    elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']:
        asn = attr.as4_aggr['asn']
        m = r.search(asn)
        if m is not None:
            asn = int(m.group(1)) * 65536 + int(m.group(2))
        line += ' as4-aggregator (%s:%s)' % (str(asn), attr.as4_aggr['id'])

    return line

def main():
    args = parse_args()
    d = Reader(args.path_to_file)
    conv_exabgp_conf(args, d)

if __name__ == '__main__':
    main()
