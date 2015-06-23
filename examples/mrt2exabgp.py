#!/usr/bin/env python
'''
mrt2exabgp.py - a script to convert MRT format to ExaBGP format.

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
import sys, re, argparse, time

flags = 0x00
FLAG_T = {
    'IPv4': 0x01,
    'IPv6': 0x02,
    'ALL' : 0x04,
    'API' : 0x08,
    'API-GROUP' : 0x10,
}

def parse_args():
    global flags

    if '-4' in sys.argv:
        flags |= FLAG_T['IPv4']
    if '-6' in sys.argv:
        flags |= FLAG_T['IPv6']
    if '-4' not in sys.argv and '-6' not in sys.argv:
        flags = FLAG_T['IPv4'] | FLAG_T['IPv6']
    if '-a' in sys.argv:
        flags |= FLAG_T['ALL']
    if '-A' in sys.argv:
        flags |= FLAG_T['API']
    if '-G' in sys.argv:
        flags |= FLAG_T['API'] | FLAG_T['API-GROUP']

    p = argparse.ArgumentParser(
        description='This script converts to ExaBGP format config.')
    p.add_argument(
        'path_to_file',
        help='specify path to MRT format file')
    p.add_argument(
        '-r', type=str, default='192.168.0.1', dest='router_id',
        help='specify router-id (default: 192.168.0.1)')
    p.add_argument(
        '-l', type=int, default=64512, dest='local_as',
        help='specify local AS number (default: 64512)')
    p.add_argument(
        '-p', type=int, default=65000, dest='peer_as',
        help='specify peer AS number (default: 65000)')
    p.add_argument(
        '-L', type=str, default='192.168.1.1', dest='local_addr',
        help='specify local address (default: 192.168.1.1)')
    p.add_argument(
        '-n', type=str, default='192.168.1.100', dest='neighbor',
        help='specify neighbor address (default: 192.168.1.100)')
    p.add_argument(
        '-4', type=str, nargs='?', metavar='NEXT_HOP', dest='next_hop',
        help='convert IPv4 entries and use IPv4 next-hop if specified')
    p.add_argument(
        '-6', type=str, nargs='?', metavar='NEXT_HOP', dest='next_hop6',
        help='convert IPv6 entries and use IPv6 next-hop if specified''')
    p.add_argument(
        '-a', default=False, action='store_true',
        help='convert all entries \
            (default: convert only first entry per one prefix)')
    p.add_argument(
        '-A', action='store_false',
        help='convert to ExaBGP API format')
    p.add_argument(
        '-G', type=int, default=1000000, nargs='?', metavar='NUM', dest='api_grp_num',
        help='convert to ExaBGP API format and group updates with the same attributes for each spceified the number of prefixes (default: 1000000)')

    if re.search('^-', sys.argv[-1]): 
        r = p.parse_args()
    else:
        r = p.parse_args(sys.argv[:-1])
        r.path_to_file=sys.argv[-1]

    return r

def mrt_type_check(m):
    if m.type != MSG_T['TABLE_DUMP_V2']:
        return 1

    if (    m.subtype != TD_V2_ST['RIB_IPV4_UNICAST']
        and m.subtype != TD_V2_ST['RIB_IPV6_UNICAST']):
        return 1

    if (m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
        and not (flags & FLAG_T['IPv4'])):
        return 1

    if (m.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
        and not (flags & FLAG_T['IPv6'])):
        return 1

    return 0

def print_conf_header(args):
    print('''\
neighbor %s {
    router-id %s;
    local-address %s;
    local-as %d;
    peer-as %d;
    graceful-restart;
    aigp enable;

    static {'''
    % (args.neighbor, args.router_id, args.local_addr, \
        args.local_as, args.peer_as))

def print_conf_footer():
    print('    }\n}')

def print_api_grp(d):
    for k in d:
        sys.stdout.write('announce attribute%s nlri %s\n' \
            % (k, ' '.join(d[k])))
        sys.stdout.flush()

def conv_format(args, d):
    global next_hop

    attr_grp = {}
    n = 1

    if flags & FLAG_T['API'] == 0:
        print_conf_header(args)

    for m in d:
        m = m.mrt

        if mrt_type_check(m):
            continue

        entry = []
        if flags & FLAG_T['ALL']:
            entry = m.rib.entry
        else:
            entry.append(m.rib.entry[0])

        line = ''
        for e in entry:
            next_hop = ''
            for a in e.attr:
                line += get_bgp_attr(args, m.subtype, a)
            
            if flags & FLAG_T['API-GROUP']:
                attr_grp.setdefault('%s next-hop %s' % (line, next_hop), [])\
                    .append('%s/%d' % (m.rib.prefix, m.rib.plen))
            elif flags & FLAG_T['API']:
                sys.stdout.write('announce route %s/%d%s next-hop %s\n' \
                    % (m.rib.prefix, m.rib.plen, line, next_hop))
                sys.stdout.flush()
            else:
                print('        route %s/%d%s next-hop %s;' \
                    % (m.rib.prefix, m.rib.plen, line, next_hop))

        if flags & FLAG_T['API-GROUP'] and n == args.api_grp_num:
            print_api_grp(attr_grp)
            attr_grp = {}
            n = 0
        n += 1

    if flags & FLAG_T['API-GROUP']:
        print_api_grp(attr_grp)

    if flags & FLAG_T['API']:
        while True:
            time.sleep(1)
    else:
        print_conf_footer()

def get_bgp_attr(args, subtype, attr):
    global next_hop

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
        next_hop = args.next_hop if args.next_hop else attr.next_hop

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

    elif attr.type == BGP_ATTR_T['MP_REACH_NLRI']:
        next_hop = attr.mp_reach['next_hop'][0]
        if subtype == TD_V2_ST['RIB_IPV4_UNICAST'] and args.next_hop:
            next_hop = args.next_hop
        elif subtype == TD_V2_ST['RIB_IPV6_UNICAST'] and args.next_hop6:
            next_hop = args.next_hop6

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

    elif attr.type == BGP_ATTR_T['AIGP']:
        line += ' aigp %d' % attr.aigp[0]['val']

    return line

def main():
    args = parse_args()
    d = Reader(args.path_to_file)
    conv_format(args, d)

if __name__ == '__main__':
    main()

