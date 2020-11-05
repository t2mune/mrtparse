#!/usr/bin/env python
'''
mrt2exabgp.py - a script to convert MRT format to ExaBGP format.

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

from mrtparse import *
import sys, re, argparse, time

FLAG_T = {
    'IPv4': 0x01,
    'IPv6': 0x02,
    'ALL' : 0x04,
    'SINGLE' : 0x08,
    'API' : 0x10,
    'API_GROUP' : 0x20,
    'API_PROG' : 0x40,
}

class NotDisplay(Exception):
    pass

def print_conf_header(args):
    """
    Print the configuration for the current peer.

    Args:
    """
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
    """
    Print all available footer

    Args:
    """
    print('    }\n}')

def print_api_prog_header():
    """
    Print the api header.

    Args:
    """
    print('''\
#!/usr/bin/env python

import sys
import time

msgs = [''')

def print_api_prog_footer():
    """
    Print api footer.

    Args:
    """
    print('''\
]

while msgs:
    msg = msgs.pop(0)
    if isinstance(msg, str):
        sys.stdout.write(msg + '\\n')
        sys.stdout.flush()
    else:
        time.sleep(msg)

while True:
    time.sleep(1)
''')

def parse_args():
    """
    Parse command line arguments.

    Args:
    """
    global flags

    p = argparse.ArgumentParser(
        description='This script converts to ExaBGP format.')
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
        help='convert IPv4 entries and change IPv4 next-hop if specified')
    p.add_argument(
        '-6', type=str, nargs='?', metavar='NEXT_HOP', dest='next_hop6',
        help='convert IPv6 entries and change IPv6 next-hop if specified''')
    p.add_argument(
        '-a', default=False, action='store_true',
        help='convert all entries \
            (default: convert only first entry per one prefix)')
    p.add_argument(
        '-s', default=False, action='store_true',
        help='convert only entries from a single asn \
            (the peer asn, specify as -p PEER_ASN)')
    p.add_argument(
        '-A', action='store_false',
        help='convert to ExaBGP API format')
    p.add_argument(
        '-G', type=int, default=1000000, nargs='?', metavar='NUM',
        dest='api_grp_num', help='convert to ExaBGP API format '
        + 'and group updates with the same attributes '
        + 'for each spceified the number of prefixes '
        + 'using "announce attributes ..." syntax (default: 1000000)')
    p.add_argument(
        '-P', action='store_false',
        help='convert to ExaBGP API program')

    if re.search('^-', sys.argv[-1]): 
        r = p.parse_args()
    else:
        r = p.parse_args(sys.argv[:-1])
        r.path_to_file=sys.argv[-1]

    flags = 0x00
    if '-4' in sys.argv:
        flags |= FLAG_T['IPv4']
    if '-6' in sys.argv:
        flags |= FLAG_T['IPv6']
    if '-4' not in sys.argv and '-6' not in sys.argv:
        flags = FLAG_T['IPv4'] | FLAG_T['IPv6']
    if '-a' in sys.argv:
        flags |= FLAG_T['ALL']
    if '-s' in sys.argv:
        flags |= FLAG_T['SINGLE']
    if '-A' in sys.argv:
        flags |= FLAG_T['API']
    if '-G' in sys.argv:
        flags |= FLAG_T['API'] | FLAG_T['API_GROUP']
    if '-P' in sys.argv:
        flags |= FLAG_T['API'] | FLAG_T['API_PROG']
    return (r, flags)

def conv_format(args, flags, d):
    """
    Formats data format of a dt.

    Args:
        flags: (int): write your description
        d: (todo): write your description
    """
    params = {}
    params['flags'] = flags
    params['next_hop'] = ''
    params['pre_line'] = ''
    params['post_line'] = ''
    params['prefix_num'] = 1
    params['prefix_before'] = ''
    params['ts_before'] = -1
    params['mp_withdrawn'] = None
    params['mp_nlri'] = None
    params['api_grp_syntax'] = 'attributes'
    params['api_grp'] = {}

    if flags & FLAG_T['API'] == 0:
        print_conf_header(args)
    elif flags & FLAG_T['API_PROG']:
        print_api_prog_header()
        params['pre_line'] = '\''
        params['post_line'] = '\','

    for m in d:
        if m.err:
            continue

        if m.data['type'][0] == MRT_T['TABLE_DUMP_V2'] \
            or m.data['type'][0] == MRT_T['TABLE_DUMP']:
            print_route_td(args, params, m.data)
        elif m.data['type'][0] == MRT_T['BGP4MP'] \
            or m.data['type'][0] == MRT_T['BGP4MP_ET']:
            params['flags'] |= FLAG_T['API'] | FLAG_T['API_GROUP']
            print_route_bgp4mp(args, params, m.data)

    if params['flags'] & FLAG_T['API'] == 0:
        print_conf_footer()
    else:
        if params['flags'] & FLAG_T['API_GROUP']:
            print_api_grp(args, params)

        if params['flags'] & FLAG_T['API_PROG']:
            print_api_prog_footer()
        else:
            while True:
                time.sleep(1)

    return 0

