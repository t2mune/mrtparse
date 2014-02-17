'''
mrtparse is a module to parse a MRT format data.

See https://github.com/YoshiyukiYamauchi/mrtparse for more informations.
This module is published under a Apache License, Version 2.0.
Created by
    Tetsumune KISO <t2mune@gmail.com>,
    Yoshiyuki YAMAUCHI <info@greenhippo.co.jp>,
    Nobuhiro ITOU <js333123@gmail.com>.
Copyright (C) greenHippo, LLC. All rights reserved.
'''

import sys, struct, socket
import gzip, bz2

# mrtparse information
__pyname__  = 'mrtparse'
__version__ =  '0.8'
__descr__   = 'parse a MRT-format data'
__url__     = 'https://github.com/YoshiyukiYamauchi/mrtparse'
__author__  = 'Tetsumune KISO, Yoshiyuki YAMAUCHI, Nobuhiro ITOU'
__email__   = 't2mune@gmail.com, info@greenhippo.co.jp, js333123@gmail.com'
__license__ = 'Apache License, Version 2.0'

# Magic Number
GZIP_MAGIC = b'\x1f\x8b'
BZ2_MAGIC  = b'\x42\x5a\x68'

# MRT header length
MRT_HDR_LEN = 12

# AS number length(especially to use AS_PATH attribute)
as_len = 4

# a variable to reverse the keys and values of dictionaries below
dl = []

# AFI Types
# Assigend by IANA
AFI_T = {
    1:'AFI_IPv4',
    2:'AFI_IPv6',
}
dl += [AFI_T]

# SAFI Types
# Assigend by IANA
SAFI_T = {
    1:'SAFI_UNICAST',
    2:'SAFI_MULTICAST',
}
dl += [SAFI_T]

# MRT Message Types
# Defined in RFC6396
MSG_T = {
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
}
dl += [MSG_T]

# BGP,BGP4PLUS,BGP4PLUS_01 Subtypes
# Deprecated in RFC6396
BGP_ST = {
    0:'BGP_NULL',
    1:'BGP_UPDATE',
    2:'BGP_PREF_UPDATE',
    3:'BGP_STATE_CHANGE',
    4:'BGP_SYNC', 
    5:'BGP_OPEN',
    6:'BGP_NOTIFY',
    7:'BGP_KEEPALIVE',
}
dl += [BGP_ST]

# TABLE_DUMP Subtypes
# Defined in RFC6396
TD_ST = {
    1:'AFI_IPv4',
    2:'AFI_IPv6',
}
dl += [AFI_T]

# TABLE_DUMP_V2 Subtypes
# Defined in RFC6396
TD_V2_ST = {
    1:'PEER_INDEX_TABLE',
    2:'RIB_IPV4_UNICAST',
    3:'RIB_IPV4_MULTICAST',
    4:'RIB_IPV6_UNICAST',
    5:'RIB_IPV6_MULTICAST',
    6:'RIB_GENERIC',
}
dl += [TD_V2_ST]

# BGP4MP,BGP4MP_ET Subtypes
# Defined in RFC6396
BGP4MP_ST = {
    0:'BGP4MP_STATE_CHANGE',
    1:'BGP4MP_MESSAGE',
    2:'BGP4MP_ENTRY',             # Deprecated in RFC6396
    3:'BGP4MP_SNAPSHOT',          # Deprecated in RFC6396
    4:'BGP4MP_MESSAGE_AS4',
    5:'BGP4MP_STATE_CHANGE_AS4',
    6:'BGP4MP_MESSAGE_LOCAL',
    7:'BGP4MP_MESSAGE_AS4_LOCAL',
}
dl += [BGP4MP_ST]

# MRT Message Subtypes
# Defined in RFC6396
MSG_ST = {
    9:BGP_ST,
    10:BGP_ST,
    12:AFI_T,
    13:TD_V2_ST,
    16:BGP4MP_ST,
    17:BGP4MP_ST,
}

