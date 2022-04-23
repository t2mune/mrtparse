#!/usr/bin/env python
'''
mrt2bgpdump.py - a script to convert MRT format to bgpdump format.

Copyright (C) 2022 Tetsumune KISO

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
            d = datetime.utcfromtimestamp(d).strftime('%m/%d/%y %H:%M:%S')

        if self.pkt_num == True:
            d = '%d|%s' % (self.num, d)

        if self.flag == 'B' or self.flag == 'A':
            self.output.write(
                '%s|%s|%s|%s|%s|%s|%s|%s' % (
                    self.type, d, self.flag, self.peer_ip, self.peer_as, prefix,
                    self.merge_as_path(), self.origin
                )
            )
            if self.verbose == True:
                self.output.write(
                    '|%s|%d|%d|%s|%s|%s|\n' % (
                        next_hop, self.local_pref, self.med, self.comm,
                        self.atomic_aggr, self.merge_aggr()
                    )
                )
            else:
                self.output.write('\n')
        elif self.flag == 'W':
            self.output.write(
                '%s|%s|%s|%s|%s|%s\n' % (
                    self.type, d, self.flag, self.peer_ip, self.peer_as,
                    prefix
                )
            )
        elif self.flag == 'STATE':
            self.output.write(
                '%s|%s|%s|%s|%s|%d|%d\n' % (
                    self.type, d, self.flag, self.peer_ip, self.peer_as,
                    self.old_state, self.new_state
                )
            )

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
        self.ts = list(m['timestamp'])[0]
        self.num = count
        self.org_time = list(m['originated_time'])[0]
        self.peer_ip = m['peer_ip']
        self.peer_as = m['peer_as']
        self.nlri.append('%s/%d' % (m['prefix'], m['length']))
        for attr in m['path_attributes']:
            self.bgp_attr(attr)
        self.print_routes()

    def td_v2(self, m):
        global peer
        self.type = 'TABLE_DUMP2'
        self.flag = 'B'
        self.ts = list(m['timestamp'])[0]
        st = list(m['subtype'])[0]
        if st == TD_V2_ST['PEER_INDEX_TABLE']:
            peer = copy.copy(m['peer_entries'])
        elif (st == TD_V2_ST['RIB_IPV4_UNICAST']
            or st == TD_V2_ST['RIB_IPV4_MULTICAST']
            or st == TD_V2_ST['RIB_IPV6_UNICAST']
            or st == TD_V2_ST['RIB_IPV6_MULTICAST']):
            self.num = m['sequence_number']
            self.nlri.append('%s/%d' % (m['prefix'], m['length']))
            for entry in m['rib_entries']:
                self.org_time = list(entry['originated_time'])[0]
                self.peer_ip = peer[entry['peer_index']]['peer_ip']
                self.peer_as = peer[entry['peer_index']]['peer_as']
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
                for attr in entry['path_attributes']:
                    self.bgp_attr(attr)
                self.print_routes()

    def bgp4mp(self, m, count):
        self.type = 'BGP4MP'
        self.ts = list(m['timestamp'])[0]
        self.num = count
        self.org_time = list(m['timestamp'])[0]
        self.peer_ip = m['peer_ip']
        self.peer_as = m['peer_as']
        st = list(m['subtype'])[0]
        if (st == BGP4MP_ST['BGP4MP_STATE_CHANGE']
            or st == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
            self.flag = 'STATE'
            self.old_state = list(m['old_state'])[0]
            self.new_state = list(m['new_state'])[0]
            self.print_line([], '')
        elif (st == BGP4MP_ST['BGP4MP_MESSAGE']
            or st == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
            or st == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
            or st == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
            if list(m['bgp_message']['type'])[0] != BGP_MSG_T['UPDATE']:
                return
            for attr in m['bgp_message']['path_attributes']:
                self.bgp_attr(attr)
            for withdrawn in m['bgp_message']['withdrawn_routes']:
                self.withdrawn.append(
                    '%s/%d' % (
                        withdrawn['prefix'], withdrawn['length']
                    )
                )
            for nlri in m['bgp_message']['nlri']:
                self.nlri.append(
                    '%s/%d' % (
                        nlri['prefix'], nlri['length']
                    )
                )
            self.print_routes()

    def bgp_attr(self, attr):
        attr_t = list(attr['type'])[0]
        if attr_t == BGP_ATTR_T['ORIGIN']:
            self.origin = ORIGIN_T[list(attr['value'])[0]]
        elif attr_t == BGP_ATTR_T['NEXT_HOP']:
            self.next_hop.append(attr['value'])
        elif attr_t == BGP_ATTR_T['AS_PATH']:
            self.as_path = []
            for seg in attr['value']:
                seg_t = list(seg['type'])[0]
                if seg_t == AS_PATH_SEG_T['AS_SET']:
                    self.as_path.append('{%s}' % ','.join(seg['value']))
                elif seg_t == AS_PATH_SEG_T['AS_CONFED_SEQUENCE']:
                    self.as_path.append('(' + seg['value'][0])
                    self.as_path += seg['value'][1:-1]
                    self.as_path.append(seg['value'][-1] + ')')
                elif seg_t == AS_PATH_SEG_T['AS_CONFED_SET']:
                    self.as_path.append('[%s]' % ','.join(seg['value']))
                else:
                    self.as_path += seg['value']
        elif attr_t == BGP_ATTR_T['MULTI_EXIT_DISC']:
            self.med = attr['value']
        elif attr_t == BGP_ATTR_T['LOCAL_PREF']:
            self.local_pref = attr['value']
        elif attr_t == BGP_ATTR_T['ATOMIC_AGGREGATE']:
            self.atomic_aggr = 'AG'
        elif attr_t == BGP_ATTR_T['AGGREGATOR']:
            self.aggr = '%s %s' % (attr['value']['as'], attr['value']['id'])
        elif attr_t == BGP_ATTR_T['COMMUNITY']:
            self.comm = ' '.join(attr['value'])
        elif attr_t == BGP_ATTR_T['MP_REACH_NLRI']:
            self.next_hop = attr['value']['next_hop']
            if self.type != 'BGP4MP':
                return
            for nlri in attr['value']['nlri']:
                self.nlri.append(
                    '%s/%d' % (
                        nlri['prefix'], nlri['length']
                    )
                )
        elif attr_t == BGP_ATTR_T['MP_UNREACH_NLRI']:
            if self.type != 'BGP4MP':
                return
            for withdrawn in attr['value']['withdrawn_routes']:
                self.withdrawn.append(
                    '%s/%d' % (
                        withdrawn['prefix'], withdrawn['length']
                    )
                )
        elif attr_t == BGP_ATTR_T['AS4_PATH']:
            self.as4_path = []
            for seg in attr['value']:
                seg_t = list(seg['type'])[0]
                if seg_t == AS_PATH_SEG_T['AS_SET']:
                    self.as4_path.append('{%s}' % ','.join(seg['value']))
                elif seg_t == AS_PATH_SEG_T['AS_CONFED_SEQUENCE']:
                    self.as4_path.append('(' + seg['value'][0])
                    self.as4_path += seg['value'][1:-1]
                    self.as4_path.append(seg['value'][-1] + ')')
                elif seg_t == AS_PATH_SEG_T['AS_CONFED_SET']:
                    self.as4_path.append('[%s]' % ','.join(seg['value']))
                else:
                    self.as4_path += seg['value']
        elif attr_t == BGP_ATTR_T['AS4_AGGREGATOR']:
            self.as4_aggr = '%s %s' % (
                attr['value']['as'], attr['value']['id']
            )

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
        if m.err:
            continue
        b = BgpDump(args)
        t = list(m.data['type'])[0]
        if t == MRT_T['TABLE_DUMP']:
            b.td(m.data, count)
        elif t == MRT_T['TABLE_DUMP_V2']:
            b.td_v2(m.data)
        elif t == MRT_T['BGP4MP']:
            b.bgp4mp(m.data, count)
        count += 1

if __name__ == '__main__':
    main()
