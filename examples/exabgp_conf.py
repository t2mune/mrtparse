#!/usr/bin/env python

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
    
    r = re.compile("([0-9]+)\.([0-9]+)")
    
    for m in d:
        if m.type == MSG_T['TABLE_DUMP_V2']:
            if m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']:
                line = '            route %s/%d' % (m.rib.prefix, m.rib.plen)
                for attr in m.rib.entry[0].attr:
                    if attr.type == BGP_ATTR_T['ORIGIN'] and attr.len != 0:
                        line += ' origin %s' % ORIGIN_T[attr.origin]
                    elif attr.type == BGP_ATTR_T['AS_PATH'] and attr.len != 0: 
                        as_path = ' '.join(attr.as_path)
                        as_path = as_path.replace('{', '(')
                        as_path = as_path.replace('}', ')')
                        line += ' as-path [%s]' % as_path
                    elif attr.type == BGP_ATTR_T['NEXT_HOP'] and attr.len != 0:
                        pass
                    elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC'] and attr.len != 0:
                        line += ' med %d' % attr.med
                    elif attr.type == BGP_ATTR_T['LOCAL_PREF'] and attr.len != 0:
                        line += ' local-preference %d' % attr.local_pref
                    elif attr.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
                        line += ' atomic-aggregate'
                    elif attr.type == BGP_ATTR_T['AGGREGATOR']  and attr.len != 0:
                        asn = attr.aggr['asn']
                        m = r.search(asn)
                        if m is not None:
                            asn = int(m.group(1)) * 65536 + int(m.group(2))
                        line += ' aggregator (%s:%s)' % (str(asn), attr.aggr['id'])
                    elif attr.type == BGP_ATTR_T['COMMUNITIES'] and attr.len != 0:
                        comm = ' '.join(attr.comm)
                        line += ' community [%s]' % comm
                    elif attr.type == BGP_ATTR_T['ORIGINATOR_ID'] and attr.len != 0:
                        line += ' originator-id %s' % attr.org_id
                    elif attr.type == BGP_ATTR_T['CLUSTER_LIST'] and attr.len != 0:
                        line += ' cluster-list [%s]' % ' '.join(attr.cl_list)
                    elif attr.type == BGP_ATTR_T['EXTENDED_COMMUNITIES'] and attr.len != 0:
                        ext_comm_list = []
                        for ext_comm in attr.ext_comm:
                            ext_comm_list.append('0x%016x' % ext_comm)
                        line += ' extended-community [%s]' % ' '.join(ext_comm_list)
                    elif attr.type == BGP_ATTR_T['AS4_PATH'] and attr.len != 0:
                        as_path = ' '.join(attr.as_path)
                        as_path = as_path.replace('{', '(')
                        as_path = as_path.replace('}', ')')
                        line += ' as-path [%s]' % as_path
                    elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']  and attr.len != 0:
                        asn = attr.aggr['asn']
                        m = r.search(asn)
                        if m is not None:
                            asn = int(m.group(1)) * 65536 + int(m.group(2))
                        line += ' aggregator (%s:%s)' % (str(asn), attr.aggr['id'])
                print('%s next-hop %s;' % (line, nexthop))
    print('''
        }
    }
    ''')

def main():
    if len(sys.argv) != 2:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    d = Reader(sys.argv[1])
    make_exabgp_conf(d)

if __name__ == '__main__':
    main()