# BGP FSM States
# Defined in RFC4271
BGP_FSM = {
    1:'Idle',
    2:'Connect',
    3:'Active',
    4:'OpenSent',
    5:'OpenConfirm',
    6:'Established',
    7:'Clearing',    # Used only in quagga?
    8:'Deleted',     # Used only in quagga?
}
dl += [BGP_FSM]

# BGP Attribute Types
# Defined in RFC4271
BGP_ATTR_T = {
    0:'Reserved',
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
}
dl += [BGP_ATTR_T]

# BGP ORIGIN Types
# Defined in RFC4271
ORIGIN_T = {
    0:'IGP',
    1:'EGP',
    2:'INCOMPLETE',
}
dl += [ORIGIN_T]

# BGP AS_PATH Types
# Defined in RFC4271
AS_PATH_SEG_T = {
    1:'AS_SET',
    2:'AS_SEQUENCE',
}
dl += [AS_PATH_SEG_T]

# Reserved BGP COMMUNITY Types
# Defined in RFC1997
COMM_T = {
    0xffffff01:'NO_EXPORT',
    0xffffff02:'NO_ADVERTISE',
    0xffffff03:'NO_EXPORT_SCONFED',
    0xffffff04:'NO_PEER',           # Defined in RFC3765
}
dl += [COMM_T]

# BGP Message Types
# Defined in RFC4271
BGP_MSG_T = {
    0:'Reserved',
    1:'OPEN',
    2:'UPDATE',
    3:'NOTIFICATION',
    4:'KEEPALIVE',
    5:'ROUTE-REFRESH', # Defined in RFC2918
}
dl += [BGP_MSG_T]

# BGP Error Codes
# Defined in RFC4271
BGP_ERR_C = {
    0:'Reserved',
    1:'Message Header Error',
    2:'OPEN Message Error',
    3:'UPDATE Message Error',
    4:'Hold Timer Expired',
    5:'Finite State Machine Error',
    6:'Cease',
}
dl += [BGP_ERR_C]

# BGP Message Header Error Subcodes
# Defined in RFC4271
BGP_HDR_ERR_SC = {
    0:'Reserved',
    1:'Connection Not Synchronized',
    2:'Bad Message Length',
    3:'Bad Message Type',
}
dl += [BGP_HDR_ERR_SC]

# OPEN Message Error Subcodes
# Defined in RFC4271
BGP_OPEN_ERR_SC = {
    0:'Reserved',
    1:'Unsupported Version Number',
    2:'Bad Peer AS',
    3:'Bad BGP Identifier',
    4:'Unsupported Optional Parameter',
    5:'[Deprecated]',
    6:'Unacceptable Hold Time',
    7:'Unsupported Capability',         # Defined in RFC5492
}
dl += [BGP_OPEN_ERR_SC]

# UPDATE Message Error Subcodes
# Defined in RFC4271
BGP_UPDATE_ERR_SC = {
    0:'Reserved',
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
}
dl += [BGP_UPDATE_ERR_SC]

# BGP Finite State Machine Error Subcodes
# Defined in RFC6608
BGP_FSM_ERR_SC = {
    0:'Unspecified Error',
    1:'Receive Unexpected Message in OpenSent State',
    2:'Receive Unexpected Message in OpenConfirm State',
    3:'Receive Unexpected Message in Established State',
}
dl += [BGP_FSM_ERR_SC]

# BGP Cease NOTIFICATION Message Subcodes
# Defined in RFC4486
BGP_CEASE_ERR_SC = {
    0:'Reserved',
    1:'Maximum Number of Prefixes Reached',
    2:'Administrative Shutdown',
    3:'Peer De-configured',
    4:'Administrative Reset',
    5:'Connection Rejected',
    6:'Other Configuration Change',
    7:'Connection Collision Resolution',
    8:'Out of Resources',
}
dl += [BGP_CEASE_ERR_SC]

