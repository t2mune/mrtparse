#!/usr/bin/env python
'''
print_all.py - a script to print a MRT format data using mrtparse.

Copyright (C) 2020 Tetsumune KISO

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

import sys
from optparse import OptionParser
from datetime import *
from mrtparse import *

indt = ' ' * 4
indt_num = 0
contents = ''

def prerror(m):
    print('%s: %s' % (MRT_ERR_C[m.err], m.err_msg))
    if m.err == MRT_ERR_C['MRT Header Error']:
        buf = m.buf
    else:
        buf = m.buf[12:]
    s = ''
    for i in range(len(buf)):
        if isinstance(buf[i], str):
            s += '%02x ' % ord(buf[i])
        else:
            s += '%02x ' % buf[i]

        if (i + 1) % 16 == 0:
            print('    %s' % s)
            s = ''
        elif (i + 1) % 8 == 0:
            s += ' '
    if len(s):
        print('    %s' % s)

def put_lines(*lines):
    global contents
    for line in lines:
        contents += indt * indt_num + line + '\n'

def print_mrt(m):
    global indt_num
    indt_num = 0
    put_lines('MRT Header')

    indt_num += 1

    try:
        subtype = MRT_ST[m.type][m.subtype]
    except KeyError:
        subtype = 'Unknown'

    put_lines(
        'Timestamp: %d(%s)' % (m.ts, datetime.fromtimestamp(m.ts)),
        'Type: %d(%s)' % (m.type, MRT_T[m.type]),
        'Subtype: %d(%s)' % (m.subtype, subtype),
        'Length: %d' % m.len
    )

    if m.type == MRT_T['BGP4MP_ET'] \
        or m.type == MRT_T['ISIS_ET'] \
        or m.type == MRT_T['OSPFv3_ET']:
        put_lines('Microsecond Timestamp: %d' % m.micro_ts)

def print_td(m):
    global indt_num
    indt_num = 0
    put_lines('%s' % MRT_T[m.type])

    indt_num += 1
    put_lines(
        'View Number: %d' % m.td.view,
        'Sequence Number: %d' % m.td.seq,
        'Prefix: %s' % m.td.prefix,
        'Prefix length: %d' % m.td.plen,
        'Status: %d' % m.td.status,
        'Originated Time: %d(%s)' %
        (m.td.org_time, datetime.fromtimestamp(m.td.org_time)),
        'Peer IP Address: %s' % m.td.peer_ip,
        'Peer AS: %s' % m.td.peer_as,
        'Attribute Length: %d' % m.td.attr_len
    )

    for attr in m.td.attr:
        print_bgp_attr(attr, 1)

def print_td_v2(m):
    global indt_num
    indt_num = 0
    put_lines('%s' % TD_V2_ST[m.subtype])

    indt_num += 1
    if m.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
        put_lines(
            'Collector: %s' % m.peer.collector,
            'View Name Length: %d' % m.peer.view_len,
            'View Name: %s' % m.peer.view,
            'Peer Count: %d' % m.peer.count
        )

        for entry in m.peer.entry:
            put_lines(
                'Peer Type: 0x%02x' % entry.type,
                'Peer BGP ID: %s' % entry.bgp_id,
                'Peer IP Address: %s' % entry.ip,
                'Peer AS: %s' % entry.asn
            )

    elif m.subtype == TD_V2_ST['RIB_IPV4_UNICAST'] \
        or m.subtype == TD_V2_ST['RIB_IPV4_MULTICAST'] \
        or m.subtype == TD_V2_ST['RIB_IPV6_UNICAST'] \
        or m.subtype == TD_V2_ST['RIB_IPV6_MULTICAST'] \
        or m.subtype == TD_V2_ST['RIB_IPV4_UNICAST_ADDPATH'] \
        or m.subtype == TD_V2_ST['RIB_IPV4_MULTICAST_ADDPATH'] \
        or m.subtype == TD_V2_ST['RIB_IPV6_UNICAST_ADDPATH'] \
        or m.subtype == TD_V2_ST['RIB_IPV6_MULTICAST_ADDPATH']:
        put_lines(
            'Sequence Number: %d' % m.rib.seq,
            'Prefix Length: %d' % m.rib.plen,
            'Prefix: %s' % m.rib.prefix,
            'Entry Count: %d' % m.rib.count
        )

        for entry in m.rib.entry:
            indt_num = 1
            put_lines(
                'Peer Index: %d' % entry.peer_index,
                'Originated Time: %d(%s)' %
                (entry.org_time, datetime.fromtimestamp(entry.org_time))
            )

            if entry.path_id is not None:
                put_lines('Path Identifier: %d' % entry.path_id)
            put_lines('Attribute Length: %d' % entry.attr_len)

            for attr in entry.attr:
                print_bgp_attr(attr, 1)

    elif m.subtype == TD_V2_ST['RIB_GENERIC'] \
        or m.subtype == TD_V2_ST['RIB_GENERIC_ADDPATH']:
        put_lines(
            'Sequence Number: %d' % m.rib.seq,
            'AFI: %d(%s)' % (m.rib.afi, AFI_T[m.rib.afi]),
            'SAFI: %d(%s)' % (m.rib.safi, SAFI_T[m.rib.safi])
        )

        for nlri in m.rib.nlri:
            print_nlri(nlri, 'NLRI', m.rib.safi)
        put_lines('Entry Count: %d' % m.rib.count)

        for entry in m.rib.entry:
            indt_num = 1
            put_lines(
                'Peer Index: %d' % entry.peer_index,
                'Originated Time: %d(%s)' %
                (entry.org_time, datetime.fromtimestamp(entry.org_time)),
                'Attribute Length: %d' % entry.attr_len
            )

            for attr in entry.attr:
                print_bgp_attr(attr, 1)

def print_bgp4mp(m):
    global indt_num
    indt_num = 0
    put_lines('%s' % BGP4MP_ST[m.subtype])

    indt_num += 1
    put_lines(
        'Peer AS Number: %s' % m.bgp.peer_as,
        'Local AS Number: %s' % m.bgp.local_as,
        'Interface Index: %d' % m.bgp.ifindex,
        'Address Family: %d(%s)' % (m.bgp.af, AFI_T[m.bgp.af]),
        'Peer IP Address: %s' % m.bgp.peer_ip,
        'Local IP Address: %s' % m.bgp.local_ip
    )

    if m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE'] \
        or m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']:
        put_lines(
            'Old State: %d(%s)' % (m.bgp.old_state, BGP_FSM[m.bgp.old_state]),
            'New State: %d(%s)' % (m.bgp.new_state, BGP_FSM[m.bgp.new_state])
        )

    elif m.subtype == BGP4MP_ST['BGP4MP_MESSAGE'] \
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4'] \
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL'] \
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL'] \
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_ADDPATH'] \
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_ADDPATH'] \
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL_ADDPATH'] \
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL_ADDPATH']:
        print_bgp_msg(m.bgp.msg, m.subtype)

def print_bgp_msg(msg, subtype):
    global indt_num
    indt_num = 0
    put_lines('BGP Message')

    indt_num += 1
    put_lines(
        'Marker: -- ignored --',
        'Length: %d' % msg.len,
        'Type: %d(%s)' % (msg.type, BGP_MSG_T[msg.type]),
    )

    if msg.type == BGP_MSG_T['OPEN']:
        put_lines(
            'Version: %d' % msg.ver,
            'My AS: %d' % msg.my_as,
            'Hold Time: %d' % msg.holdtime,
            'BGP Identifier: %s' % msg.bgp_id,
            'Optional Parameter Length: %d' % msg.opt_len
        )

        for opt in msg.opt_params:
            print_bgp_opt_params(opt)

    elif msg.type == BGP_MSG_T['UPDATE']:
        put_lines('Withdrawn Routes Length: %d' % msg.wd_len)
        for withdrawn in msg.withdrawn:
            print_nlri(withdrawn, 'Withdrawn Routes')

        put_lines('Total Path Attribute Length: %d' % msg.attr_len)
        for attr in msg.attr:
            print_bgp_attr(attr, 1)

        indt_num = 1
        for nlri in msg.nlri:
            print_nlri(nlri, 'NLRI')

    elif msg.type == BGP_MSG_T['NOTIFICATION']:
        put_lines(
            'Error Code: %d(%s)' % (msg.err_code, BGP_ERR_C[msg.err_code]),
            'Error Subcode: %d(%s)'
            % (msg.err_subcode, BGP_ERR_SC[msg.err_code][msg.err_subcode]),
            'Data: %s' % msg.data
        )

    elif msg.type == BGP_MSG_T['ROUTE-REFRESH']:
        put_lines(
            'AFI: %d(%s)' % (msg.afi, AFI_T[msg.afi]),
            'Reserved: %d' % msg.rsvd,
            'SAFI: %d(%s)' % (msg.safi, SAFI_T[msg.safi])
        )

def print_bgp_opt_params(opt):
    global indt_num
    indt_num = 1
    put_lines('Parameter Type/Length: %d/%d' % (opt.type, opt.len))

    indt_num += 1
    put_lines('%s' % BGP_OPT_PARAMS_T[opt.type])

    if opt.type != BGP_OPT_PARAMS_T['Capabilities']:
        return

    indt_num += 1
    put_lines(
        'Capability Code: %d(%s)' % (opt.cap_type, BGP_CAP_C[opt.cap_type]),
        'Capability Length: %d' % opt.cap_len
    )

    if opt.cap_type == BGP_CAP_C['Multiprotocol Extensions for BGP-4']:
        put_lines(
            'AFI: %d(%s)' % (opt.multi_ext['afi'], AFI_T[opt.multi_ext['afi']]),
            'Reserved: %d' % opt.multi_ext['rsvd'],
            'SAFI: %d(%s)'
            % (opt.multi_ext['safi'], SAFI_T[opt.multi_ext['safi']])
        )

    elif opt.cap_type == BGP_CAP_C['Route Refresh Capability for BGP-4']:
        pass

    elif opt.cap_type == BGP_CAP_C['Outbound Route Filtering Capability']:
        put_lines(
            'AFI: %d(%s)' % (opt.orf['afi'], AFI_T[opt.orf['afi']]),
            'Reserved: %d' % opt.orf['rsvd'],
            'SAFI: %d(%s)' % (opt.orf['safi'], SAFI_T[opt.orf['safi']]),
            'Number: %d' % opt.orf['number']
        )

        for entry in opt.orf['entry']:
            put_lines(
                'Type: %d' % entry['type'],
                'Send Receive: %d(%s)' %
                (entry['send_recv'], ORF_SEND_RECV[entry['send_recv']])
            )

    elif opt.cap_type == BGP_CAP_C['Graceful Restart Capability']:
        put_lines(
            'Restart Flags: 0x%x' % opt.graceful_restart['flag'],
            'Restart Time in Seconds: %d' % opt.graceful_restart['sec']
        )

        for entry in opt.graceful_restart['entry']:
            put_lines(
                'AFI: %d(%s)' % (entry['afi'], AFI_T[entry['afi']]),
                'SAFI: %d(%s)' % (entry['safi'], SAFI_T[entry['safi']]),
                'Flag: 0x%02x' % entry['flag']
            )

    elif opt.cap_type == BGP_CAP_C['Support for 4-octet AS number capability']:
        put_lines('AS Number: %s' % opt.support_as4)

    elif opt.cap_type == BGP_CAP_C['ADD-PATH Capability']:
        for entry in opt.add_path:
            put_lines(
                'AFI: %d(%s)' % (entry['afi'], AFI_T[entry['afi']]),
                'SAFI: %d(%s)' % (entry['safi'], SAFI_T[entry['safi']]),
                'Send Receive: %d(%s)'
                % (entry['send_recv'], ADD_PATH_SEND_RECV[entry['send_recv']])
            )

def print_bgp_attr(attr, n):
    global indt_num
    indt_num = n
    put_lines(
        'Path Attribute Flags/Type/Length: 0x%02x/%d/%d'
        % (attr.flag, attr.type, attr.len)
    )

    indt_num += 1
    line = '%s' % BGP_ATTR_T[attr.type]

    if attr.type == BGP_ATTR_T['ORIGIN']:
        put_lines(line + ': %d(%s)' % (attr.origin, ORIGIN_T[attr.origin]))

    elif attr.type == BGP_ATTR_T['AS_PATH']:
        put_lines(line)
        indt_num += 1
        for path_seg in attr.as_path:
            put_lines(
                'Path Segment Type: %d(%s)' %
                (path_seg['type'], AS_PATH_SEG_T[path_seg['type']]),
                'Path Segment Length: %d' % path_seg['len'],
                'Path Segment Value: %s' % ' '.join(path_seg['val'])
            )

    elif attr.type == BGP_ATTR_T['NEXT_HOP']:
        put_lines(line + ': %s' % attr.next_hop)

    elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
        put_lines(line + ': %d' % attr.med)

    elif attr.type == BGP_ATTR_T['LOCAL_PREF']:
        put_lines(line + ': %d' % attr.local_pref)

    elif attr.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
        put_lines(line)

    elif attr.type == BGP_ATTR_T['AGGREGATOR']:
        put_lines(line + ': %s %s' % (attr.aggr['asn'], attr.aggr['id']))

    elif attr.type == BGP_ATTR_T['COMMUNITY']:
        put_lines(line + ': %s' % ' '.join(attr.comm))

    elif attr.type == BGP_ATTR_T['ORIGINATOR_ID']:
        put_lines(line + ': %s' % attr.org_id)

    elif attr.type == BGP_ATTR_T['CLUSTER_LIST']:
        put_lines(line + ': %s' % ' '.join(attr.cl_list))

    elif attr.type == BGP_ATTR_T['MP_REACH_NLRI']:
        put_lines(line)
        indt_num += 1
        if 'afi' in attr.mp_reach:
            put_lines(
                'AFI: %d(%s)'
                % (attr.mp_reach['afi'], AFI_T[attr.mp_reach['afi']])
            )

        if 'safi' in attr.mp_reach:
            put_lines(
                'SAFI: %d(%s)' %
                (attr.mp_reach['safi'], SAFI_T[attr.mp_reach['safi']])
            )

            if attr.mp_reach['safi'] == SAFI_T['L3VPN_UNICAST'] \
                or attr.mp_reach['safi'] == SAFI_T['L3VPN_MULTICAST']:
                put_lines('Route Distinguisher: %s' % attr.mp_reach['rd'])

        put_lines('Length: %d' % attr.mp_reach['nlen'])

        if 'next_hop' not in attr.mp_reach:
            return

        next_hop = " ".join(attr.mp_reach['next_hop'])
        put_lines('Next-Hop: %s' % next_hop)

        if 'nlri' in attr.mp_reach:
            for nlri in attr.mp_reach['nlri']:
                print_nlri(nlri, 'NLRI', attr.mp_reach['safi'])

    elif attr.type == BGP_ATTR_T['MP_UNREACH_NLRI']:
        put_lines(line)
        indt_num += 1
        put_lines(
            'AFI: %d(%s)' %
            (attr.mp_unreach['afi'], AFI_T[attr.mp_unreach['afi']]),
            'SAFI: %d(%s)' %
            (attr.mp_unreach['safi'], SAFI_T[attr.mp_unreach['safi']])
        )

        if 'withdrawn' not in attr.mp_unreach:
            return

        for withdrawn in attr.mp_unreach['withdrawn']:
            print_nlri(withdrawn, 'Withdrawn Routes', attr.mp_unreach['safi'])

    elif attr.type == BGP_ATTR_T['EXTENDED COMMUNITIES']:
        ext_comm_list = []
        for ext_comm in attr.ext_comm:
            ext_comm_list.append('0x%016x' % ext_comm)
        put_lines(line + ': %s' % ' '.join(ext_comm_list))

    elif attr.type == BGP_ATTR_T['AS4_PATH']:
        put_lines(line)
        indt_num += 1
        for path_seg in attr.as4_path:
            put_lines(  
                'Path Segment Type: %d(%s)' %
                (path_seg['type'], AS_PATH_SEG_T[path_seg['type']]),
                'Path Segment Length: %d' % path_seg['len'],
                'Path Segment Value: %s' % ' '.join(path_seg['val'])
            )

    elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']:
        put_lines(
            line + ': %s %s' % (attr.as4_aggr['asn'], attr.as4_aggr['id'])
        )

    elif attr.type == BGP_ATTR_T['AIGP']:
        put_lines(line)
        indt_num += 1
        for aigp in attr.aigp:
            put_lines(
                'Type: %d' % aigp['type'],
                'Length: %d' % aigp['len'],
                'Value: %d' % aigp['val']
            )

    elif attr.type == BGP_ATTR_T['ATTR_SET']:
        put_lines(line)
        indt_num += 1
        put_lines('Origin AS: %s' % attr.attr_set['origin_as'])
        for attr in attr.attr_set['attr']:
            print_bgp_attr(attr, 3)

    elif attr.type == BGP_ATTR_T['LARGE_COMMUNITY']:
        put_lines(line + ': %s' % ' '.join(attr.large_comm))

    else:
        line += ': 0x'
        for c in attr.val:
            if isinstance(c, str):
                c = ord(c)
            line += '%02x' % c
        put_lines(line)

def print_nlri(nlri, title, *args):
    global indt_num
    safi = args[0] if len(args) > 0 else 0

    if safi == SAFI_T['L3VPN_UNICAST'] \
        or safi == SAFI_T['L3VPN_MULTICAST']:
        put_lines('%s' % title)
        indt_num += 1
        plen = nlri.plen - (len(nlri.label) * 3 + 8) * 8
        l_all = []
        l_val = []
        for label in nlri.label:
            l_all.append('0x%06x' % label)
            l_val.append(str(label >> 4))
        if nlri.path_id is not None:
            put_lines('Path Identifier: %d' % nlri.path_id)
        put_lines(
            'Label: %s(%s)' % (' '.join(l_all), ' '.join(l_val)),
            'Route Distinguisher: %s' % nlri.rd,
            'Prefix: %s/%d' % (nlri.prefix, plen)
        )
        indt_num -= 1
    else:
        if nlri.path_id is not None:
            put_lines('%s' % title)
            indt_num += 1
            put_lines(
                'Path Identifier: %d' % nlri.path_id,
                'Prefix: %s/%d' % (nlri.prefix, nlri.plen)
            )
            indt_num -= 1
        else:
            put_lines('%s: %s/%d' % (title, nlri.prefix, nlri.plen))

def main():
    global contents

    if len(sys.argv) != 2:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    d = Reader(sys.argv[1])

    # if you want to use 'asdot+' or 'asdot' for AS numbers,
    # comment out either line below.
    # default is 'asplain'.
    #
    # as_repr(AS_REPR['asdot+'])
    # as_repr(AS_REPR['asdot'])
    for m in d:
        contents = ''
        m = m.mrt
        print('---------------------------------------------------------------')
        if m.err == MRT_ERR_C['MRT Header Error']:
            prerror(m)
            continue
        print_mrt(m)
        sys.stdout.write(contents)

        contents = ''
        if m.err == MRT_ERR_C['MRT Data Error']:
            prerror(m)
            continue
        if m.type == MRT_T['TABLE_DUMP']:
            print_td(m)
        elif m.type == MRT_T['TABLE_DUMP_V2']:
            print_td_v2(m)
        elif m.type == MRT_T['BGP4MP'] \
            or m.type == MRT_T['BGP4MP_ET']:
            print_bgp4mp(m)
        sys.stdout.write(contents)

if __name__ == '__main__':
    main()
