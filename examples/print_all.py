#!/usr/bin/env python

import sys
from optparse import OptionParser
from datetime import *
from mrtparse import *

def print_mrt(m):
    if m.type in MSG_T:
        msg_type = MSG_T[m.type]
    else:
        msg_type = 'UNKNOWN'

    if (m.type in MSG_ST
        and m.subtype in MSG_ST[m.type]):
        msg_subtype = MSG_ST[m.type][m.subtype]
    else:
        msg_subtype = 'UNKNOWN'

    print '---------------------------------------------------------------'
    print 'MRT Header'
    print '    Timestamp: %d(%s)' % (m.ts, datetime.fromtimestamp(m.ts))
    print '    Type: %d(%s)' % (m.type, msg_type)
    print '    Subtype: %d(%s)' % (m.subtype, msg_subtype)
    print '    Length: %d' % m.len

    if (   m.type == MSG_T['BGP4MP_ET']
        or m.type == MSG_T['ISIS_ET']
        or m.type == MSG_T['OSPFv3_ET']):
        print '    Microsecond Timestamp: %d' % m.micro_ts

def print_bgp4mp(m):
    print '%s' % BGP4MP_ST[m.subtype]
    print '    Peer AS Number: %s' % m.bgp.peer_as
    print '    Local AS Number: %s' % m.bgp.local_as
    print '    Interface Index: %d' % m.bgp.ifindex
    print '    Address Family: %d(%s)' % (m.bgp.af, TD_ST[m.bgp.af])
    print '    Peer IP Address: %s' % m.bgp.peer_ip
    print '    Local IP Address: %s' % m.bgp.local_ip

    if (   m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
        or m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
        print '    Old State: %d(%s)' % (
            m.bgp.old_state, BGP_FSM[m.bgp.old_state])
        print '    New State: %d(%s)' % (
            m.bgp.new_state, BGP_FSM[m.bgp.new_state])
    elif ( m.subtype == BGP4MP_ST['BGP4MP_MESSAGE']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
        print_bgp_msg(m)

def print_bgp_msg(m):
    print 'BGP Message'
    print '    Marker: -- ignored --'
    print '    Length: %d' % m.bgp.msg.len
    print '    Type: %d(%s)' % (m.bgp.msg.type, BGP_MSG_T[m.bgp.msg.type])

    if m.bgp.msg.type == BGP_MSG_T['UPDATE']:
        print '    Withdrawn Routes Length: %d' % (m.bgp.msg.wd_len)

        for withdrawn in m.bgp.msg.withdrawn:
            print '    Withdrawn Routes: %s/%d' % (withdrawn.prefix, withdrawn.plen)
        print '    Total Path Attribute Length: %d' % (m.bgp.msg.attr_len)

        print_bgp_attr(m)

        for nlri in m.bgp.msg.nlri:
            print '    NLRI: %s/%d' % (nlri.prefix, nlri.plen)

def print_td_v2(m):
    print '%s' % TD_V2_ST[m.subtype]

    if m.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
        print '    Collector: %s' % m.peer.collector
        print '    View Name Length: %d' % m.peer.view_len
        print '    View Name: %s' % m.peer.view
        print '    Peer Count: %d' % m.peer.count

        for entry in m.peer.entry:
            print '    Peer Type: 0x%x' % entry.type
            print '    Peer BGP ID: %s' % entry.bgp_id
            print '    Peer IP Address: %s' % entry.ip
            print '    Peer AS: %s' % entry.asn
    elif ( m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
        or m.subtype == TD_V2_ST['RIB_IPV4_MULTICAST']
        or m.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
        or m.subtype == TD_V2_ST['RIB_IPV6_MULTICAST']):
        print '    Sequence Number: %d' % m.rib.seq
        print '    Prefix Length: %d' % m.rib.plen
        print '    Prefix: %s' % m.rib.prefix
        print '    Entry Count: %d' % m.rib.count

        for entry in m.rib.entry:
            print '    Peer Index: %d' % entry.peer_index
            print '    Originated Time: %d(%s)' % (
                entry.org_time, datetime.fromtimestamp(entry.org_time))
            print '    Attribute Length: %d' % entry.attr_len
            print_bgp_attr(m)

def print_bgp_attr(m):
    for attr in m.bgp.msg.attr:
        print '    Path Attribute Flag/Type/Length: 0x%02x/%d/%d' % (
            attr.flag, attr.type, attr.len)
        print '    %s:' % BGP_ATTR_T[attr.type],

        if attr.type == BGP_ATTR_T['ORIGIN']:
            print '%d(%s)' % (attr.origin, ORIGIN_T[attr.origin]),
        elif attr.type == BGP_ATTR_T['AS_PATH']:
            for seg in attr.as_path:
                print '%s' % seg,
        elif attr.type == BGP_ATTR_T['NEXT_HOP']:
            print '%s' % attr.next_hop,
        elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
            print '%d' % attr.med,
        elif attr.type == BGP_ATTR_T['LOCAL_PREF']:
            print '%d' % attr.local_pref,
        elif attr.type == BGP_ATTR_T['AGGREGATOR']:
            print '%s %s' % (attr.aggr['asn'], attr.aggr['ip']),
        elif attr.type == BGP_ATTR_T['COMMUNITIES']:
            for comm in attr.comm:
                print '%s' % comm,
        elif attr.type == BGP_ATTR_T['ORIGINATOR_ID']:
            print '%s' % attr.org_id,
        elif attr.type == BGP_ATTR_T['CLUSTER_LIST']:
            print '%s' % attr.cl_list,
        elif attr.type == BGP_ATTR_T['EXTENDED_COMMUNITIES']:
            for comm in attr.comm:
                print '%s' % comm,
        elif attr.type == BGP_ATTR_T['AS4_PATH']:
            for seg in attr.as_path:
                print '%s' % seg,
        elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']:
            print '%s %s' % (attr.aggr['asn'], attr.aggr['ip']),
        print

def main():
    if len(sys.argv) != 2:
        print "Usage: %s FILENAME" % sys.argv[0]
        exit(1)

    f = open(sys.argv[1], 'rb')
    d = Reader(f)

    for m in d:
        print_mrt(m)

        if (   m.type == MSG_T['BGP4MP']
            or m.type == MSG_T['BGP4MP_ET']):
            print_bgp4mp(m)
        elif m.type == MSG_T['TD_V2']:
            print_td_v2(m)

if __name__ == '__main__':
    main()