def print_route_td(args, params, m):
    """
    Print route information about route

    Args:
        params: (dict): write your description
        m: (todo): write your description
    """
    entry = []

    if m['type'][0] == MRT_T['TABLE_DUMP_V2']:
        if m['subtype'][0] == TD_V2_ST['RIB_IPV4_UNICAST']:
            if not params['flags'] & FLAG_T['IPv4']:
                return
        elif m['subtype'][0] == TD_V2_ST['RIB_IPV6_UNICAST']:
            if not params['flags'] & FLAG_T['IPv6']:
                return
        else:
            return

        prefix = '%s/%d' % (m['prefix'], m['prefix_length'])
        if flags & FLAG_T['ALL']:
            entry = m['rib_entries']
        else:
            entry.append(m['rib_entries'][0])

    elif m['type'][0] == MRT_T['TABLE_DUMP']:
        if m['subtype'][0] == TD_ST['AFI_IPv4']:
            if not params['flags'] & FLAG_T['IPv4']:
                return
        elif m['subtype'][0] == TD_ST['AFI_IPv6']:
            if not params['flags'] & FLAG_T['IPv6']:
                return
        else:
            return

        prefix = '%s/%d' % (m['prefix'], m['prefix_length'])
        if params['flags'] & FLAG_T['ALL'] == 0:
            if prefix == params['prefix_before']:
                return
            else:
                entry.append(m)
                params['prefix_before'] = prefix
        else:
            entry.append(m)

    for e in entry:
        line = ''
        params['next_hop'] = ''

        try:
            for attr in e['path_attributes']:
                line += get_bgp_attr(args, params, m, attr)

        except NotDisplay:
            continue

        if not params['next_hop']:
            continue

        if params['flags'] & FLAG_T['API_GROUP']:
            params['api_grp'].setdefault(
                '%s next-hop %s' % (line, params['next_hop']), {}
            ).update({'%s' % prefix: None})
        elif params['flags'] & FLAG_T['API']:
            sys.stdout.write(
                '%sannounce route %s%s next-hop %s%s\n' % (
                    params['pre_line'], prefix, line, params['next_hop'],
                    params['post_line']
                )
            )
            sys.stdout.flush()
        else:
            print(
                '        route %s%s next-hop %s;' % (
                    prefix, line, params['next_hop']
                )
            )

    if params['flags'] & FLAG_T['API_GROUP'] \
        and params['prefix_num'] == args.api_grp_num:
        print_api_grp(args, params)
        params['api_grp'] = {}
        params['prefix_num'] = 0

    params['prefix_num'] += 1

def print_api_grp(args, params):
    """
    Print the api information.

    Args:
        params: (dict): write your description
    """
    for k in params['api_grp']:
        sys.stdout.write(
            '%sannounce %s%s nlri %s%s\n' % (
                params['pre_line'], params['api_grp_syntax'], k,
                ' '.join(params['api_grp'][k].keys()), params['post_line']
            )
        )
        sys.stdout.flush()

