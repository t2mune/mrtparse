#!/usr/bin/env python
'''
mrt2bgpdump.py - a script to convert MRT format to bgpdump format.

Copyright (C) 2016 greenHippo, LLC.

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

import sys, argparse, copy
from datetime import *
from mrtparse import *

peer = None

def parse_args():
    p = argparse.ArgumentParser(
        description='This script converts to bgpdump format.')
    p.add_argument(
        '-m', dest='verbose', default=False, action='store_true',
        help='one-line per entry with unix timestamps')
    p.add_argument(
        '-M', dest='verbose', action='store_false',
        help='one-line per entry with human readable timestamps(default format)')
    p.add_argument(
        '-O', dest='output', default=sys.stdout, nargs='?', metavar='file',
        type=argparse.FileType('w'),
        help='output to a specified file')
    p.add_argument(
        '-s', dest='output', action='store_const', const=sys.stdout,
        help='output to STDOUT(default output)')
    p.add_argument(
        '-v', dest='output', action='store_const', const=sys.stderr,
        help='output to STDERR')
    p.add_argument(
        '-t', dest='ts_format', default='dump', choices=['dump', 'change'],
        help='timestamps for RIB dumps reflect the time of the dump \
            or the last route modification(default: dump)')
    p.add_argument(
        '-p', dest='pkt_num', default=False, action='store_true',
        help='show packet index at second position')
    p.add_argument(
        'path_to_file',
        help='specify path to MRT format file')
    return p.parse_args()

class BgpDump:
    __slots__ = [
        'verbose', 'output', 'ts_format', 'pkt_num', 'type', 'num', 'ts',
        'org_time', 'flag', 'peer_ip', 'peer_as', 'nlri', 'withdrawn',
        'as_path', 'origin', 'next_hop', 'local_pref', 'med', 'comm',
        'atomic_aggr', 'aggr', 'as4_path', 'as4_aggr', 'old_state', 'new_state',
    ]

    def __init__(self, args):
        self.verbose = args.verbose
        self.output = args.output
        self.ts_format = args.ts_format
        self.pkt_num = args.pkt_num
        self.type = ''
        self.num = 0
        self.ts = 0
        self.org_time = 0
        self.flag = ''
        self.peer_ip = ''
        self.peer_as = 0
        self.nlri = []
        self.withdrawn = []
        self.as_path = []
        self.origin = ''
        self.next_hop = []
        self.local_pref = 0
        self.med = 0
        self.comm = ''
        self.atomic_aggr = 'NAG'
        self.aggr = ''
        self.as4_path = []
        self.as4_aggr = ''
        self.old_state = 0
        self.new_state = 0

    def print_line(self, prefix, next_hop):
        if self.ts_format == 'dump':
            d = self.ts
        else:
            d = self.org_time

        if self.verbose:
            d = str(d)
        else:
            d = datetime.utcfromtimestamp(d).\
                strftime('%m/%d/%y %H:%M:%S')

        if self.pkt_num == True:
            d = '%d|%s' % (self.num, d)

        if self.flag == 'B' or self.flag == 'A':
            self.output.write('%s|%s|%s|%s|%s|%s|%s|%s' % (
                self.type, d, self.flag, self.peer_ip, self.peer_as, prefix,
                self.merge_as_path(), self.origin))
            if self.verbose == True:
                self.output.write('|%s|%d|%d|%s|%s|%s|\n' % (
                    next_hop, self.local_pref, self.med, self.comm,
                    self.atomic_aggr, self.merge_aggr()))
            else:
                self.output.write('\n')
        elif self.flag == 'W':
            self.output.write('%s|%s|%s|%s|%s|%s\n' % (
                self.type, d, self.flag, self.peer_ip, self.peer_as,
                prefix))
        elif self.flag == 'STATE':
            self.output.write('%s|%s|%s|%s|%s|%d|%d\n' % (
                self.type, d, self.flag, self.peer_ip, self.peer_as,
                self.old_state, self.new_state))

    def print_routes(self):
        for withdrawn in self.withdrawn:
            if self.type == 'BGP4MP':
                self.flag = 'W'
            self.print_line(withdrawn, '')
        for nlri in self.nlri:
            if self.type == 'BGP4MP':
                self.flag = 'A'
            for next_hop in self.next_hop:
                self.print_line(nlri, next_hop)

    def td(self, m, count):
        self.type = 'TABLE_DUMP'
        self.flag = 'B'
        self.ts = m.ts
        self.num = count
        self.org_time = m.td.org_time
        self.peer_ip = m.td.peer_ip
        self.peer_as = m.td.peer_as
        self.nlri.append('%s/%d' % (m.td.prefix, m.td.plen))
        for attr in m.td.attr:
            self.bgp_attr(attr)
        self.print_routes()

    def td_v2(self, m):
        global peer
        self.type = 'TABLE_DUMP2'
        self.flag = 'B'
        self.ts = m.ts
        if m.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
            peer = copy.copy(m.peer.entry)
        elif (m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
            or m.subtype == TD_V2_ST['RIB_IPV4_MULTICAST']
            or m.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
            or m.subtype == TD_V2_ST['RIB_IPV6_MULTICAST']):
            self.num = m.rib.seq
            self.nlri.append('%s/%d' % (m.rib.prefix, m.rib.plen))
            for entry in m.rib.entry:
                self.org_time = entry.org_time
                self.peer_ip = peer[entry.peer_index].ip
                self.peer_as = peer[entry.peer_index].asn
                self.as_path = []
                self.origin = ''
                self.next_hop = []
                self.local_pref = 0
                self.med = 0
                self.comm = ''
                self.atomic_aggr = 'NAG'
                self.aggr = ''
                self.as4_path = []
                self.as4_aggr = ''
                for attr in entry.attr:
                    self.bgp_attr(attr)
                self.print_routes()

    def bgp4mp(self, m, count):
        self.type = 'BGP4MP'
        self.ts = m.ts
        self.num = count
        self.org_time = m.ts
        self.peer_ip = m.bgp.peer_ip
        self.peer_as = m.bgp.peer_as
        if (m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
            or m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
            self.flag = 'STATE'
            self.old_state = m.bgp.old_state
            self.new_state = m.bgp.new_state
            self.print_line([], '')
        elif (m.subtype == BGP4MP_ST['BGP4MP_MESSAGE']
            or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
            or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
            or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
            if m.bgp.msg.type != BGP_MSG_T['UPDATE']:
                return
            for attr in m.bgp.msg.attr:
                self.bgp_attr(attr)
            for withdrawn in m.bgp.msg.withdrawn:
                self.withdrawn.append(
                    '%s/%d' % (withdrawn.prefix, withdrawn.plen))
            for nlri in m.bgp.msg.nlri:
                self.nlri.append('%s/%d' % (nlri.prefix, nlri.plen))
            self.print_routes()

    def bgp_attr(self, attr):
        if attr.type == BGP_ATTR_T['ORIGIN']:
            self.origin = ORIGIN_T[attr.origin]
        elif attr.type == BGP_ATTR_T['NEXT_HOP']:
            self.next_hop.append(attr.next_hop)
        elif attr.type == BGP_ATTR_T['AS_PATH']:
            self.as_path = []
            for seg in attr.as_path:
                if seg['type'] == AS_PATH_SEG_T['AS_SET']:
                    self.as_path.append('{%s}' % ','.join(seg['val']))
                elif seg['type'] == AS_PATH_SEG_T['AS_CONFED_SEQUENCE']:
                    self.as_path.append('(' + seg['val'][0])
                    self.as_path += seg['val'][1:-1]
                    self.as_path.append(seg['val'][-1] + ')')
                elif seg['type'] == AS_PATH_SEG_T['AS_CONFED_SET']:
                    self.as_path.append('[%s]' % ','.join(seg['val']))
                else:
                    self.as_path += seg['val']
        elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
            self.med = attr.med
        elif attr.type == BGP_ATTR_T['LOCAL_PREF']:
            self.local_pref = attr.local_pref
        elif attr.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
            self.atomic_aggr = 'AG'
        elif attr.type == BGP_ATTR_T['AGGREGATOR']:
            self.aggr = '%s %s' % (attr.aggr['asn'], attr.aggr['id'])
        elif attr.type == BGP_ATTR_T['COMMUNITY']:
            self.comm = ' '.join(attr.comm)
        elif attr.type == BGP_ATTR_T['MP_REACH_NLRI']:
            self.next_hop = attr.mp_reach['next_hop']
            if self.type != 'BGP4MP':
                return
            for nlri in attr.mp_reach['nlri']:
                self.nlri.append('%s/%d' % (nlri.prefix, nlri.plen))
        elif attr.type == BGP_ATTR_T['MP_UNREACH_NLRI']:
            if self.type != 'BGP4MP':
                return
            for withdrawn in attr.mp_unreach['withdrawn']:
                self.withdrawn.append(
                    '%s/%d' % (withdrawn.prefix, withdrawn.plen))
        elif attr.type == BGP_ATTR_T['AS4_PATH']:
            self.as4_path = []
            for seg in attr.as4_path:
                if seg['type'] == AS_PATH_SEG_T['AS_SET']:
                    self.as4_path.append('{%s}' % ','.join(seg['val']))
                elif seg['type'] == AS_PATH_SEG_T['AS_CONFED_SEQUENCE']:
                    self.as4_path.append('(' + seg['val'][0])
                    self.as4_path += seg['val'][1:-1]
                    self.as4_path.append(seg['val'][-1] + ')')
                elif seg['type'] == AS_PATH_SEG_T['AS_CONFED_SET']:
                    self.as4_path.append('[%s]' % ','.join(seg['val']))
                else:
                    self.as4_path += seg['val']
        elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']:
            self.as4_aggr = '%d %s' % (attr.as4_aggr['asn'], attr.as4_aggr['ip'])

    def merge_as_path(self):
        if len(self.as4_path):
            n = len(self.as_path) - len(self.as4_path)
            return ' '.join(self.as_path[:n] + self.as4_path)
        else:
            return ' '.join(self.as_path)

    def merge_aggr(self):
        if len(self.as4_aggr):
            return self.as4_aggr
        else:
            return self.aggr

def main():
    args = parse_args()
    d = Reader(args.path_to_file)
    count = 0
    for m in d:
        m = m.mrt
        if m.err:
            continue
        b = BgpDump(args)
        if m.type == MRT_T['TABLE_DUMP']:
            b.td(m, count)
        elif m.type == MRT_T['TABLE_DUMP_V2']:
            b.td_v2(m)
        elif m.type == MRT_T['BGP4MP']:
            b.bgp4mp(m, count)
        count += 1

if __name__ == '__main__':
    main()
