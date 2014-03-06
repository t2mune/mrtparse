#!/usr/bin/env python
'''
print_all.py is a script to print a MRT format data using mrtparse.

See https://github.com/YoshiyukiYamauchi/mrtparse for more informations.
This script is published under a Apache License, Version 2.0.
Created by
    Tetsumune KISO <t2mune@gmail.com>,
    Yoshiyuki YAMAUCHI <info@greenhippo.co.jp>,
    Nobuhiro ITOU <js333123@gmail.com>.
Copyright (C) greenHippo, LLC. All rights reserved.
'''

import sys
from optparse import OptionParser
from datetime import *
from mrtparse import *

indt = 0

def prline(line):
    global indt
    print('    ' * indt + line)

def print_mrt(m):
    global indt
    indt = 0
    prline('---------------------------------------------------------------')
    prline('MRT Header')

    indt += 1
    prline('Timestamp: %d(%s)' %
        (m.ts, datetime.fromtimestamp(m.ts)))
    prline('Type: %d(%s)' % (m.type, val_dict(MSG_T, m.type)))
    prline('Subtype: %d(%s)' %
        (m.subtype, val_dict(MSG_ST, m.type, m.subtype)))
    prline('Length: %d' % m.len)

    if (   m.type == MSG_T['BGP4MP_ET']
        or m.type == MSG_T['ISIS_ET']
        or m.type == MSG_T['OSPFv3_ET']):
        prline('Microsecond Timestamp: %d' % m.micro_ts)

def print_td(m):
    global indt
    indt = 0
    prline('%s' % MSG_T[m.type])

    indt += 1
    prline('View Number: %d' % m.td.view)
    prline('Sequence Number: %d' % m.td.seq)
    prline('Prefix: %s' % m.td.prefix)
    prline('Prefix length: %d' % m.td.plen)
    prline('Status: %d' % m.td.status)
    prline('Originated Time: %d(%s)' %
        (m.td.org_time,
         datetime.fromtimestamp(m.td.org_time)))
    prline('Peer IP Address: %s' % m.td.peer_ip)
    prline('Peer AS: %s' % m.td.peer_as)
    prline('Attribute Length: %d' % m.td.attr_len)
    for attr in m.td.attr:
        print_bgp_attr(attr, 1)

def print_td_v2(m):
    global indt
    indt = 0
    prline('%s' % TD_V2_ST[m.subtype])

    indt += 1
    if m.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
        prline('Collector: %s' % m.peer.collector)
        prline('View Name Length: %d' % m.peer.view_len)
        prline('View Name: %s' % m.peer.view)
        prline('Peer Count: %d' % m.peer.count)

        for entry in m.peer.entry:
            prline('Peer Type: 0x%02x' % entry.type)
            prline('Peer BGP ID: %s' % entry.bgp_id)
            prline('Peer IP Address: %s' % entry.ip)
            prline('Peer AS: %s' % entry.asn)

    elif ( m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
        or m.subtype == TD_V2_ST['RIB_IPV4_MULTICAST']
        or m.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
        or m.subtype == TD_V2_ST['RIB_IPV6_MULTICAST']):
        prline('Sequence Number: %d' % m.rib.seq)
        prline('Prefix Length: %d' % m.rib.plen)
        prline('Prefix: %s' % m.rib.prefix)
        prline('Entry Count: %d' % m.rib.count)

        for entry in m.rib.entry:
            prline('Peer Index: %d' % entry.peer_index)
            prline('Originated Time: %d(%s)' %
                (entry.org_time,
                 datetime.fromtimestamp(entry.org_time)))
            prline('Attribute Length: %d' % entry.attr_len)
            for attr in entry.attr:
                print_bgp_attr(attr, 1)