# BGP Error Subcodes
BGP_MSG_ERR_SC = {
    1:BGP_HDR_ERR_SC,
    2:BGP_UPDATE_ERR_SC,
    3:BGP_OPEN_ERR_SC,
    4:BGP_UPDATE_ERR_SC,
    5:BGP_FSM_ERR_SC,
    6:BGP_CEASE_ERR_SC,
}

# BGP OPEN Optional Parameter Types
# Defined in RFC5492
BGP_OPT_PARAMS_T = {
    0:'Reserved',
    1:'Authentication', # Deprecated
    2:'Capabilities',
}
dl += [BGP_OPT_PARAMS_T]

# Capability Codes
# Defined in RFC5492
CAP_CODE_T = {
    0:'Reserved',
    1:'Multiprotocol Extensions for BGP-4',                     # Defined in RFC2858
    2:'Route Refresh Capability for BGP-4',                     # Defined in RFC2918
    3:'Outbound Route Filtering Capability',                    # Defined in RFC5291
    4:'Multiple routes to a destination capability',            # Defined in RFC3107
    5:'Extended Next Hop Encoding',                             # Defined in RFC5549
    64:'Graceful Restart Capability',                           # Defined in RFC4724
    65:'Support for 4-octet AS number capability',              # Defined in RFC6793
    66:'[Deprecated]',
    67:'Support for Dynamic Capability (capability specific)',  # draft-ietf-idr-dynamic-cap
    68:'Multisession BGP Capability',                           # draft-ietf-idr-bgp-multisession
    69:'ADD-PATH Capability',                                   # draft-ietf-idr-add-paths
    70:'Enhanced Route Refresh Capability',                     # draft-keyur-bgp-enhanced-route-refresh
    71:'Long-Lived Graceful Restart (LLGR) Capability',         # draft-uttaro-idr-bgp-persistence
}
dl += [CAP_CODE_T]

MULTI_EXT_T = {
    1:'AFI',
    2:'Reserved',
    3:'SAFI',
}
dl += [MULTI_EXT_T]

ROUTE_REFRESH_CAP_T = {
    1:'AFI',
    2:'Reserved',
    3:'SAFI',
}
dl += [ROUTE_REFRESH_CAP_T]

OUT_ROUTE_FILTER_CAP_T = {
    1:'AFI',
    2:'Reserved',
    3:'SAFI',
    4:'Number of ORFs',
    5:'ORF Type',
    6:'Send/Receive',
}
dl += [OUT_ROUTE_FILTER_CAP_T]

MULTI_ROUTES_DEST_T = {
    1:'Label',
    2:'Prefix variable',
}
dl += [MULTI_ROUTES_DEST_T]

EXT_NEXT_HOP_ENC = {
    1:'NLRI AFI',
    2:'NLRI SAFI',
    3:'Nexthop AFI',
}
dl += [EXT_NEXT_HOP_ENC]

GRACEFUL_RESTART_T = {
    1:'Restart Flags',
    2:'Restart Time in seconds',
    3:'AFI',
    4:'SAFI',
    5:'Flags for Address Family',
}
dl += [GRACEFUL_RESTART_T]

SUPPORT_FOR_AS = {
    1:'AS Number',
}
dl += [SUPPORT_FOR_AS]

# Reverse the keys and values of dictionaries above
for d in dl:
    for k in list(d.keys()):
        d[d[k]] = k

# Function to get a value by specified keys from dictionaries above
def val_dict(d, *args):
    k = args[0]
    if k in d:
        if isinstance(d[k], dict) and len(args) > 1:
            return val_dict(d[k], *args[1:])
        return d[k]
    return 'Unassigned'

