#!/usr/bin/env python

import sys
from optparse import OptionParser
from datetime import *
from mrtparse import *

def print_mrt(m):
    print('---------------------------------------------------------------')
    print('MRT Header')
    print('Timestamp: %d(%s)' % (m.ts, datetime.fromtimestamp(m.ts)))
    print('    Type: %d(%s)' % (m.type, val_dict(MSG_T, m.type)))
    print('    Subtype: %d(%s)' %
        (m.subtype, val_dict(MSG_ST, m.type, m.subtype)))
    print('    Length: %d' % m.len)

    if (   m.type == MSG_T['BGP4MP_ET']
        or m.type == MSG_T['ISIS_ET']
        or m.type == MSG_T['OSPFv3_ET']):
        print('    Microsecond Timestamp: %d' % m.micro_ts)

def print_bgp4mp(m):
    print('%s' % BGP4MP_ST[m.subtype])
    print('    Peer AS Number: %s' % m.bgp.peer_as)
    print('    Local AS Number: %s' % m.bgp.local_as)
    print('    Interface Index: %d' % m.bgp.ifindex)
    print('    Address Family: %d(%s)' %
        (m.bgp.af, val_dict(AFI_T, m.bgp.af)))
    print('    Peer IP Address: %s' % m.bgp.peer_ip)
    print('    Local IP Address: %s' % m.bgp.local_ip)

    if (   m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
        or m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
        print('    Old State: %d(%s)' %
            (m.bgp.old_state, val_dict(BGP_FSM, m.bgp.old_state)))
        print('    New State: %d(%s)' %
            (m.bgp.new_state, val_dict(BGP_FSM, m.bgp.new_state)))
    elif ( m.subtype == BGP4MP_ST['BGP4MP_MESSAGE']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
        print_bgp_msg(m)

def print_bgp_msg(m):
    print('BGP Message')
    print('    Marker: -- ignored --')
    print('    Length: %d' % m.bgp.msg.len)
    print('    Type: %d(%s)' %
        (m.bgp.msg.type, val_dict(BGP_MSG_T, m.bgp.msg.type)))

    if m.bgp.msg.type == BGP_MSG_T['OPEN']:
        print('    Version: %d' % (m.bgp.msg.ver))
        print('    My AS: %d' % (m.bgp.msg.my_as))
        print('    Hold Time: %d' % (m.bgp.msg.holdtime))
        print('    BGP Identifier: %s' % (m.bgp.msg.bgp_id))
        print('    Optional Parameter Length: %d' % (m.bgp.msg.opt_len))
        print_bgp_opt_params(m.bgp.msg.opt_params)
    elif m.bgp.msg.type == BGP_MSG_T['UPDATE']:
        print('    Withdrawn Routes Length: %d' % (m.bgp.msg.wd_len))

        for withdrawn in m.bgp.msg.withdrawn:
            print('    Withdrawn Route: %s/%d' %
                (withdrawn.prefix, withdrawn.plen))
        print('    Total Path Attribute Length: %d' % (m.bgp.msg.attr_len))

        print_bgp_attr(m.bgp.msg.attr)

        for nlri in m.bgp.msg.nlri:
            print('    NLRI: %s/%d' % (nlri.prefix, nlri.plen))
    elif m.bgp.msg.type == BGP_MSG_T['NOTIFICATION']:
        print('     Error Code: %d(%s)' % 
            (m.bgp.msg.err_code, val_dict(BGP_ERR_C, m.bgp.msg.err_code)))
        print('     Error Subcode: %d(%s)' % 
            (m.bgp.msg.err_subcode,
            val_dict(BGP_ERR_SC, m.bgp.msg.err_code, m.bgp.msg.err_subcode)))

def print_td_v2(m):
    print('%s' % TD_V2_ST[m.subtype])

    if m.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
        print('    Collector: %s' % m.peer.collector)
        print('    View Name Length: %d' % m.peer.view_len)
        print('    View Name: %s' % m.peer.view)
        print('    Peer Count: %d' % m.peer.count)
        for entry in m.peer.entry:
            print('    Peer Type: 0x%02x' % entry.type)
            print('    Peer BGP ID: %s' % entry.bgp_id)
            print('    Peer IP Address: %s' % entry.ip)
            print('    Peer AS: %s' % entry.asn)
    elif ( m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
        or m.subtype == TD_V2_ST['RIB_IPV4_MULTICAST']
        or m.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
        or m.subtype == TD_V2_ST['RIB_IPV6_MULTICAST']):
        print('    Sequence Number: %d' % m.rib.seq)
        print('    Prefix Length: %d' % m.rib.plen)
        print('    Prefix: %s' % m.rib.prefix)
        print('    Entry Count: %d' % m.rib.count)
        for entry in m.rib.entry:
            print('    Peer Index: %d' % entry.peer_index)
            print('    Originated Time: %d(%s)' %
                (entry.org_time, datetime.fromtimestamp(entry.org_time)))
            print('    Attribute Length: %d' % entry.attr_len)
            print_bgp_attr(entry.attr)

def print_bgp_opt_params(opt_params):
    for opt in opt_params:
        print('    Parameter Type/Length: %d/%d' % (opt.type, opt.len))
        print('        %s' % val_dict(BGP_OPT_PARAMS_T, opt.type))

        if opt.type != BGP_OPT_PARAMS_T['Capabilities']:
            return

        print('            Capability Code: %d(%s)' %
            (opt.cap_type, val_dict(CAP_CODE_T, opt.cap_type)))
        print('            Capability Length: %d' % opt.cap_len)

        if opt.cap_type == CAP_CODE_T['Multiprotocol Extensions for BGP-4']:
            print('            AFI: %d(%s)' %
                (opt.multi_ext['afi'], val_dict(AFI_T, opt.multi_ext['afi'])))
            print('            Reserved: %d' % opt.multi_ext['reserved'])
            print('            SAFI: %d(%s)' %
                (opt.multi_ext['safi'], val_dict(SAFI_T, opt.multi_ext['safi'])))
        elif opt.cap_type == CAP_CODE_T['Outbound Route Filtering Capability']:
            print('            AFI: %d(%s)' %
                (opt.orf['afi'], val_dict(AFI_T, opt.orf['afi'])))
            print('            Reserved: %d' % opt.orf['reserved'])
            print('            SAFI: %d(%s)' %
                (opt.orf['safi'], val_dict(SAFI_T, opt.orf['safi'])))
            print('            Number: %d' % opt.orf['number_of_orfs'])
            print('            Type: %d' % opt.orf['orf_type'])
            print('            Send Receive: %d' % opt.orf['send_receive'])
        elif opt.cap_type == CAP_CODE_T['Support for 4-octet AS number capability']:
            print('            AS Number: %d' % opt.support_for_as['as_number'])
        elif opt.cap_type == CAP_CODE_T['Route Refresh Capability for BGP-4']:
            pass
        elif opt.cap_type == CAP_CODE_T['Graceful Restart Capability']:
            print('            Restart Timers: %d' % opt.graceful_restart['timer'])
            if opt.cap_len > 2:
                print('            AFI: %d(%s)' %
                    (opt.graceful_restart['afi'], val_dict(AFI_T, opt.graceful_restart['afi'])))
                print('            SAFI: %d(%s)' %
                    (opt.graceful_restart['safi'], val_dict(SAFI_T, opt.graceful_restart['safi'])))
                print('            Flag: %d' % opt.graceful_restart['flags_for_afi'])
        elif opt.cap_type == CAP_CODE_T['Multiple routes to a destination capability']:
            while opt.cap_len > 3:
                print('            Prefix: %d' % self.multi_routes_dest['prefix'])
                opt.cap_len -= 1
        elif opt.cap_type == CAP_CODE_T['Extended Next Hop Encoding']:
            while opt.cap_len > 5:
                print('            NLRI AFI: %d' % (self.self.ext_next_hop['nlri_afi'] ))
                print('            NLRI SAFI: %d' % (self.self.ext_next_hop['nlri_safi'] ))
                print('            Nexthop AFI: %d' % (self.self.ext_next_hop['nexthop_afi'] ))
                opt.cap_len -= 6

def print_bgp_attr(attr_list):
    for attr in attr_list:
        print('    Path Attribute Flag/Type/Length: 0x%02x/%d/%d' %
            (attr.flag, attr.type, attr.len))

        line = '        %s: ' % val_dict(BGP_ATTR_T, attr.type)
        if attr.type == BGP_ATTR_T['ORIGIN']:
            line += '%d(%s)' % (attr.origin, val_dict(ORIGIN_T, attr.origin))
        elif attr.type == BGP_ATTR_T['AS_PATH']:
            line += '%s' % ' '.join(attr.as_path)
        elif attr.type == BGP_ATTR_T['NEXT_HOP']:
            line += '%s' % attr.next_hop
        elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
            line += '%d' % attr.med
        elif attr.type == BGP_ATTR_T['LOCAL_PREF']:
            line += '%d' % attr.local_pref
        elif attr.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
            pass
        elif attr.type == BGP_ATTR_T['AGGREGATOR']:
            line += '%s %s' % (attr.aggr['asn'], attr.aggr['id'])
        elif attr.type == BGP_ATTR_T['COMMUNITY']:
            line += '%s' % ' '.join(attr.comm)
        elif attr.type == BGP_ATTR_T['ORIGINATOR_ID']:
            line += '%s' % attr.org_id
        elif attr.type == BGP_ATTR_T['CLUSTER_LIST']:
            line += '%s' % attr.cl_list
        elif attr.type == BGP_ATTR_T['EXTENDED_COMMUNITIES']:
            ext_comm_list = []
            for ext_comm in attr.ext_comm:
                ext_comm_list.append('0x%016x' % ext_comm)
            line += '%s' % ' '.join(ext_comm_list)
        elif attr.type == BGP_ATTR_T['AS4_PATH']:
            line += '%s' % ' '.join(attr.as_path)
        elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']:
            line += '%s %s' % (attr.aggr['asn'], attr.aggr['id'])
        print(line)

        if attr.type == BGP_ATTR_T['MP_REACH_NLRI']:
            print('        AFI: %d(%s), SAFI: %d(%s)' %
                (attr.mp_reach['afi'], val_dict(AFI_T, attr.mp_reach['afi']),
                 attr.mp_reach['safi'], val_dict(SAFI_T, attr.mp_reach['safi'])))
            print('        Length: %d, Next-Hop: %s' %
                (attr.mp_reach['nlen'], attr.mp_reach['next_hop']))
            for nlri in attr.mp_reach['nlri']:
                print('        NLRI: %s/%d' % (nlri.prefix, nlri.plen))
        elif attr.type == BGP_ATTR_T['MP_UNREACH_NLRI']:
            print('        AFI: %d(%s), SAFI: %d(%s)' %
                (attr.mp_unreach['afi'], val_dict(AFI_T, attr.mp_unreach['afi']),
                 attr.mp_unreach['safi'], val_dict(SAFI_T, attr.mp_unreach['safi'])))
            for withdrawn in attr.mp_unreach['withdrawn']:
                print('        Withdrawn Route: %s/%d' %
                    (withdrawn.prefix, withdrawn.plen))

def main():
    if len(sys.argv) != 2:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    d = Reader(sys.argv[1])
    for m in d:
        print_mrt(m)
        if (   m.type == MSG_T['BGP4MP']
            or m.type == MSG_T['BGP4MP_ET']):
            print_bgp4mp(m)
        elif m.type == MSG_T['TABLE_DUMP_V2']:
            print_td_v2(m)

if __name__ == '__main__':
    main()