def print_bgp4mp(m):
    global indt
    indt = 0
    prline('%s' % BGP4MP_ST[m.subtype])

    indt += 1
    prline('Peer AS Number: %s' % m.bgp.peer_as)
    prline('Local AS Number: %s' % m.bgp.local_as)
    prline('Interface Index: %d' % m.bgp.ifindex)
    prline('Address Family: %d(%s)' %
        (m.bgp.af, val_dict(AFI_T, m.bgp.af)))
    prline('Peer IP Address: %s' % m.bgp.peer_ip)
    prline('Local IP Address: %s' % m.bgp.local_ip)

    if (   m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
        or m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
        prline('Old State: %d(%s)' %
            (m.bgp.old_state, val_dict(BGP_FSM, m.bgp.old_state)))
        prline('New State: %d(%s)' %
            (m.bgp.new_state, val_dict(BGP_FSM, m.bgp.new_state)))

    elif ( m.subtype == BGP4MP_ST['BGP4MP_MESSAGE']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
        print_bgp_msg(m.bgp.msg, m.subtype)

def print_bgp_msg(msg, subtype):
    global indt
    indt = 0
    prline('BGP Message')

    indt += 1
    prline('Marker: -- ignored --')
    prline('Length: %d' % msg.len)
    prline('Type: %d(%s)' %
        (msg.type, val_dict(BGP_MSG_T, msg.type)))

    if msg.type == BGP_MSG_T['OPEN']:
        prline('Version: %d' % msg.ver)
        prline('My AS: %d' % msg.my_as)
        prline('Hold Time: %d' % msg.holdtime)
        prline('BGP Identifier: %s' % msg.bgp_id)
        prline('Optional Parameter Length: %d' % msg.opt_len)

        for opt in msg.opt_params:
            print_bgp_opt_params(opt)

    elif msg.type == BGP_MSG_T['UPDATE']:
        prline('Withdrawn Routes Length: %d' % msg.wd_len)
        for withdrawn in msg.withdrawn:
            prline('Withdrawn Route: %s/%d' %
                (withdrawn.prefix, withdrawn.plen))

        prline('Total Path Attribute Length: %d' % msg.attr_len)
        for attr in msg.attr:
            print_bgp_attr(attr, 1)

        indt = 1
        for nlri in msg.nlri:
            prline('NLRI: %s/%d' % (nlri.prefix, nlri.plen))

    elif msg.type == BGP_MSG_T['NOTIFICATION']:
        prline('Error Code: %d(%s)' % 
            (msg.err_code,
             val_dict(BGP_ERR_C, msg.err_code)))
        prline('Error Subcode: %d(%s)' % 
            (msg.err_subcode,
            val_dict(BGP_ERR_SC, msg.err_code, msg.err_subcode)))

    elif msg.type == BGP_MSG_T['ROUTE-REFRESH']:
        prline('AFI: %d(%s)' % 
            (msg.afi,
             val_dict(AFI_T, msg.afi)))
        prline('Reserved: %d' % (msg.reserved))
        prline('SAFI: %d(%s)' % 
            (msg.safi,
             val_dict(SAFI_T, msg.safi)))

def print_bgp_opt_params(opt):
    global indt
    indt = 1
    prline('Parameter Type/Length: %d/%d' % (opt.type, opt.len))

    indt += 1
    prline('%s' % val_dict(BGP_OPT_PARAMS_T, opt.type))

    if opt.type != BGP_OPT_PARAMS_T['Capabilities']:
        return

    indt += 1
    prline('Capability Code: %d(%s)' %
        (opt.cap_type, val_dict(BGP_CAP_C, opt.cap_type)))
    prline('Capability Length: %d' % opt.cap_len)

    if opt.cap_type == BGP_CAP_C['Multiprotocol Extensions for BGP-4']:
        prline('AFI: %d(%s)' %
            (opt.multi_ext['afi'],
             val_dict(AFI_T, opt.multi_ext['afi'])))
        prline('Reserved: %d' % opt.multi_ext['reserved'])
        prline('SAFI: %d(%s)' %
            (opt.multi_ext['safi'],
             val_dict(SAFI_T, opt.multi_ext['safi'])))

    elif opt.cap_type == BGP_CAP_C['Route Refresh Capability for BGP-4']:
        pass

    elif opt.cap_type == BGP_CAP_C['Outbound Route Filtering Capability']:
        prline('AFI: %d(%s)' %
            (opt.orf['afi'],
             val_dict(AFI_T, opt.orf['afi'])))
        prline('Reserved: %d' % opt.orf['rsvd'])
        prline('SAFI: %d(%s)' %
            (opt.orf['safi'],
             val_dict(SAFI_T, opt.orf['safi'])))
        prline('Number: %d' % opt.orf['number'])

        for entry in opt.orf['entry']:
            prline('Type: %d' % entry['type'])
            prline('Send Receive: %d(%s)' %
                (entry['send_recv'],
                 val_dict(ORF_SEND_RECV, entry['send_recv'])))

    elif opt.cap_type == BGP_CAP_C['Graceful Restart Capability']:
        prline('Restart Flags: 0x%x' %
            opt.graceful_restart['flag'])
        prline('Restart Time in Seconds: %d' %
            opt.graceful_restart['sec'])

        for entry in opt.graceful_restart['entry']:
            prline('AFI: %d(%s)' %
                (entry['afi'], val_dict(AFI_T, entry['afi'])))
            prline('SAFI: %d(%s)' %
                (entry['safi'], val_dict(SAFI_T, entry['safi'])))
            prline('Flag: 0x%02x' % entry['flag'])

    elif opt.cap_type == BGP_CAP_C['Support for 4-octet AS number capability']:
        prline('AS Number: %s' % opt.support_as4)

def print_bgp_attr(attr, n):
    global indt
    indt = n
    prline('Path Attribute Flags/Type/Length: 0x%02x/%d/%d' %
        (attr.flag, attr.type, attr.len))

    indt += 1
    line = '%s: ' % val_dict(BGP_ATTR_T, attr.type)
    if attr.type == BGP_ATTR_T['ORIGIN']:
        prline(line + '%d(%s)' % (attr.origin, val_dict(ORIGIN_T, attr.origin)))
    elif(    attr.type == BGP_ATTR_T['AS_PATH']
        or attr.type == BGP_ATTR_T['AS4_PATH']):
        prline(line)
        indt += 1
        for path_seg in attr.as_path:
            prline('Path Segment Type: %d(%s)' %
                (path_seg['type'],
                 val_dict(AS_PATH_SEG_T, path_seg['type'])))
            prline('Path Segment Length: %d' % path_seg['len'])
            prline('Path Segment Value: %s' % path_seg['val'])
    elif attr.type == BGP_ATTR_T['NEXT_HOP']:
        prline(line + '%s' % attr.next_hop)
    elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
        prline(line + '%d' % attr.med)
    elif attr.type == BGP_ATTR_T['LOCAL_PREF']:
        prline(line + '%d' % attr.local_pref)
    elif attr.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
        prline(line)
    elif attr.type == BGP_ATTR_T['AGGREGATOR']:
        prline(line + '%s %s' % (attr.aggr['asn'], attr.aggr['id']))
    elif attr.type == BGP_ATTR_T['COMMUNITY']:
        prline(line + '%s' % ' '.join(attr.comm))
    elif attr.type == BGP_ATTR_T['ORIGINATOR_ID']:
        prline(line + '%s' % attr.org_id)
    elif attr.type == BGP_ATTR_T['CLUSTER_LIST']:
        prline(line + '%s' % ' '.join(attr.cl_list))
    elif attr.type == BGP_ATTR_T['MP_REACH_NLRI']:
        prline(line)
        indt += 1
        prline('AFI: %d(%s), SAFI: %d(%s)' %
            (attr.mp_reach['afi'],
             val_dict(AFI_T, attr.mp_reach['afi']),
             attr.mp_reach['safi'],
             val_dict(SAFI_T, attr.mp_reach['safi'])))

        if (   attr.mp_reach['safi'] == SAFI_T['L3VPN_UNICAST']
            or attr.mp_reach['safi'] == SAFI_T['L3VPN_MULTICAST']):
            prline('Route Distinguisher: %s' % attr.mp_reach['rd'])

        prline('Length: %d, Next-Hop: %s' %
            (attr.mp_reach['nlen'], attr.mp_reach['next_hop']))

        for nlri in attr.mp_reach['nlri']:
            print_nlri(nlri, attr.mp_reach['safi'], 'NLRI')
    elif attr.type == BGP_ATTR_T['MP_UNREACH_NLRI']:
        prline(line)
        indt += 1
        prline('AFI: %d(%s), SAFI: %d(%s)' %
            (attr.mp_unreach['afi'],
             val_dict(AFI_T, attr.mp_unreach['afi']),
             attr.mp_unreach['safi'],
             val_dict(SAFI_T, attr.mp_unreach['safi'])))

        for withdrawn in attr.mp_unreach['withdrawn']:
            print_nlri(withdrawn, attr.mp_unreach['safi'], 'Withdrawn Routes')
    elif attr.type == BGP_ATTR_T['EXTENDED_COMMUNITIES']:
        ext_comm_list = []
        for ext_comm in attr.ext_comm:
            ext_comm_list.append('0x%016x' % ext_comm)
        prline(line + '%s' % ' '.join(ext_comm_list))
    elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']:
        prline(line + '%s %s' % (attr.aggr['asn'], attr.aggr['id']))
    elif attr.type == BGP_ATTR_T['ATTR_SET']:
        prline(line)
        indt += 1
        prline('Origin AS: %s' % attr.attr_set['origin_as'])
        for attr in attr.attr_set['attr']:
            print_bgp_attr(attr, 3)
    else:
        line += '0x'
        for c in attr.val:
            if isinstance(c, str):
                c = ord(c)
            line += '%02x' % c
        prline(line)

def print_nlri(nlri, safi, title):
    global indt
    if (   safi == SAFI_T['L3VPN_UNICAST']
        or safi == SAFI_T['L3VPN_MULTICAST']):
        prline('%s:' % title)
        indt += 1
        plen = nlri.plen - (len(nlri.label) * 3 + 8) * 8
        l = []
        for label in nlri.label:
            l.append(str(label >> 4))
        prline('Label: %s' % ' '.join(l))
        prline('Route Distinguisher: %s' % nlri.rd)
        prline('Prefix: %s/%d' % (nlri.prefix, plen))
        indt -= 1
    else:
        prline('%s: %s/%d' % (title, nlri.prefix, nlri.plen))

def main():
    if len(sys.argv) != 2:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    d = Reader(sys.argv[1])

    # if you want to use 'asdot+' or 'asdot' for AS numbers,
    # comment out eithre line below.
    # default is 'asplain'.
    #
    # d.as_rep = AS_REP['asdot+']
    # d.as_rep = AS_REP['asdot']
    for m in d:
        print_mrt(m)
        if m.type == MSG_T['TABLE_DUMP']:
            print_td(m)
        elif m.type == MSG_T['TABLE_DUMP_V2']:
            print_td_v2(m)
        elif ( m.type == MSG_T['BGP4MP']
            or m.type == MSG_T['BGP4MP_ET']):
            print_bgp4mp(m)

if __name__ == '__main__':
    main()