# Super class for all other classes
class Base:
    def __init__(self):
        self.p = 0

    def val_num(self, buf, _len):
        if _len == 1:
            fmt = '>B'
        elif _len == 2:
            fmt = '>H'
        elif _len == 4:
            fmt = '>I'
        elif _len == 8:
            fmt = '>Q'
        else:
            return None
        if _len > 0 and len(buf) - self.p >= _len:
            val = struct.unpack(fmt, buf[self.p:self.p+_len])[0]
        else:
            val = None
        self.p += _len
        return val

    def val_str(self, buf, _len):
        if _len > 0 and len(buf) - self.p >= _len:
            val = buf[self.p:self.p+_len]
        else:
            val = None
        self.p += _len
        return val

    def val_addr(self, buf, af, *args):
        if af == AFI_T['AFI_IPv4']:
            _max = 4
            _af = socket.AF_INET
        elif af == AFI_T['AFI_IPv6']:
            _max = 16
            _af = socket.AF_INET6
        else:
            _len = -1
        if len(args) != 0:
            _len = int(args[0] / 8)
            if args[0] % 8: _len += 1
        else:
            _len = _max
        if _len >= 0 and len(buf) - self.p >= _len:
            addr = socket.inet_ntop(
                _af, buf[self.p:self.p+_len] + b'\x00'*(_max - _len))
        else:
            addr = None
        self.p += _len
        return addr

    def val_asn(self, buf):
        global as_len
        asn = self.val_num(buf, as_len)
        if as_len == 4 and asn > 65535:
            asn = str(asn >> 16) + '.' + str(asn & 0xffff)
        else:
            asn = str(asn)
        return asn

class Reader(Base):
    def __init__(self, arg):
        Base.__init__(self)

        if hasattr(arg, 'read'):
            self.f = arg
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
            sys.stderr.write("error: unsupported instance type\n")

    def close(self):
        self.f.close()
        raise StopIteration

    def __iter__(self):
        return self

    def next(self):
        global as_len
        as_len = 4
        self.mrt = Mrt()
        self.unpack()
        return self.mrt

    def __next__(self):
        global as_len
        as_len = 4
        self.mrt = Mrt()
        self.unpack()
        return self.mrt

    def unpack(self):
        global as_len
        hdr = self.f.read(MRT_HDR_LEN)
        if len(hdr) == 0:
            self.close()
        elif len(hdr) < MRT_HDR_LEN:
            sys.stderr.write("error: mrt header is too short\n")
            self.close()
        self.mrt.unpack(hdr)
        data = self.f.read(self.mrt.len)
        if len(data) < self.mrt.len:
            sys.stderr.write("error: mrt data is too short\n")
            self.close()

        if (   self.mrt.type == MSG_T['BGP4MP_ET']
            or self.mrt.type == MSG_T['ISIS_ET']
            or self.mrt.type == MSG_T['OSPFv3_ET']):
            self.mrt.micro_ts = self.val_num(data, 4)

        if self.mrt.type == MSG_T['TABLE_DUMP']:
            as_len = 2
            self.mrt.table_dump = TableDump()
            self.mrt.table_dump.unpack(data, self.mrt.subtype)
        elif self.mrt.type == MSG_T['TABLE_DUMP_V2']:
            self.unpack_td_v2(data)
        elif ( self.mrt.type == MSG_T['BGP4MP']
            or self.mrt.type == MSG_T['BGP4MP_ET']):
            self.mrt.bgp = Bgp4Mp()
            self.mrt.bgp.unpack(data, self.mrt.subtype)
        elif ( self.mrt.type == MSG_T['ISIS_ET']
            or self.mrt.type == MSG_T['OSPFv3_ET']):
            self.p += self.len - 4
        else:
            self.p += self.len
        return self.p

    def unpack_td_v2(self, data):
        if self.mrt.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
            self.mrt.peer = PeerIndexTable()
            self.mrt.peer.unpack(data)
        elif ( self.mrt.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
            or self.mrt.subtype == TD_V2_ST['RIB_IPV4_MULTICAST']):
            self.mrt.rib = AfiSpecRib()
            self.mrt.rib.unpack(data, AFI_T['AFI_IPv4'])
        elif ( self.mrt.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
            or self.mrt.subtype == TD_V2_ST['RIB_IPV6_MULTICAST']):
            self.mrt.rib = AfiSpecRib()
            self.mrt.rib.unpack(data, AFI_T['AFI_IPv6'])
        else:
            self.p += self.len

