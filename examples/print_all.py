#!/usr/bin/env python

from mrtparse import *
from datetime import *
import sys

if len(sys.argv) != 2:
    print "Usage: %s FILENAME" % sys.argv[0]
    exit(1)

f = open(sys.argv[1], 'rb')
d = Reader(f)
for m in d:
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

    if (   m.type == MSG_T['BGP4MP']
        or m.type == MSG_T['BGP4MP_ET']):
        print '%s' % msg_subtype
        print '    Peer AS Number: %s' % m.bgp.peer_as
        print '    Local AS Number: %s' % m.bgp.local_as
        print '    Interface Index: %d' % m.bgp.ifindex
        print '    Address Family: %d(%s)' % (m.bgp.af, TD_ST[m.bgp.af])
        print '    Peer IP Address: %s' % m.bgp.peer_ip
        print '    Local IP Address: %s' % m.bgp.local_ip

        if (   m.subtype == BGP4MP_ST['BGP4MP_MESSAGE']
            or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
            or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
            or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
            print 'BGP Message'
            print '    Marker: -- ignored --'
            print '    Length: %d' % m.bgp.msg.len
            print '    Type: %d(%s)' % (m.bgp.msg.type, BGP_MSG_T[m.bgp.msg.type])

            if m.bgp.msg.type == BGP_MSG_T['UPDATE']:
                print '    Withdrawn Routes Length: %d' % (m.bgp.msg.wd_len)
                for withdrawn in m.bgp.msg.withdrawn:
                    print '    Withdrawn Routes: %s/%d' % (withdrawn.prefix, withdrawn.plen)
                print '    Total Path Attribute Length: %d' % (m.bgp.msg.attr_len)
                for attr in m.bgp.msg.attr:
                    print '    Path Attribute Flag/Type/Length: 0x%02x/%d/%d' % (
                        attr.flag, attr.type, attr.len)
                    print '    %s: ' % BGP_ATTR_T[attr.type],
                    if attr.type == BGP_ATTR_T['ORIGIN']:
                        print '%d(%s)' % (attr.val, ORIGIN_T[attr.val])
                    elif attr.len != 0:
                        print attr.val
                for nlri in m.bgp.msg.nlri:
                    print '    NLRI: %s/%d' % (nlri.prefix, nlri.plen)
        elif ( m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
            or m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
            print '    Old State: %d(%s)' % (
                m.bgp.old_state, BGP_FSM[m.bgp.old_state])
            print '    New State: %d(%s)' % (
                m.bgp.new_state, BGP_FSM[m.bgp.new_state])
    elif m.type == MSG_T['TD_V2']:
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

                for attr in entry.attr:
                    print '    Path Attribute Flag/Type/Length: 0x%02x/%d/%d' % (
                        attr.flag, attr.type, attr.len)
                    print '    %s: ' % BGP_ATTR_T[attr.type],
                    if attr.type == BGP_ATTR_T['ORIGIN']:
                        print '%d(%s)' % (attr.val, ORIGIN_T[attr.val])
                    elif attr.len != 0:
                        print attr.val