def print_route_bgp4mp(args, params, m):
    """
    Show bgp route parameters

    Args:
        params: (dict): write your description
        m: (todo): write your description
    """
    params['next_hop'] = ''
    params['mp_withdrawn'] = []
    params['mp_nlri'] = []

    if flags & FLAG_T['API_GROUP'] == 0:
        sys.stderr.write(
            'Error: BGP4MP/BGP4MP_ET is only suuported ' \
            + 'by API Grouping format.\n'
        )
        sys.stderr.write('Error: You must run with -G option.\n')
        if params['flags'] & FLAG_T['API_PROG']:
            print_api_prog_footer()
        else:
            print_conf_footer()
        exit(1)

    if m['subtype'][0] == BGP4MP_ST['BGP4MP_STATE_CHANGE'] \
        or m['subtype'][0] == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']:
        return

    msg = m['bgp_message']

    if msg['type'][0] != BGP_MSG_T['UPDATE']:
        return

    attr_line = ''

    try:
        for attr in msg['path_attributes']:
            attr_line += get_bgp_attr(args, params, m, attr)

    except NotDisplay:
        return

    wd_line = ''
    for wd in params['mp_withdrawn']:
        wd_line += ' %s/%s' % (wd['prefix'], wd['prefix_length'])

    if len(msg['withdrawn_routes']) and params['flags'] & FLAG_T['IPv4']:
        for wd in msg['withdrawn_routes']:
            wd_line += ' %s/%s' % (wd['prefix'], wd['prefix_length'])

    if len(wd_line):
        nh_line = ''
        if params['next_hop']:
            nh_line = ' next-hop %s' % params['next_hop']
        sys.stdout.write(
            '%swithdrawn %s%s%s nlri%s%s\n' % (
                params['pre_line'], params['api_grp_syntax'], attr_line,
                nh_line, wd_line, params['post_line']
            )
        )

    nlri_line = ''
    for nlri in params['mp_nlri']:
        nlri_line += ' %s/%s' % (nlri['prefix'], nlri['prefix_length'])

    if len(msg['nlri']) and params['flags'] & FLAG_T['IPv4']:
        for nlri in msg['nlri']:
            nlri_line += ' %s/%s' % (nlri['prefix'], nlri['prefix_length'])

    if len(nlri_line):
        if params['next_hop']:
            sys.stdout.write(
                '%sannounce %s%s next-hop %s nlri%s%s\n' % (
                    params['pre_line'], params['api_grp_syntax'], attr_line,
                    params['next_hop'], nlri_line, params['post_line']
                )
            )

    interval = 0
    if params['ts_before'] >= 0:
        interval = m['timestamp'][0] - params['ts_before']
        if m['type'][0] == MRT_T['BGP4MP_ET']:
            interval += m['micro_timestamp'] / 1000000.0

    params['ts_before'] = m['timestamp'][0]
    if m['type'][0] == MRT_T['BGP4MP_ET']:
        params['ts_before'] += m['microsecond_timestamp']

    if interval > 0:
        if params['flags'] & FLAG_T['API_PROG']:
            sys.stdout.write('%d,\n' % interval)
        else:
            time.sleep(interval)

