'''
mrtparse.py - MRT format data parser

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

import sys
import struct
import socket
import gzip
import bz2
import collections
import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

__version__ = '1.5'

# Magic Number
GZIP_MAGIC = b'\x1f\x8b'
BZ2_MAGIC = b'\x42\x5a\x68'

def reverse_defaultdict(d):
    '''
    Reverse the keys and values of dictionaries.
    '''
    for k in list(d.keys()):
        d[d[k]] = k
    d = collections.defaultdict(lambda: "Unknown", d)
    return d

# Error codes for MrtFormatError exception
MRT_ERR_C = reverse_defaultdict({
    1:'MRT Header Error',
    2:'MRT Data Error',
})

# AFI Types
# Assigend by IANA
AFI_T = reverse_defaultdict({
    1:'IPv4',
    2:'IPv6',
    25: 'L2VPN',
})

# SAFI Types
# Assigend by IANA
SAFI_T = reverse_defaultdict({
    1:'UNICAST',
    2:'MULTICAST',
    65:'VPLS',
    70:'EVPN',
    128:'L3VPN_UNICAST',
    129:'L3VPN_MULTICAST',
})

# MRT Message Types
# Defined in RFC6396
MRT_T = reverse_defaultdict({
    0:'NULL',           # Deprecated in RFC6396
    1:'START',          # Deprecated in RFC6396
    2:'DIE',            # Deprecated in RFC6396
    3:'I_AM_DEAD',      # Deprecated in RFC6396
    4:'PEER_DOWN',      # Deprecated in RFC6396
    5:'BGP',            # Deprecated in RFC6396
    6:'RIP',            # Deprecated in RFC6396
    7:'IDRP',           # Deprecated in RFC6396
    8:'RIPNG',          # Deprecated in RFC6396
    9:'BGP4PLUS',       # Deprecated in RFC6396
    10:'BGP4PLUS_01',   # Deprecated in RFC6396
    11:'OSPFv2',
    12:'TABLE_DUMP',
    13:'TABLE_DUMP_V2',
    16:'BGP4MP',
    17:'BGP4MP_ET',
    32:'ISIS',
    33:'ISIS_ET',
    48:'OSPFv3',
    49:'OSPFv3_ET',
})

# BGP,BGP4PLUS,BGP4PLUS_01 Subtypes
# Deprecated in RFC6396
BGP_ST = reverse_defaultdict({
    0:'BGP_NULL',
    1:'BGP_UPDATE',
    2:'BGP_PREF_UPDATE',
    3:'BGP_STATE_CHANGE',
    4:'BGP_SYNC',
    5:'BGP_OPEN',
    6:'BGP_NOTIFY',
    7:'BGP_KEEPALIVE',
})

# TABLE_DUMP Subtypes
# Defined in RFC6396
TD_ST = reverse_defaultdict({
    1:'AFI_IPv4',
    2:'AFI_IPv6',
})

# TABLE_DUMP_V2 Subtypes
# Defined in RFC6396
TD_V2_ST = reverse_defaultdict({
    1:'PEER_INDEX_TABLE',
    2:'RIB_IPV4_UNICAST',
    3:'RIB_IPV4_MULTICAST',
    4:'RIB_IPV6_UNICAST',
    5:'RIB_IPV6_MULTICAST',
    6:'RIB_GENERIC',
})

# BGP4MP,BGP4MP_ET Subtypes
# Defined in RFC6396
BGP4MP_ST = reverse_defaultdict({
    0:'BGP4MP_STATE_CHANGE',
    1:'BGP4MP_MESSAGE',
    2:'BGP4MP_ENTRY',             # Deprecated in RFC6396
    3:'BGP4MP_SNAPSHOT',          # Deprecated in RFC6396
    4:'BGP4MP_MESSAGE_AS4',
    5:'BGP4MP_STATE_CHANGE_AS4',
    6:'BGP4MP_MESSAGE_LOCAL',
    7:'BGP4MP_MESSAGE_AS4_LOCAL',
})

# MRT Message Subtypes
# Defined in RFC6396
MRT_ST = collections.defaultdict(lambda: dict(), {
    9:BGP_ST,
    10:BGP_ST,
    12:AFI_T,
    13:TD_V2_ST,
    16:BGP4MP_ST,
    17:BGP4MP_ST,
})

# BGP FSM States
# Defined in RFC4271
BGP_FSM = reverse_defaultdict({
    1:'Idle',
    2:'Connect',
    3:'Active',
    4:'OpenSent',
    5:'OpenConfirm',
    6:'Established',
    7:'Clearing',    # Used only in quagga?
    8:'Deleted',     # Used only in quagga?
})

# BGP Attribute Types
# Defined in RFC4271
BGP_ATTR_T = reverse_defaultdict({
    1:'ORIGIN',
    2:'AS_PATH',
    3:'NEXT_HOP',
    4:'MULTI_EXIT_DISC',
    5:'LOCAL_PREF',
    6:'ATOMIC_AGGREGATE',
    7:'AGGREGATOR',
    8:'COMMUNITY',             # Defined in RFC1997
    9:'ORIGINATOR_ID',         # Defined in RFC4456
    10:'CLUSTER_LIST',         # Defined in RFC4456
    11:'DPA',                  # Deprecated in RFC6938
    12:'ADVERTISER',           # Deprecated in RFC6938
    13:'RCID_PATH/CLUSTER_ID', # Deprecated in RFC6938
    14:'MP_REACH_NLRI',        # Defined in RFC4760
    15:'MP_UNREACH_NLRI',      # Defined in RFC4760
    16:'EXTENDED_COMMUNITIES', # Defined in RFC4360
    17:'AS4_PATH',             # Defined in RFC6793
    18:'AS4_AGGREGATOR',       # Defined in RFC6793
    26:'AIGP',                 # Defined in RFC7311
    32:'LARGE_COMMUNITY',      # Defined in draft-ietf-idr-large-community
    128:'ATTR_SET',            # Defined in RFC6368
})

# BGP ORIGIN Types
# Defined in RFC4271
ORIGIN_T = reverse_defaultdict({
    0:'IGP',
    1:'EGP',
    2:'INCOMPLETE',
})

# BGP AS_PATH Types
# Defined in RFC4271
AS_PATH_SEG_T = reverse_defaultdict({
    1:'AS_SET',
    2:'AS_SEQUENCE',
    3:'AS_CONFED_SEQUENCE', # Defined in RFC5065
    4:'AS_CONFED_SET',      # Defined in RFC5065
})

# Reserved BGP COMMUNITY Types
# Defined in RFC1997
COMM_T = reverse_defaultdict({
    0xffffff01:'NO_EXPORT',
    0xffffff02:'NO_ADVERTISE',
    0xffffff03:'NO_EXPORT_SCONFED',
    0xffffff04:'NO_PEER',           # Defined in RFC3765
})

# BGP Message Types
# Defined in RFC4271
BGP_MSG_T = reverse_defaultdict({
    1:'OPEN',
    2:'UPDATE',
    3:'NOTIFICATION',
    4:'KEEPALIVE',
    5:'ROUTE-REFRESH', # Defined in RFC2918
})

# BGP Error Codes
# Defined in RFC4271
BGP_ERR_C = reverse_defaultdict({
    1:'Message Header Error',
    2:'OPEN Message Error',
    3:'UPDATE Message Error',
    4:'Hold Timer Expired',
    5:'Finite State Machine Error',
    6:'Cease',
    7:'ROUTE-REFRESH Message Error', # Defined in RFC7313
})

# BGP Message Header Error Subcodes
# Defined in RFC4271
BGP_HDR_ERR_SC = reverse_defaultdict({
    1:'Connection Not Synchronized',
    2:'Bad Message Length',
    3:'Bad Message Type',
})

# OPEN Message Error Subcodes
# Defined in RFC4271
BGP_OPEN_ERR_SC = reverse_defaultdict({
    1:'Unsupported Version Number',
    2:'Bad Peer AS',
    3:'Bad BGP Identifier',
    4:'Unsupported Optional Parameter',
    5:'[Deprecated]',
    6:'Unacceptable Hold Time',
    7:'Unsupported Capability',         # Defined in RFC5492
})

# UPDATE Message Error Subcodes
# Defined in RFC4271
BGP_UPDATE_ERR_SC = reverse_defaultdict({
    1:'Malformed Attribute List',
    2:'Unrecognized Well-known Attribute',
    3:'Missing Well-known Attribute',
    4:'Attribute Flags Error',
    5:'Attribute Length Error',
    6:'Invalid ORIGIN Attribute',
    7:'[Deprecated]',
    8:'Invalid NEXT_HOP Attribute',
    9:'Optional Attribute Error',
    10:'Invalid Network Field',
    11:'Malformed AS_PATH',
})

# BGP Finite State Machine Error Subcodes
# Defined in RFC6608
BGP_FSM_ERR_SC = reverse_defaultdict({
    0:'Unspecified Error',
    1:'Receive Unexpected Message in OpenSent State',
    2:'Receive Unexpected Message in OpenConfirm State',
    3:'Receive Unexpected Message in Established State',
})

# BGP Cease NOTIFICATION Message Subcodes
# Defined in RFC4486
BGP_CEASE_ERR_SC = reverse_defaultdict({
    1:'Maximum Number of Prefixes Reached',
    2:'Administrative Shutdown',
    3:'Peer De-configured',
    4:'Administrative Reset',
    5:'Connection Rejected',
    6:'Other Configuration Change',
    7:'Connection Collision Resolution',
    8:'Out of Resources',
})

# BGP ROUTE-REFRESH Message Error subcodes
# Defined in RFC7313
BGP_ROUTE_REFRESH_ERR_SC = reverse_defaultdict({
    1:'Invalid Message Length',
})

# BGP Error Subcodes
BGP_ERR_SC = collections.defaultdict(lambda: dict(), {
    1:BGP_HDR_ERR_SC,
    2:BGP_UPDATE_ERR_SC,
    3:BGP_OPEN_ERR_SC,
    4:BGP_UPDATE_ERR_SC,
    5:BGP_FSM_ERR_SC,
    6:BGP_CEASE_ERR_SC,
    7:BGP_ROUTE_REFRESH_ERR_SC,
})

# BGP OPEN Optional Parameter Types
# Defined in RFC5492
BGP_OPT_PARAMS_T = reverse_defaultdict({
    1:'Authentication', # Deprecated
    2:'Capabilities',
})

# Capability Codes
# Defined in RFC5492
BGP_CAP_C = reverse_defaultdict({
    1:'Multiprotocol Extensions for BGP-4',          # Defined in RFC2858
    2:'Route Refresh Capability for BGP-4',          # Defined in RFC2918
    3:'Outbound Route Filtering Capability',         # Defined in RFC5291
    4:'Multiple routes to a destination capability', # Defined in RFC3107
    5:'Extended Next Hop Encoding',                  # Defined in RFC5549
    64:'Graceful Restart Capability',                # Defined in RFC4724
    65:'Support for 4-octet AS number capability',   # Defined in RFC6793
    66:'[Deprecated]',
    # draft-ietf-idr-dynamic-cap
    67:'Support for Dynamic Capability (capability specific)',
    # draft-ietf-idr-bgp-multisession
    68:'Multisession BGP Capability',
    # Defined in RFC7911
    69:'ADD-PATH Capability',
    # Defined in RFC7313
    70:'Enhanced Route Refresh Capability',
    # draft-uttaro-idr-bgp-persistence
    71:'Long-Lived Graceful Restart (LLGR) Capability',
})

# Outbound Route Filtering Capability
# Defined in RFC5291
ORF_T = reverse_defaultdict({
    64:'Address Prefix ORF', # Defined in RFC5292
    65: 'CP-ORF', # Defined in RFC7543
})

ORF_SEND_RECV = reverse_defaultdict({
    1:'Receive',
    2:'Send',
    3:'Both',
})

# ADD-PATH Capability
# Defined in RFC7911
ADD_PATH_SEND_RECV = reverse_defaultdict({
    1:'Receive',
    2:'Send',
    3:'Both',
})

# AS Number Representation
AS_REPR = reverse_defaultdict({
    1:'asplain',
    2:'asdot+',
    3:'asdot',
})

# MPLS Label
LBL_BOTTOM = 0x01        # Defined in RFC3032
LBL_WITHDRAWN = 0x800000 # Defined in RFC3107

def as_len(n=None):
    '''
    AS number length for AS_PATH attribute.
    '''
    if n is not None:
        as_len.n = n
    try:
        return as_len.n
    except AttributeError:
        return 4

def as_repr(n=None):
    '''
    AS number representation.
    Default is 'asplain'(defined in RFC5396).
    '''
    if n is not None:
        as_repr.n = n
    try:
        return as_repr.n
    except AttributeError:
        return AS_REPR['asplain']

class MrtFormatError(Exception):
    '''
    Exception for invalid MRT formatted data.
    '''
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg

class Base:
    '''
    Super class for all other classes.
    '''
    __slots__ = ['buf', 'p']

    def __init__(self):
        self.buf = None
        self.p = 0

    def chk_buf(self, n):
        '''
        Check whether there is sufficient buffers.
        '''
        if len(self.buf) - self.p < n:
            raise MrtFormatError(
                'Insufficient buffer %d < %d'
                % (len(self.buf) - self.p, n))

    def val_num(self, n):
        '''
        Convert buffers to integer.
        '''
        self.chk_buf(n)
        val = 0
        for i in self.buf[self.p:self.p+n]:
            val <<= 8
            # for Python3
            if isinstance(i, int):
                val += i
            # for Python2
            else:
                val += struct.unpack('>B', i)[0]
        self.p += n
        return val

    def val_bytes(self, n):
        '''
        Convert buffers to bytes.
        '''
        self.chk_buf(n)
        val = self.buf[self.p:self.p+n]
        self.p += n
        return val

    def val_str(self, n):
        '''
        Convert buffers to string.
        '''
        self.chk_buf(n)
        val = self.buf[self.p:self.p+n]
        self.p += n
        # for Python2
        if isinstance(val, str):
            return val
        # for Python3
        else:
            return val.decode('utf-8')

    def val_addr(self, af, n=-1):
        '''
        Convert buffers to IP address.
        '''
        if af == AFI_T['IPv4']:
            m = 4
            _af = socket.AF_INET
        elif af == AFI_T['IPv6']:
            m = 16
            _af = socket.AF_INET6
        else:
            raise MrtFormatError('Unsupported AFI %d(%s)' % (af, AFI_T[af]))
        n = m if n < 0 else (n + 7) // 8
        self.chk_buf(n)
        addr = socket.inet_ntop(
            _af, self.buf[self.p:self.p+n] + b'\x00'*(m - n))
        self.p += n
        return addr

    def val_asn(self, n):
        '''
        Convert buffers to AS number.
        '''
        asn = self.val_num(n)
        if as_repr() == AS_REPR['asplain'] \
            or (as_repr() == AS_REPR['asdot'] and asn < 0x10000):
            return str(asn)
        else:
            return str(asn >> 16) + '.' + str(asn & 0xffff)

    def val_rd(self):
        '''
        Convert buffers to route distinguisher.
        '''
        rd = self.val_num(8)
        return str(rd >> 32) + ':' + str(rd & 0xffffffff)

    def val_nlri(self, n, af, saf=0):
        '''
        Convert buffers to NLRI.
        '''
        try:
            p = self.p
            l = []
            while p < n:
                nlri = Nlri(self.buf[p:])
                p += nlri.unpack(af, saf)
                nlri.is_valid()
                nlri.is_dup(l)
                l.append(nlri)
            self.p = p
        except MrtFormatError:
            l = []
            while self.p < n:
                nlri = Nlri(self.buf[self.p:])
                self.p += nlri.unpack(af, saf, add_path=1)
                nlri.is_valid()
                l.append(nlri)
        return l

class Reader(Base):
    '''
    Reader for MRT format data.
    '''
    __slots__ = ['mrt', 'f']

    def __init__(self, arg):
        Base.__init__(self)
        self.mrt = None
        self.f = None

        # for file instance
        if hasattr(arg, 'read'):
            self.f = arg
        # for file path
        elif isinstance(arg, str):
            f = open(arg, 'rb')
            hdr = f.read(max(len(BZ2_MAGIC), len(GZIP_MAGIC)))
            f.close()

            if hdr.startswith(BZ2_MAGIC):
                self.f = bz2.BZ2File(arg, 'rb')
            elif hdr.startswith(GZIP_MAGIC):
                self.f = gzip.GzipFile(arg, 'rb')
            else:
                self.f = open(arg, 'rb')
        else:
            sys.stderr.write("Error: Unsupported instance type\n")

    def close(self):
        '''
        Close file object and stop iteration.
        '''
        self.f.close()
        raise StopIteration

    def __iter__(self):
        return self

    def __next__(self):
        try:
            self.unpack_hdr()
        except MrtFormatError as e:
            self.mrt.err = MRT_ERR_C['MRT Header Error']
            self.mrt.err_msg = e.msg
            return self

        try:
            self.unpack_data()
        except MrtFormatError as e:
            self.mrt.err = MRT_ERR_C['MRT Data Error']
            self.mrt.err_msg = e.msg
            return self

        return self

    # for Python2 compatibility
    next = __next__

    def unpack_hdr(self):
        '''
        Decoder for MRT header.
        '''
        as_len(4)
        self.mrt = Mrt(self.f.read(12))
        if len(self.mrt.buf) == 0:
            self.close()
        elif len(self.mrt.buf) < 12:
            raise MrtFormatError(
                'Invalid MRT header length %d < 12'
                % len(self.mrt.buf))
        self.mrt.unpack()

    def unpack_data(self):
        '''
        Decoder for MRT payload.
        '''
        data = self.f.read(self.mrt.len)
        self.mrt.buf += data
        if len(data) < self.mrt.len:
            raise MrtFormatError(
                'Invalid MRT data length %d < %d'
                % (len(data), self.mrt.len))

        if self.mrt.type == MRT_T['TABLE_DUMP_V2']:
            self.unpack_td_v2(data)
        elif self.mrt.type == MRT_T['BGP4MP'] \
            or self.mrt.type == MRT_T['BGP4MP_ET']:
            if self.mrt.subtype == BGP4MP_ST['BGP4MP_ENTRY'] \
                or self.mrt.subtype == BGP4MP_ST['BGP4MP_SNAPSHOT']:
                self.p += self.mrt.len
                raise MrtFormatError(
                    'Unsupported %s subtype %d(%s)'
                    % (MRT_T[self.mrt.type], self.mrt.subtype,
                       BGP4MP_ST[self.mrt.subtype]))
            else:
                if self.mrt.type == MRT_T['BGP4MP_ET']:
                    self.mrt.micro_ts = self.val_num(4)
                self.mrt.bgp = Bgp4Mp(data)
                self.mrt.bgp.unpack(self.mrt.subtype)
        elif self.mrt.type == MRT_T['TABLE_DUMP']:
            self.mrt.td = TableDump(data)
            self.mrt.td.unpack(self.mrt.subtype)
        else:
            self.p += self.mrt.len
            raise MrtFormatError(
                'Unsupported MRT type %d(%s)'
                % (self.mrt.type, MRT_T[self.mrt.type]))

        return self.p

    def unpack_td_v2(self, data):
        '''
        Decoder for Table_Dump_V2 format.
        '''
        if self.mrt.subtype == TD_V2_ST['RIB_IPV4_UNICAST'] \
            or self.mrt.subtype == TD_V2_ST['RIB_IPV4_MULTICAST']:
            self.mrt.rib = AfiSpecRib(data)
            self.mrt.rib.unpack(AFI_T['IPv4'])
        elif self.mrt.subtype == TD_V2_ST['RIB_IPV6_UNICAST'] \
            or self.mrt.subtype == TD_V2_ST['RIB_IPV6_MULTICAST']:
            self.mrt.rib = AfiSpecRib(data)
            self.mrt.rib.unpack(AFI_T['IPv6'])
        elif self.mrt.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
            self.mrt.peer = PeerIndexTable(data)
            self.mrt.peer.unpack()
        elif self.mrt.subtype == TD_V2_ST['RIB_GENERIC']:
            self.mrt.rib = RibGeneric(data)
            self.mrt.rib.unpack()
        else:
            self.p += self.mrt.len

class Mrt(Base):
    '''
    Class for MRT header.
    '''
    __slots__ = [
        'ts', 'type', 'subtype', 'len', 'micro_ts', 'bgp', 'peer', 'td', 'rib',
        'err', 'err_msg'
    ]

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.ts = None
        self.type = None
        self.subtype = None
        self.len = None
        self.micro_ts = None
        self.bgp = None
        self.peer = None
        self.td = None
        self.rib = None
        self.err = None
        self.err_msg = None

    def unpack(self):
        '''
        Decoder for MRT header.
        '''
        self.ts = self.val_num(4)
        self.type = self.val_num(2)
        self.subtype = self.val_num(2)
        self.len = self.val_num(4)
        return self.p

class TableDump(Base):
    '''
    Class for Table_Dump format.
    '''
    __slots__ = [
        'view', 'seq', 'prefix', 'plen', 'status', 'org_time', 'peer_ip',
        'peer_as', 'attr_len', 'attr'
    ]

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.view = None
        self.seq = None
        self.prefix = None
        self.plen = None
        self.status = None
        self.org_time = None
        self.peer_ip = None
        self.peer_as = None
        self.attr_len = None
        self.attr = None

    def unpack(self, subtype):
        '''
        Decoder for Table_Dump format.
        '''
        self.view = self.val_num(2)
        self.seq = self.val_num(2)
        self.prefix = self.val_addr(subtype)
        self.plen = self.val_num(1)
        self.status = self.val_num(1)
        self.org_time = self.val_num(4)
        self.peer_ip = self.val_addr(AFI_T['IPv4'])
        if subtype == AFI_T['IPv6'] and self.val_num(12):
            self.p -= 16
            self.peer_ip = self.val_addr(subtype)
        self.peer_as = self.val_asn(as_len(2))
        attr_len = self.attr_len = self.val_num(2)
        self.attr = []
        while attr_len > 0:
            attr = BgpAttr(self.buf[self.p:])
            self.p += attr.unpack()
            self.attr.append(attr)
            attr_len -= attr.p
        return self.p

class PeerIndexTable(Base):
    '''
    Class for PEER_INDEX_TABLE format.
    '''
    __slots__ = ['collector', 'view_len', 'view', 'count', 'entry']

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.collector = None
        self.view_len = None
        self.view = None
        self.count = None
        self.entry = None

    def unpack(self):
        '''
        Decoder for PEER_INDEX_TABLE format.
        '''
        self.collector = self.val_addr(AFI_T['IPv4'])
        self.view_len = self.val_num(2)
        self.view = self.val_str(self.view_len)
        self.count = self.val_num(2)
        self.entry = []
        for _ in range(self.count):
            entry = PeerEntries(self.buf[self.p:])
            self.p += entry.unpack()
            self.entry.append(entry)
        return self.p

class PeerEntries(Base):
    '''
    Class for Peer Entries.
    '''
    __slots__ = ['type', 'bgp_id', 'ip', 'asn']

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.type = None
        self.bgp_id = None
        self.ip = None
        self.asn = None

    def unpack(self):
        '''
        Decoder for Peer Entries.
        '''
        self.type = self.val_num(1)
        self.bgp_id = self.val_addr(AFI_T['IPv4'])
        if self.type & 0x01:
            af = AFI_T['IPv6']
        else:
            af = AFI_T['IPv4']
        self.ip = self.val_addr(af)
        n = 4 if self.type & (0x01 << 1) else 2
        self.asn = self.val_asn(n)
        return self.p

class RibGeneric(Base):
    '''
    Class for RIB_GENERIC format.
    '''
    __slots__ = ['seq', 'afi', 'safi', 'nlri', 'count', 'entry']

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.seq = None
        self.afi = None
        self.safi = None
        self.nlri = None
        self.count = None
        self.entry = None

    def unpack(self):
        '''
        Decoder for RIB_GENERIC format.
        '''
        self.seq = self.val_num(4)
        self.afi = self.val_num(2)
        self.safi = self.val_num(1)
        n = self.val_num(1)
        self.p -= 1
        self.nlri = self.val_nlri(self.p + (n + 7) // 8, self.afi, self.safi)
        self.count = self.val_num(2)
        self.entry = []
        for _ in range(self.count):
            entry = RibEntries(self.buf[self.p:])
            self.p += entry.unpack(self.afi)
            self.entry.append(entry)
        return self.p

class AfiSpecRib(Base):
    '''
    Class for AFI/SAFI-Specific RIB format.
    '''
    __slots__ = ['seq', 'plen', 'prefix', 'count', 'entry']

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.seq = None
        self.plen = None
        self.prefix = None
        self.count = None
        self.entry = None

    def unpack(self, af):
        '''
        Decoder for AFI/SAFI-Specific RIB format.
        '''
        self.seq = self.val_num(4)
        self.plen = self.val_num(1)
        self.prefix = self.val_addr(af, self.plen)
        self.count = self.val_num(2)
        self.entry = []
        for _ in range(self.count):
            entry = RibEntries(self.buf[self.p:])
            self.p += entry.unpack(af)
            self.entry.append(entry)
        return self.p

class RibEntries(Base):
    '''
    Class for Rib Entries format.
    '''
    __slots__ = ['peer_index', 'org_time', 'attr_len', 'attr']

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.peer_index = None
        self.org_time = None
        self.attr_len = None
        self.attr = None

    def unpack(self, af):
        '''
        Decoder for Rib Entries format.
        '''
        self.peer_index = self.val_num(2)
        self.org_time = self.val_num(4)
        attr_len = self.attr_len = self.val_num(2)
        self.attr = []
        while attr_len > 0:
            attr = BgpAttr(self.buf[self.p:])
            self.p += attr.unpack(af)
            self.attr.append(attr)
            attr_len -= attr.p
        return self.p

class Bgp4Mp(Base):
    '''
    Class for BGP4MP format.
    '''
    __slots__ = [
        'peer_as', 'local_as', 'ifindex', 'af', 'peer_ip', 'local_ip',
        'old_state', 'new_state', 'msg'
    ]

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.peer_as = None
        self.local_as = None
        self.ifindex = None
        self.af = None
        self.peer_ip = None
        self.local_ip = None
        self.old_state = None
        self.new_state = None
        self.msg = None

    def unpack(self, subtype):
        '''
        Decoder for BGP4MP format.
        '''
        if subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE'] \
            or subtype == BGP4MP_ST['BGP4MP_MESSAGE'] \
            or subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']:
            as_len(2)

        self.peer_as = self.val_asn(as_len())
        self.local_as = self.val_asn(as_len())
        self.ifindex = self.val_num(2)
        self.af = self.val_num(2)
        self.peer_ip = self.val_addr(self.af)
        self.local_ip = self.val_addr(self.af)

        if subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE'] \
            or subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']:
            self.old_state = self.val_num(2)
            self.new_state = self.val_num(2)
        else:
            self.msg = BgpMessage(self.buf[self.p:])
            self.p += self.msg.unpack(self.af)
        return self.p

class BgpMessage(Base):
    '''
    Class for BGP Message.
    '''
    __slots__ = [
        'marker', 'len', 'type', 'ver', 'my_as', 'holdtime', 'bgp_id',
        'opt_len', 'opt_params', 'wd_len', 'withdrawn', 'attr_len', 'attr',
        'nlri', 'err_code', 'err_subcode', 'data', 'afi', 'rsvd', 'safi'
    ]

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.marker = None
        self.len = None
        self.type = None
        self.ver = None
        self.my_as = None
        self.holdtime = None
        self.bgp_id = None
        self.opt_len = None
        self.opt_params = None
        self.wd_len = None
        self.withdrawn = None
        self.attr_len = None
        self.attr = None
        self.nlri = None
        self.err_code = None
        self.err_subcode = None
        self.data = None
        self.afi = None
        self.rsvd = None
        self.safi = None

    def unpack(self, af):
        '''
        Decoder for BGP Message.
        '''
        self.marker = self.val_bytes(16)
        self.len = self.val_num(2)
        self.type = self.val_num(1)

        if self.type == BGP_MSG_T['OPEN']:
            self.unpack_open()
        elif self.type == BGP_MSG_T['UPDATE']:
            self.unpack_update(af)
        elif self.type == BGP_MSG_T['NOTIFICATION']:
            self.unpack_notification()
        elif self.type == BGP_MSG_T['ROUTE-REFRESH']:
            self.unpack_route_refresh()

        self.p += self.len - self.p
        return self.p

    def unpack_open(self):
        '''
        Decoder for BGP OPEN Message.
        '''
        self.ver = self.val_num(1)
        self.my_as = self.val_num(2)
        self.holdtime = self.val_num(2)
        self.bgp_id = self.val_addr(AFI_T['IPv4'])
        opt_len = self.opt_len = self.val_num(1)
        self.opt_params = []
        while opt_len > 0:
            opt_params = OptParams(self.buf[self.p:])
            self.p += opt_params.unpack()
            self.opt_params.append(opt_params)
            opt_len -= opt_params.p

    def unpack_update(self, af):
        '''
        Decoder for BGP UPDATE Message.
        '''
        self.wd_len = self.val_num(2)
        self.withdrawn = self.val_nlri(self.p + self.wd_len, af)
        self.attr_len = self.val_num(2)
        attr_len = self.p + self.attr_len
        self.attr = []
        while self.p < attr_len:
            attr = BgpAttr(self.buf[self.p:])
            self.p += attr.unpack()
            self.attr.append(attr)
        self.nlri = self.val_nlri(self.len, af)

    def unpack_notification(self):
        '''
        Decoder for BGP NOTIFICATION Message.
        '''
        self.err_code = self.val_num(1)
        self.err_subcode = self.val_num(1)
        self.data = self.val_bytes(self.len - self.p)

    def unpack_route_refresh(self):
        '''
        Decoder for BGP ROUTE-REFRESH Message.
        '''
        self.afi = self.val_num(2)
        self.rsvd = self.val_num(1)
        self.safi = self.val_num(1)

class OptParams(Base):
    '''
    Class for BGP OPEN Optional Parameters.
    '''
    __slots__ = [
        'type', 'len', 'cap_type', 'cap_len', 'multi_ext', 'orf',
        'graceful_restart', 'support_as4', 'add_path'
    ]

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.type = None
        self.len = None
        self.cap_type = None
        self.cap_len = None
        self.multi_ext = None
        self.orf = None
        self.graceful_restart = None
        self.support_as4 = None
        self.add_path = None

    def unpack(self):
        '''
        Decoder for BGP OPEN Optional Parameters.
        '''
        self.type = self.val_num(1)
        self.len = self.val_num(1)
        if self.type == BGP_OPT_PARAMS_T['Capabilities']:
            self.unpack_capabilities()
        else:
            self.p += self.len
        return self.p

    def unpack_capabilities(self):
        '''
        Decoder for BGP Capabilities.
        '''
        self.cap_type = self.val_num(1)
        self.cap_len = self.val_num(1)

        if self.cap_type == BGP_CAP_C['Multiprotocol Extensions for BGP-4']:
            self.unpack_multi_ext()
        elif self.cap_type == BGP_CAP_C['Route Refresh Capability for BGP-4']:
            self.p += self.len - 2
        elif self.cap_type == BGP_CAP_C['Outbound Route Filtering Capability']:
            self.unpack_orf()
        elif self.cap_type == BGP_CAP_C['Graceful Restart Capability']:
            self.unpack_graceful_restart()
        elif self.cap_type == BGP_CAP_C['Support for 4-octet AS number capability']:
            self.unpack_support_as4()
        elif self.cap_type == BGP_CAP_C['ADD-PATH Capability']:
            self.unpack_add_path()
        else:
            self.p += self.len - 2

    def unpack_multi_ext(self):
        '''
        Decoder for Multiprotocol Extensions for BGP-4.
        '''
        self.multi_ext = {}
        self.multi_ext['afi'] = self.val_num(2)
        self.multi_ext['rsvd'] = self.val_num(1)
        self.multi_ext['safi'] = self.val_num(1)

    def unpack_orf(self):
        '''
        Decoder for Outbound Route Filtering Capability.
        '''
        self.orf = {}
        self.orf['afi'] = self.val_num(2)
        self.orf['rsvd'] = self.val_num(1)
        self.orf['safi'] = self.val_num(1)
        self.orf['number'] = self.val_num(1)
        self.orf['entry'] = []
        for _ in range(self.orf['number']):
            entry = {}
            entry['type'] = self.val_num(1)
            entry['send_recv'] = self.val_num(1)
            self.orf['entry'].append(entry)

    def unpack_graceful_restart(self):
        '''
        Decoder for Graceful Restart Capability.
        '''
        self.graceful_restart = {}
        n = self.val_num(2)
        self.graceful_restart['flag'] = n & 0xf000
        self.graceful_restart['sec'] = n & 0x0fff
        self.graceful_restart['entry'] = []
        cap_len = self.cap_len
        while cap_len > 2:
            entry = {}
            entry['afi'] = self.val_num(2)
            entry['safi'] = self.val_num(1)
            entry['flag'] = self.val_num(1)
            self.graceful_restart['entry'].append(entry)
            cap_len -= 4

    def unpack_support_as4(self):
        '''
        Decoder for Support for 4-octet AS number capability.
        '''
        self.support_as4 = self.val_asn(4)

    def unpack_add_path(self):
        '''
        Decoder for ADD-PATH Capability
        '''
        self.add_path = []
        cap_len = self.cap_len
        while cap_len > 2:
            entry = {}
            entry['afi'] = self.val_num(2)
            entry['safi'] = self.val_num(1)
            entry['send_recv'] = self.val_num(1)
            self.add_path.append(entry)
            cap_len -= 4

class BgpAttr(Base):
    '''
    Class for BGP path attributes
    '''
    __slots__ = [
        'flag', 'type', 'len', 'origin', 'as_path', 'next_hop', 'med',
        'local_pref', 'aggr', 'comm', 'org_id', 'cl_list', 'mp_reach',
        'mp_unreach', 'ext_comm', 'as4_path', 'as4_aggr', 'aigp', 'attr_set',
        'large_comm', 'val'
    ]

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.flag = None
        self.type = None
        self.len = None
        self.origin = None
        self.as_path = None
        self.next_hop = None
        self.med = None
        self.local_pref = None
        self.aggr = None
        self.comm = None
        self.org_id = None
        self.cl_list = None
        self.mp_reach = None
        self.mp_unreach = None
        self.ext_comm = None
        self.as4_path = None
        self.as4_aggr = None
        self.aigp = None
        self.attr_set = None
        self.larg_comm = None
        self.val = None

    def unpack(self, af=0):
        '''
        Decoder for BGP path attributes
        '''
        self.flag = self.val_num(1)
        self.type = self.val_num(1)

        if self.flag & 0x01 << 4:
            self.len = self.val_num(2)
        else:
            self.len = self.val_num(1)

        if self.type == BGP_ATTR_T['ORIGIN']:
            self.unpack_origin()
        elif self.type == BGP_ATTR_T['AS_PATH']:
            self.unpack_as_path()
        elif self.type == BGP_ATTR_T['NEXT_HOP']:
            self.unpack_next_hop()
        elif self.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
            self.unpack_multi_exit_disc()
        elif self.type == BGP_ATTR_T['LOCAL_PREF']:
            self.unpack_local_pref()
        elif self.type == BGP_ATTR_T['AGGREGATOR']:
            self.unpack_aggregator()
        elif self.type == BGP_ATTR_T['COMMUNITY']:
            self.unpack_community()
        elif self.type == BGP_ATTR_T['ORIGINATOR_ID']:
            self.unpack_originator_id()
        elif self.type == BGP_ATTR_T['CLUSTER_LIST']:
            self.unpack_cluster_list()
        elif self.type == BGP_ATTR_T['MP_REACH_NLRI']:
            self.unpack_mp_reach_nlri(af)
        elif self.type == BGP_ATTR_T['MP_UNREACH_NLRI']:
            self.unpack_mp_unreach_nlri()
        elif self.type == BGP_ATTR_T['EXTENDED_COMMUNITIES']:
            self.unpack_extended_communities()
        elif self.type == BGP_ATTR_T['AS4_PATH']:
            self.unpack_as4_path()
        elif self.type == BGP_ATTR_T['AS4_AGGREGATOR']:
            self.unpack_as4_aggregator()
        elif self.type == BGP_ATTR_T['AIGP']:
            self.unpack_aigp()
        elif self.type == BGP_ATTR_T['ATTR_SET']:
            self.unpack_attr_set()
        elif self.type == BGP_ATTR_T['LARGE_COMMUNITY']:
            self.unpack_large_community()
        else:
            self.val = self.val_bytes(self.len)
        return self.p

    def unpack_origin(self):
        '''
        Decoder for ORIGIN attribute
        '''
        self.origin = self.val_num(1)

    def unpack_as_path(self):
        '''
        Decoder for AS_PATH attribute
        '''
        attr_len = self.p + self.len
        self.as_path = []
        while self.p < attr_len:
            path_seg = {}
            path_seg['type'] = self.val_num(1)
            path_seg['len'] = self.val_num(1)
            path_seg['val'] = []
            for _ in range(path_seg['len']):
                path_seg['val'].append(self.val_asn(as_len()))
            self.as_path.append(path_seg)

    def unpack_next_hop(self):
        '''
        Decoder for NEXT_HOP attribute
        '''
        if self.len == 4:
            self.next_hop = self.val_addr(AFI_T['IPv4'])
        elif self.len == 16:
            self.next_hop = self.val_addr(AFI_T['IPv6'])
        else:
            self.p += self.len
            self.next_hop = None

    def unpack_multi_exit_disc(self):
        '''
        Decoder for MULTI_EXIT_DISC attribute
        '''
        self.med = self.val_num(4)

    def unpack_local_pref(self):
        '''
        Decoder for LOCAL_PREF attribute
        '''
        self.local_pref = self.val_num(4)

    def unpack_aggregator(self):
        '''
        Decoder for AGGREGATOR attribute
        '''
        self.aggr = {}
        n = 2 if self.len < 8 else 4
        self.aggr['asn'] = self.val_asn(n)
        self.aggr['id'] = self.val_addr(AFI_T['IPv4'])

    def unpack_community(self):
        '''
        Decoder for COMMUNITY attribute
        '''
        attr_len = self.p + self.len
        self.comm = []
        while self.p < attr_len:
            val = self.val_num(4)
            self.comm.append(
                '%d:%d' %
                ((val & 0xffff0000) >> 16, val & 0x0000ffff))

    def unpack_originator_id(self):
        '''
        Decoder for ORIGINATOR_ID attribute
        '''
        self.org_id = self.val_addr(AFI_T['IPv4'])

    def unpack_cluster_list(self):
        '''
        Decoder for CLUSTER_LIST attribute
        '''
        attr_len = self.p + self.len
        self.cl_list = []
        while self.p < attr_len:
            self.cl_list.append(self.val_addr(AFI_T['IPv4']))

    def unpack_mp_reach_nlri(self, af):
        '''
        Decoder for MP_REACH_NLRI attribute
        '''
        attr_len = self.p + self.len
        self.mp_reach = {}
        self.mp_reach['afi'] = self.val_num(2)

        if AFI_T[self.mp_reach['afi']] != 'Unknown':
            af = self.mp_reach['afi']
            self.mp_reach['safi'] = self.val_num(1)
            self.mp_reach['nlen'] = self.val_num(1)

            if af != AFI_T['IPv4'] and af != AFI_T['IPv6']:
                self.p = attr_len
                return

            if self.mp_reach['safi'] != SAFI_T['UNICAST'] \
                and self.mp_reach['safi'] != SAFI_T['MULTICAST'] \
                and self.mp_reach['safi'] != SAFI_T['L3VPN_UNICAST'] \
                and self.mp_reach['safi'] != SAFI_T['L3VPN_MULTICAST']:
                self.p = attr_len
                return

            if self.mp_reach['safi'] == SAFI_T['L3VPN_UNICAST'] \
                or self.mp_reach['safi'] == SAFI_T['L3VPN_MULTICAST']:
                self.mp_reach['rd'] = self.val_rd()
        else:
            self.p -= 2
            self.mp_reach = {}
            self.mp_reach['nlen'] = self.val_num(1)

        self.mp_reach['next_hop'] = []
        self.mp_reach['next_hop'].append(self.val_addr(af))
        if self.mp_reach['nlen'] == 32 and af == AFI_T['IPv6']:
            self.mp_reach['next_hop'].append(self.val_addr(af))

        if 'afi' in self.mp_reach:
            self.mp_reach['rsvd'] = self.val_num(1)
            self.mp_reach['nlri'] = self.val_nlri(
                attr_len, af, self.mp_reach['safi'])

    def unpack_mp_unreach_nlri(self):
        '''
        Decoder for MP_UNREACH_NLRI attribute
        '''
        attr_len = self.p + self.len
        self.mp_unreach = {}
        self.mp_unreach['afi'] = self.val_num(2)
        self.mp_unreach['safi'] = self.val_num(1)

        if self.mp_unreach['afi'] != AFI_T['IPv4'] \
            and self.mp_unreach['afi'] != AFI_T['IPv6']:
            self.p = attr_len
            return

        if self.mp_unreach['safi'] != SAFI_T['UNICAST'] \
            and self.mp_unreach['safi'] != SAFI_T['MULTICAST'] \
            and self.mp_unreach['safi'] != SAFI_T['L3VPN_UNICAST'] \
            and self.mp_unreach['safi'] != SAFI_T['L3VPN_MULTICAST']:
            self.p = attr_len
            return

        self.mp_unreach['withdrawn'] = self.val_nlri(
            attr_len, self.mp_unreach['afi'], self.mp_unreach['safi'])

    def unpack_extended_communities(self):
        '''
        Decoder for EXT_COMMUNITIES attribute
        '''
        attr_len = self.p + self.len
        self.ext_comm = []
        while self.p < attr_len:
            ext_comm = self.val_num(8)
            self.ext_comm.append(ext_comm)

    def unpack_as4_path(self):
        '''
        Decoder for AS4_PATH attribute
        '''
        attr_len = self.p + self.len
        self.as4_path = []
        while self.p < attr_len:
            path_seg = {}
            path_seg['type'] = self.val_num(1)
            path_seg['len'] = self.val_num(1)
            path_seg['val'] = []
            for _ in range(path_seg['len']):
                path_seg['val'].append(self.val_asn(4))
            self.as4_path.append(path_seg)

    def unpack_as4_aggregator(self):
        '''
        Decoder for AS4_AGGREGATOR attribute
        '''
        self.as4_aggr = {}
        self.as4_aggr['asn'] = self.val_asn(4)
        self.as4_aggr['id'] = self.val_addr(AFI_T['IPv4'])

    def unpack_aigp(self):
        '''
        Decoder for AIGP attribute
        '''
        attr_len = self.p + self.len
        self.aigp = []
        while self.p < attr_len:
            aigp = {}
            aigp['type'] = self.val_num(1)
            aigp['len'] = self.val_num(2)
            aigp['val'] = self.val_num(aigp['len'] - 3)
            self.aigp.append(aigp)

    def unpack_attr_set(self):
        '''
        Decoder for ATTR_SET attribute
        '''
        attr_len = self.p + self.len
        self.attr_set = {}
        self.attr_set['origin_as'] = self.val_asn(4)
        attr_len -= 4
        self.attr_set['attr'] = []
        while self.p < attr_len:
            attr = BgpAttr(self.buf[self.p:])
            self.p += attr.unpack()
            self.attr_set['attr'].append(attr)

    def unpack_large_community(self):
        '''
        Decoder for LARGE_COMMUNITY attribute
        '''
        attr_len = self.p + self.len
        self.large_comm = []
        while self.p < attr_len:
            global_admin = self.val_num(4)
            local_data_part_1 = self.val_num(4)
            local_data_part_2 = self.val_num(4)
            self.large_comm.append(
                '%d:%d:%d' %
                (global_admin, local_data_part_1, local_data_part_2))

class Nlri(Base):
    '''
    Class for NLRI.
    '''
    __slots__ = ['path_id', 'label', 'rd', 'plen', 'prefix']

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf
        self.path_id = None
        self.label = None
        self.rd = None
        self.plen = None
        self.prefix = None

    def unpack(self, af, saf=0, add_path=0):
        '''
        Decoder for NLRI.
        '''
        if add_path:
            self.path_id = self.val_num(4)
        self.plen = plen = self.val_num(1)
        if saf == SAFI_T['L3VPN_UNICAST'] \
            or saf == SAFI_T['L3VPN_MULTICAST']:
            plen = self.unpack_l3vpn(plen)
        if af == AFI_T['IPv4'] and plen > 32 \
            or af == AFI_T['IPv6'] and plen > 128:
            raise MrtFormatError(
                'Invalid prefix length %d (%s)'
                % (self.plen, AFI_T[af]))
        self.prefix = self.val_addr(af, plen)
        return self.p

    def unpack_l3vpn(self, plen):
        '''
        Decoder for L3VPN NLRI.
        '''
        self.label = []
        while True:
            label = self.val_num(3)
            self.label.append(label)
            if label &  LBL_BOTTOM or label == LBL_WITHDRAWN:
                break
        self.rd = self.val_rd()
        plen -= (3 * len(self.label) + 8) * 8
        return plen

    def is_dup(self, l):
        '''
        Check whether there is duplicate routes in NLRI.
        '''
        for e in l:
            if self.plen == e.plen and self.prefix == e.prefix \
                and self.label == e.label and self.rd == e.rd:
                raise MrtFormatError(
                    'Duplicate prefix %s/%d'
                    % (self.prefix, self.plen))

    def is_valid(self):
        '''
        Check whether route is valid.
        '''
        if self.label is not None:
            plen = self.plen - (len(self.label) * 3 + 8) * 8
        else:
            plen = self.plen
        if ':' in self.prefix:
            b = socket.inet_pton(socket.AF_INET6, self.prefix)
            t = struct.unpack("!QQ", b)
            n = t[0] << 64 | t[1]
            plen_max = 128
        else:
            b = socket.inet_pton(socket.AF_INET, self.prefix)
            n = struct.unpack("!L", b)[0]
            plen_max = 32
        if n & ~(-1 << (plen_max - plen)):
            raise MrtFormatError(
                'Invalid prefix %s/%d'
                % (self.prefix, self.plen))