class Mrt(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        self.ts = self.val_num(buf, 4)
        self.type = self.val_num(buf, 2)
        self.subtype = self.val_num(buf, 2)
        self.len = self.val_num(buf, 4)
        return self.p

class TableDump(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf, subtype):
        self.view = self.val_num(buf, 2)
        self.seq = self.val_num(buf, 2)
        self.prefix = self.val_addr(buf, subtype)
        self.len = self.val_num(buf, 1)
        self.status = self.val_num(buf, 1)
        self.org_time = self.val_num(buf, 4)
        self.peer_ip = self.val_addr(buf, subtype)
        self.peer_as = self.val_asn(buf)
        attr_len = self.attr_len = self.val_num(buf, 2)
        self.attr = []
        while attr_len > 0:
            attr = BgpAttr()
            self.p += attr.unpack(buf[self.p:])
            self.attr.append(attr)
            attr_len -= attr.p
        return self.p

class PeerIndexTable(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        self.collector = self.val_addr(buf, AFI_T['AFI_IPv4'])
        self.view_len = self.val_num(buf, 2)
        self.view = self.val_str(buf, self.view_len)
        self.count = self.val_num(buf, 2)
        self.entry = []
        for i in range(self.count):
            entry = PeerEntries()
            self.p += entry.unpack(buf[self.p:])
            self.entry.append(entry)
        return self.p

class PeerEntries(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        global as_len
        self.type = self.val_num(buf, 1)
        self.bgp_id = self.val_addr(buf, AFI_T['AFI_IPv4'])
        if self.type & 0x01:
            af = AFI_T['AFI_IPv6'] 
        else:
            af = AFI_T['AFI_IPv4']
        self.ip = self.val_addr(buf, af)
        as_len = 4 if self.type & (0x01 << 1) else 2
        self.asn = self.val_asn(buf)
        return self.p

class AfiSpecRib(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf, af):
        self.seq = self.val_num(buf, 4)
        self.plen = self.val_num(buf, 1)
        self.prefix = self.val_addr(buf, af, self.plen)
        self.count = self.val_num(buf, 2)
        self.entry = []
        for i in range(self.count):
            entry = RibEntries()
            self.p += entry.unpack(buf[self.p:])
            self.entry.append(entry)
        return self.p

class RibEntries(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        self.peer_index = self.val_num(buf, 2)
        self.org_time = self.val_num(buf, 4)
        attr_len = self.attr_len = self.val_num(buf, 2)

        self.attr = []
        while attr_len > 0:
            attr = BgpAttr()
            self.p += attr.unpack(buf[self.p:])
            self.attr.append(attr)
            attr_len -= attr.p
        return self.p

class Bgp4Mp(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf, subtype):
        global as_len
        if (   subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
            or subtype == BGP4MP_ST['BGP4MP_MESSAGE']
            or subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']):
            as_len = 2
        elif ( subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
            or subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']
            or subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
            as_len = 4

        self.peer_as = self.val_asn(buf)
        self.local_as = self.val_asn(buf)
        self.ifindex = self.val_num(buf, 2)
        self.af = self.val_num(buf, 2)
        self.peer_ip = self.val_addr(buf, self.af)
        self.local_ip = self.val_addr(buf, self.af)

        if (   subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
            or subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
            self.old_state = self.val_num(buf, 2)
            self.new_state = self.val_num(buf, 2)
        else:
            self.msg = BgpMessage()
            self.p += self.msg.unpack(buf[self.p:], self.af)
        return self.p

class BgpMessage(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf, af):
        self.marker = self.val_str(buf, 16)
        self.len = self.val_num(buf, 2)
        self.type = self.val_num(buf, 1)
        if self.type == BGP_MSG_T['OPEN']:
            self.ver = self.val_num(buf, 1)
            self.my_as = self.val_num(buf, 2)
            self.holdtime = self.val_num(buf, 2)
            self.bgp_id = self.val_addr(buf, af)
            opt_len = self.opt_len = self.val_num(buf, 1)
            self.opt_params = []
            while opt_len > 0:
                opt_params = OptParams()
                self.p += opt_params.unpack(buf[self.p:])
                self.opt_params.append(opt_params)
                opt_len -= opt_params.p
        elif self.type == BGP_MSG_T['UPDATE']:
            wd_len = self.wd_len = self.val_num(buf, 2)
            self.withdrawn = []
            while wd_len > 0:
                withdrawn    = Nlri()
                self.p += withdrawn.unpack(buf[self.p:], af)
                self.withdrawn.append(withdrawn)
                wd_len -= withdrawn.p

            attr_len = self.attr_len = self.val_num(buf, 2)
            self.attr = []
            while attr_len > 0:
                attr = BgpAttr()
                self.p += attr.unpack(buf[self.p:])
                self.attr.append(attr)
                attr_len -= attr.p

            self.nlri = []
            while self.p > self.len:
                nlri = Nlri()
                self.p += nlri.unpack(buf[self.p:], af)
                self.nlri.append(nlri)
        elif self.type == BGP_MSG_T['NOTIFICATION']:
            self.err_code = self.val_num(buf, 1)
            self.err_subcode = self.val_num(buf, 1)
            self.data = self.val_num(buf, self.len - self.p)                
        elif self.type == BGP_MSG_T['KEEPALIVE']:
            pass
        else:
            self.p += self.len - self.p
        return self.p

class OptParams(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        self.type = self.val_num(buf, 1)
        self.len = self.val_num(buf, 1)

        if self.type != BGP_OPT_PARAMS_T['Capabilities']:
            self.p += self.len
            return self.p

        self.cap_type = self.val_num(buf, 1)
        self.cap_len = self.val_num(buf, 1)
        if self.cap_type == CAP_CODE_T['Multiprotocol Extensions for BGP-4']:
            self.unpack_multi_ext(buf)
        elif self.cap_type == CAP_CODE_T['Route Refresh Capability for BGP-4']:
            self.unpack_route_refresh(buf)
        elif self.cap_type == CAP_CODE_T['Outbound Route Filtering Capability']:
            self.unpack_out_route_filter(buf)
        elif self.cap_type == CAP_CODE_T['Multiple routes to a destination capability']:
            self.unpack_multi_routes_dest(buf)
        elif self.cap_type == CAP_CODE_T['Extended Next Hop Encoding']:
            self.unpack_ext_next_hop(buf)
        elif self.cap_type == CAP_CODE_T['Graceful Restart Capability']:
            self.unpack_graceful_restart(buf)
        elif self.cap_type == CAP_CODE_T['Support for 4-octet AS number capability']:
            self.unpack_support_for_as(buf)
        else:
            self.p += self.len - 2
        return self.p

    def unpack_multi_ext(self, buf):
        self.multi_ext = {}
        self.multi_ext['afi'] = self.val_num(buf, 2)
        self.multi_ext['reserved'] = self.val_num(buf, 1)
        self.multi_ext['safi'] = self.val_num(buf, 1)
   
    def unpack_route_refresh(self, buf):
        self.route_refresh = {}
        # self.route_refresh['afi'] = self.val_num(buf, 2)
        # self.route_refresh['reserved'] = self.val_num(buf, 1)
        # self.route_refresh['safi'] = self.val_num(buf, 1)

    def unpack_out_route_filter(self, buf):
        self.orf = {}
        self.orf['afi'] = self.val_num(buf, 2)
        self.orf['reserved'] = self.val_num(buf, 1)
        self.orf['safi'] = self.val_num(buf, 1)
        self.orf['number_of_orfs'] = self.val_num(buf, 1)
        self.orf['orf_type'] = self.val_num(buf, 1)
        self.orf['send_receive'] = self.val_num(buf, 1)

    def unpack_multi_routes_dest(self, buf):
        self.multi_routes_dest = {}
        cap_len = self.cap_len
        self.multi_routes_dest['label'] = self.val_num(buf, 3)
        while cap_len  > 3:
            self.multi_routes_dest['prefix'] = self.val_num(buf, 1)
            cap_len -= 1

    def unpack_ext_next_hop(self, buf):
        self.ext_next_hop = {}
        cap_len = self.cap_len
        while cap_len > 5:
            self.ext_next_hop['nlri_afi'] = self.val_num(buf, 2)
            self.ext_next_hop['nlri_safi'] = self.val_num(buf, 2)
            self.ext_next_hop['nexthop_afi'] = self.val_num(buf, 2)
            cap_len -= 6

    def unpack_graceful_restart(self, buf):
        self.graceful_restart = {}
        self.graceful_restart['timer'] = self.val_num(buf, 2)
        cap_len = self.cap_len
        if cap_len > 2:
        # self.graceful_restart['restart_flags'] = self.val_num(buf, 1)
        # self.graceful_restart['restart_time_in_seconds'] = self.val_num(buf, 1)
            while cap_len > 2:
                self.graceful_restart['afi'] = self.val_num(buf, 2)
                cap_len -= 2
                self.graceful_restart['safi'] = self.val_num(buf, 1)
                cap_len -= 1
                self.graceful_restart['flags_for_afi'] = self.val_num(buf, 1)
                cap_len -= 1

    def unpack_support_for_as(self, buf):
        # self.support_for_as = self.val_num(buf, 2)
        self.support_for_as = {}
        self.support_for_as['as_number'] = self.val_num(buf, 4)

class BgpAttr(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        global as_len
        self.flag = self.val_num(buf, 1)
        self.type = self.val_num(buf, 1)

        if self.flag & 0x01 << 4:
            self.len = self.val_num(buf, 2)
        else:
            self.len = self.val_num(buf, 1)

        if self.len == 0: return self.p

        if self.type == BGP_ATTR_T['ORIGIN']:
            self.unpack_origin(buf)
        elif self.type == BGP_ATTR_T['AS_PATH']:
            self.unpack_as_path(buf)
        elif self.type == BGP_ATTR_T['NEXT_HOP']:
            self.unpack_next_hop(buf)
        elif self.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
            self.unpack_multi_exit_disc(buf)
        elif self.type == BGP_ATTR_T['LOCAL_PREF']:
            self.unpack_local_pref(buf)
        elif self.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
            pass
        elif self.type == BGP_ATTR_T['AGGREGATOR']:
            self.unpack_aggregator(buf)
        elif self.type == BGP_ATTR_T['COMMUNITY']:
            self.unpack_community(buf)
        elif self.type == BGP_ATTR_T['ORIGINATOR_ID']:
            self.unpack_originator_id(buf)
        elif self.type == BGP_ATTR_T['CLUSTER_LIST']:
            self.unpack_cluster_list(buf)
        elif self.type == BGP_ATTR_T['MP_REACH_NLRI']:
            self.unpack_mp_reach_nlri(buf)
        elif self.type == BGP_ATTR_T['MP_UNREACH_NLRI']:
            self.unpack_mp_unreach_nlri(buf)
        elif self.type == BGP_ATTR_T['EXTENDED_COMMUNITIES']:
            self.unpack_extended_communities(buf)
        elif self.type == BGP_ATTR_T['AS4_PATH']:
            as_len = 4
            self.unpack_as_path(buf)
        elif self.type == BGP_ATTR_T['AS4_AGGREGATOR']:
            self.unpack_aggregator(buf)
        else:
            self.p += self.len
        return self.p

    def unpack_origin(self, buf):
        self.origin = self.val_num(buf, 1)

    def unpack_as_path(self, buf):
        global as_len
        self.as_path = []
        attr_len = self.p + self.len
        while self.p < attr_len:
            seg_val = []
            seg_type = self.val_num(buf, 1)
            seg_len = self.val_num(buf, 1)
            if seg_len == 0: next

            for i in range(seg_len):
                seg_val.append(self.val_asn(buf))

            if seg_type == 1:
                self.as_path.append('{%s}' % ' '.join(seg_val))
            else:
                self.as_path.append(' '.join(seg_val))

    def unpack_next_hop(self, buf):
        if self.len == 4:
            self.next_hop = self.val_addr(buf, AFI_T['AFI_IPv4'])
        elif self.len == 16:
            self.next_hop = self.val_addr(buf, AFI_T['AFI_IPv6'])
        else:
            self.p += self.len
            self.next_hop = None

    def unpack_multi_exit_disc(self, buf):
        self.med = self.val_num(buf, 4)

    def unpack_local_pref(self, buf):
        self.local_pref = self.val_num(buf, 4)

    def unpack_aggregator(self, buf):
        global as_len
        self.aggr = {}
        if self.len < 8:
            as_len = 2
        else:
            as_len = 4
        self.aggr['asn'] = self.val_asn(buf)
        self.aggr['id'] = self.val_addr(buf, AFI_T['AFI_IPv4'])

    def unpack_community(self, buf):
        self.comm = []
        attr_len = self.p + self.len
        while self.p < attr_len:
            val = self.val_num(buf, 4)
            self.comm.append('%d:%d' % 
                ((val & 0xffff0000) >> 16, val & 0x0000ffff))

    def unpack_originator_id(self, buf):
        self.org_id= self.val_addr(buf, AFI_T['AFI_IPv4'])

    def unpack_cluster_list(self, buf):
        self.cl_list = []
        attr_len = self.p + self.len
        while self.p < attr_len:
            self.cl_list.append(self.val_addr(buf, AFI_T['AFI_IPv4']))

    def unpack_mp_reach_nlri(self, buf):
        attr_len = self.p + self.len
        self.mp_reach = {}
        self.mp_reach['afi'] = self.val_num(buf, 2)
        self.mp_reach['safi'] = self.val_num(buf, 1)
        self.mp_reach['nlen'] = self.val_num(buf, 1)

        if (    self.mp_reach['afi'] != AFI_T['AFI_IPv4']
            and self.mp_reach['afi'] != AFI_T['AFI_IPv6']):
            self.p = attr_len
            return

        if (    self.mp_reach['safi'] != SAFI_T['SAFI_UNICAST']
            and self.mp_reach['safi'] != SAFI_T['SAFI_MULTICAST']):
            self.p = attr_len
            return

        self.mp_reach['next_hop'] = self.val_addr(
            buf, self.mp_reach['afi'], self.mp_reach['nlen']*8)
        self.mp_reach['rsvd'] = self.val_num(buf, 1)

        self.mp_reach['nlri'] = []
        while self.p < attr_len:
            nlri = Nlri()
            self.p += nlri.unpack(buf[self.p:], self.mp_reach['afi'])
            self.mp_reach['nlri'].append(nlri)

    def unpack_mp_unreach_nlri(self, buf):
        attr_len = self.p + self.len
        self.mp_unreach = {}
        self.mp_unreach['afi'] = self.val_num(buf, 2)
        self.mp_unreach['safi'] = self.val_num(buf, 1)

        if (    self.mp_unreach['afi'] != AFI_T['AFI_IPv4']
            and self.mp_unreach['afi'] != AFI_T['AFI_IPv6']):
            self.p = attr_len
            return

        if (    self.mp_unreach['safi'] != SAFI_T['SAFI_UNICAST']
            and self.mp_unreach['safi'] != SAFI_T['SAFI_MULTICAST']):
            self.p = attr_len
            return

        self.mp_unreach['withdrawn'] = []
        while self.p < attr_len:
            withdrawn = Nlri()
            self.p += withdrawn.unpack(buf[self.p:], self.mp_unreach['afi'])
            self.mp_unreach['withdrawn'].append(withdrawn)

    def unpack_extended_communities(self, buf):
        self.ext_comm = []
        attr_len = self.p + self.len
        while self.p < attr_len:
            ext_comm = self.val_num(buf, 8)
            self.ext_comm.append(ext_comm)

class Nlri(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf, af):
        self.plen = self.val_num(buf, 1)
        self.prefix = self.val_addr(buf, af, self.plen)
        return self.p