def get_bgp_attr(args, params, m, attr):
    """
    Get bgp attribute.

    Args:
        params: (dict): write your description
        m: (todo): write your description
        attr: (str): write your description
    """
    line = ''
    r = re.compile("([0-9]+)\.([0-9]+)")

    if attr['type'][0] == BGP_ATTR_T['ATOMIC_AGGREGATE']:
        line += ' atomic-aggregate'

    if attr['type'][0] == BGP_ATTR_T['ORIGIN']:
        line += ' origin %s' % ORIGIN_T[attr['value']]

    elif attr['type'][0] == BGP_ATTR_T['AS_PATH']: 
        if flags & FLAG_T['SINGLE']:
            if len(attr['value']) == 0:
                raise NotDisplay()

            path_seg = attr['as_path'][0]
            if path_seg['type'][0] != AS_PATH_SEG_T['AS_SEQUENCE'] \
                or len(path_seg['value']) == 0 \
                or path_seg['value'][0] != str(args.peer_as):
                raise NotDisplay()

        as_path = ''
        for path_seg in attr['value']:
            if path_seg['type'][0] == AS_PATH_SEG_T['AS_SET']:
                as_path += '(%s) ' % ' '.join(path_seg['value'])
            else:
                as_path += '%s ' % ' '.join(path_seg['value'])
        line += ' as-path [%s]' % as_path

    elif attr['type'][0] == BGP_ATTR_T['NEXT_HOP']:
        params['next_hop'] = args.next_hop if args.next_hop else attr['value']

    elif attr['type'][0] == BGP_ATTR_T['MULTI_EXIT_DISC']:
        line += ' med %d' % attr['value']

    elif attr['type'][0] == BGP_ATTR_T['LOCAL_PREF']:
        line += ' local-preference %d' % attr['value']

    elif attr['type'][0] == BGP_ATTR_T['AGGREGATOR']:
        asn = attr['value']['as']
        m = r.search(asn)
        if m is not None:
            asn = int(m.group(1)) * 65536 + int(m.group(2))
        line += ' aggregator (%s:%s)' % (str(asn), attr['value']['id'])

    elif attr['type'][0] == BGP_ATTR_T['COMMUNITY']:
        comm = ' '.join(attr['value'])
        line += ' community [%s]' % comm

    elif attr['type'][0] == BGP_ATTR_T['ORIGINATOR_ID']:
        line += ' originator-id %s' % attr['value']

    elif attr['type'][0] == BGP_ATTR_T['CLUSTER_LIST']:
        line += ' cluster-list [%s]' % ' '.join(attr['value'])

    elif attr['type'][0] == BGP_ATTR_T['MP_REACH_NLRI']:
        params['next_hop'] = attr['value']['next_hop'][0]
        if m['type'][0] == MRT_T['TABLE_DUMP_V2']:
            if m['subtype'][0] == TD_V2_ST['RIB_IPV4_UNICAST'] \
                and args.next_hop:
                params['next_hop'] = args.next_hop
            elif m['subtype'][0] == TD_V2_ST['RIB_IPV6_UNICAST'] \
                and args.next_hop6:
                params['next_hop'] = args.next_hop6
        elif m['type'][0] == MRT_T['TABLE_DUMP']:
            if m['subtype'][0] == TD_ST['AFI_IPv4'] and args.next_hop:
                params['next_hop'] = args.next_hop
            elif m['subtype'][0] == TD_ST['AFI_IPv6'] and args.next_hop6:
                params['next_hop'] = args.next_hop6
        elif m['type'][0] == MRT_T['BGP4MP'] \
            or m['type'][0] == MRT_T['BGP4MP_ET']:
            if attr['value']['afi'][0] == AFI_T['IPv4'] \
                and params['flags'] & FLAG_T['IPv4']:
                if args.next_hop:
                    params['next_hop'] = args.next_hop
                if 'nlri' in attr['value']:
                    params['mp_nlri'] = attr['value']['nlri']
            elif attr['value']['afi'][0] == AFI_T['IPv6'] \
                and params['flags'] & FLAG_T['IPv6']:
                if args.next_hop6:
                    params['next_hop'] = args.next_hop6
                if 'nlri' in attr['value']:
                    params['mp_nlri'] = attr['value']['nlri']

    elif attr['type'][0] == BGP_ATTR_T['MP_UNREACH_NLRI']:
        if m['type'][0] == MRT_T['BGP4MP'] or m['type'][0] == MRT_T['BGP4MP_ET']:
            if attr['value']['afi'][0] == AFI_T['IPv4'] \
                and params['flags'] & FLAG_T['IPv4']:
                if 'withdrawn_routes' in attr['value']:
                    params['mp_withdrawn'] = attr['value']['withdrawn_routes']
            elif attr['value']['afi'][0] == AFI_T['IPv6'] \
                and params['flags'] & FLAG_T['IPv6']:
                if 'withdrawn_routes' in attr['value']:
                    params['mp_withdrawn'] = attr['value']['withdrawn_routes']

    elif attr['type'][0] == BGP_ATTR_T['EXTENDED COMMUNITIES']:
        ext_comm_list = []
        for ext_comm in attr['value']:
            ext_comm_list.append('0x%016x' % ext_comm)
        line += ' extended-community [%s]' % ' '.join(ext_comm_list)

    elif attr['type'][0] == BGP_ATTR_T['AS4_PATH']:
        as4_path = ''
        for path_seg in attr['value']:
            if path_seg['type'][0] == AS_PATH_SEG_T['AS_SET']:
                as4_path += '(%s) ' % ' '.join(path_seg['val'])
            else:
                as4_path += '%s ' % ' '.join(path_seg['val'])
        line += ' as4-path [%s]' % as4_path

    elif attr['type'][0] == BGP_ATTR_T['AS4_AGGREGATOR']:
        asn = attr['value']['asn']
        m = r.search(asn)
        if m is not None:
            asn = int(m.group(1)) * 65536 + int(m.group(2))
        line += ' as4-aggregator (%s:%s)' % (str(asn), attr['value']['id'])

    elif attr['type'][0] == BGP_ATTR_T['AIGP']:
        line += ' aigp %d' % attr['value'][0]['val']

    elif attr['type'][0] == BGP_ATTR_T['LARGE_COMMUNITY']:
        large_comm = ' '.join(attr['value'])
        line += ' large-community [%s]' % large_comm

    return line

def main():
    """
    Main function.

    Args:
    """
    (args, flags) = parse_args()
    d = Reader(args.path_to_file)
    conv_format(args, flags, d)

if __name__ == '__main__':
    main()
