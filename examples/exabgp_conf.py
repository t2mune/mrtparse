#!/usr/bin/env python

from mrtparse import *
import sys, re

if len(sys.argv) != 2:
    print "Usage: %s FILENAME" % sys.argv[0]
    exit(1)

f = open(sys.argv[1], 'rb')
d = Reader(f)
router_id  = '192.168.0.20'
local_addr = '192.168.1.20'
neighbor   = '192.168.1.100'
nexthop    = '192.168.1.254'
local_as   = 65000
peer_as    = 64512
indent     = '    '

print '''
neighbor %s {
    router-id %s;
    local-address %s;
    local-as %d;
    peer-as %d;
    graceful-restart;

    static {''' \
% (neighbor, router_id, local_addr, local_as, peer_as)

r = re.compile("([0-9]+)\.([0-9]+)")

for m in d:
    if m.type == MSG_T['TD_V2']:
        if m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']:
            print '        route %s/%d' % (m.rib.prefix, m.rib.plen),
            print 'next-hop %s' % nexthop,
            for attr in m.rib.entry[0].attr:
                if attr.type == BGP_ATTR_T['ORIGIN'] and attr.len != 0:
                    print 'origin %s' % ORIGIN_T[attr.val],
                elif attr.type == BGP_ATTR_T['AS_PATH'] and attr.len != 0:
                    val = attr.val.replace('{', '(')
                    val = val.replace('}', ')')
                    print 'as-path [%s]' % val,
                elif attr.type == BGP_ATTR_T['NEXT_HOP'] and attr.len != 0:
                    pass
                elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC'] and attr.len != 0:
                    print 'med %d' % attr.val,
                elif attr.type == BGP_ATTR_T['LOCAL_PREF'] and attr.len != 0:
                    print 'local-preference %d' % attr.val,
                elif attr.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
                    pass
                elif attr.type == BGP_ATTR_T['AGGREGATOR']  and attr.len != 0:
                    asn, bgp_id = attr.val.split(' ')
                    m = r.search(asn)
                    if m is not None:
                        asn = int(m.group(1)) * 65536 + int(m.group(2))
                    print 'aggregator (%s:%s)' % (asn, bgp_id),
                elif attr.type == BGP_ATTR_T['COMMUNITIES'] and attr.len != 0:
                    print 'community [%s]' % attr.val,
                elif attr.type == BGP_ATTR_T['ORIGINATOR_ID'] and attr.len != 0:
                    print 'originator-id %s' % attr.val,
                elif attr.type == BGP_ATTR_T['CLUSTER_LIST'] and attr.len != 0:
                    print 'cluster-list [%s]' % attr.val,
            print ';'
print '''
    }
}
'''
