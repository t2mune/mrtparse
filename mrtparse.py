'''
mrtparse is a module to parse a MRT format data.

See http://*** for more informations.
This module is published under a *** license.
Created by
    Tetsumune KISO <t2mune@gmail.com>,
    Yoshiyuki YAMAUCHI <y.44snow@gmail.com>,
    Nobuhiro ITOU <js333123@gmail.com>.
Copyright (C) GREEN HIPPO. All rights reserved.
'''

import sys, struct, socket
import gzip, bz2

# mrtparse information
__pyname__  = 'mrtparse'
__version__ =  '0.5'
__descr__   = 'parse a MRT-format data'
__url__     = 'http://***'
__author__  = 'Tetsumune KISO, Yoshiyuki YAMAUCHI, Nobuhiro ITOU'
__email__   = 't2mune@gmail.com, y.44snow@gmail.com, js333123@gmail.com'
__license__ = '***'

# Magic Number
GZIP_MAGIC = '\x1f\x8b'
BZ2_MAGIC  = '\x42\x5a\x68'

# a variable to reverse the keys and values of dictionaries below
dl = []

# AS number length(especially to use AS_PATH attribute)
as_len = 4

# MRT header length
MRT_HDR_LEN = 12

# Message types
# Defined in RFC6396
MSG_T = {
    0L:'NULL',           # Deprecated in RFC6396
    1L:'START',          # Deprecated in RFC6396
    2L:'DIE',            # Deprecated in RFC6396
    3L:'I_AM_DEAD',      # Deprecated in RFC6396
    4L:'PEER_DOWN',      # Deprecated in RFC6396
    5L:'BGP',            # Deprecated in RFC6396
    6L:'RIP',            # Deprecated in RFC6396
    7L:'IDRP',           # Deprecated in RFC6396
    8L:'RIPNG',          # Deprecated in RFC6396
    9L:'BGP4PLUS',       # Deprecated in RFC6396
    10L:'BGP4PLUS_01',   # Deprecated in RFC6396
    11L:'OSPFv2',
    12L:'TD',
    13L:'TD_V2',
    16L:'BGP4MP',
    17L:'BGP4MP_ET',
    32L:'ISIS',
    33L:'ISIS_ET',
    48L:'OSPFv3',
    49L:'OSPFv3_ET', 
}
dl = dl + [MSG_T]

# BGP,BGP4PLUS,BGP4PLUS_01 subtypes
# Deprecated in RFC6396
BGP_ST = {
    0L:'BGP_NULL',
    1L:'BGP_UPDATE',
    2L:'BGP_PREF_UPDATE',
    3L:'BGP_STATE_CHANGE',
    4L:'BGP_SYNC', 
    5L:'BGP_OPEN',
    6L:'BGP_NOTIFY',
    7L:'BGP_KEEPALIVE',
}
dl = dl + [BGP_ST]

# TD subtypes
# Defined in RFC6396
TD_ST = {
    1L:'AFI_IPv4',
    2L:'AFI_IPv6',
}
dl = dl + [TD_ST]

# TD_V2 subtypes
# Defined in RFC6396
TD_V2_ST = {
    1L:'PEER_INDEX_TABLE',
    2L:'RIB_IPV4_UNICAST',
    3L:'RIB_IPV4_MULTICAST',
    4L:'RIB_IPV6_UNICAST',
    5L:'RIB_IPV6_MULTICAST',
    6L:'RIB_GENERIC',
}
dl = dl + [TD_V2_ST]

# BGP4MP,BGP4MP_ET subtypes
# Defined in RFC6396
BGP4MP_ST = {
    0L:'BGP4MP_STATE_CHANGE',
    1L:'BGP4MP_MESSAGE',
    4L:'BGP4MP_MESSAGE_AS4',
    5L:'BGP4MP_STATE_CHANGE_AS4',
    6L:'BGP4MP_MESSAGE_LOCAL',
    7L:'BGP4MP_MESSAGE_AS4_LOCAL',
}
dl = dl + [BGP4MP_ST]

# MRT Message subtypes
# Defined in RFC6396
MSG_ST = {
    9L:BGP_ST,
    10L:BGP_ST,
    12L:TD_ST,
    13L:TD_V2_ST,
    16L:BGP4MP_ST,
    17L:BGP4MP_ST,
}

# BGP FSM states
# Defined in RFC4271
BGP_FSM = {
    1L:'Idle',
    2L:'Connect',
    3L:'Active',
    4L:'OpenSent',
    5L:'OpenConfirm',
    6L:'Established',
}
dl = dl + [BGP_FSM]

# BGP attribute types
# Defined in RFC4271
BGP_ATTR_T = {
    1L:'ORIGIN',
    2L:'AS_PATH',
    3L:'NEXT_HOP',
    4L:'MULTI_EXIT_DISC',
    5L:'LOCAL_PREF',
    6L:'ATOMIC_AGGREGATE',
    7L:'AGGREGATOR',
    8L:'COMMUNITIES',           # Defined in RFC1997
    9L:'ORIGINATOR_ID',         # Defined in RFC4456
    10L:'CLUSTER_LIST',         # Defined in RFC4456
    11L:'DPA',                  # Deprecated in RFC6938
    12L:'ADVERTISER',           # Deprecated in RFC6938
    13L:'RCID_PATH/CLUSTER_ID', # Deprecated in RFC6938
    14L:'MP_REACH_NLRI',        # Defined in RFC4760
    15L:'MP_UNREACH_NLRI',      # Defined in RFC4760
    16L:'EXTENDED_COMMUNITIES', # Defined in RFC4360
    17L:'AS4_PATH',             # Defined in RFC6793
    18L:'AS4_AGGREGATOR',       # Defined in RFC6793
}
dl = dl + [BGP_ATTR_T]

# BGP ORIGIN types
# Defined in RFC4271
ORIGIN_T = {
    0L:'IGP',
    1L:'EGP',
    2L:'INCOMPLETE',
}
dl = dl + [ORIGIN_T]

# BGP AS_PATH types
# Defined in RFC4271
AS_PATH_SEG_T = {
    1L:'AS_SET',
    2L:'AS_SEQUENCE',
}
dl = dl + [AS_PATH_SEG_T]

# Reserved BGP COMMUNITY types
# Defined in RFC1997
COMM_T = {
    0xffffff01L:'NO_EXPORT',
    0xffffff02L:'NO_ADVERTISE',
    0xffffff03L:'NO_EXPORT_SCONFED',
    0xffffff04L:'NO_PEER',           # Defined in RFC3765
}
dl = dl + [COMM_T]

# BGP message types
# Defined in RFC4271
BGP_MSG_T = {
    1L:'OPEN',
    2L:'UPDATE',
    3L:'NOTIFICATION',
    4L:'KEEPALIVE',
    5L:'ROUTE_REFRESH',
}
dl = dl + [BGP_MSG_T]

# Reverse the keys and values of dictionaries above
for d in dl:
    for k in d.keys():
        d[d[k]] = k

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
        if af == TD_ST['AFI_IPv4']:
            _max = 4
            _af = socket.AF_INET
        elif af == TD_ST['AFI_IPv6']:
            _max = 16
            _af = socket.AF_INET6
        else:
            _len = -1
        if len(args) != 0:
            _len = args[0] / 8
            if args[0] % 8: _len += 1
        else:
            _len = _max
        if _len >= 0 and len(buf) - self.p >= _len:
            addr = socket.inet_ntop(
                _af, buf[self.p:self.p+_len] + '\x00'*(_max - _len))
        else:
            addr = None
        self.p += _len
        return addr

    def val_asn(self, buf):
        global as_len
        asn = self.val_num(buf, as_len)
        if as_len == 4 and asn > 65535:
            asn = str(asn >> 16) + '.' + str(asn & 0xffffL)
        else:
            asn = str(asn)
        return asn

class Reader(Base):
    def __init__(self, arg):
        Base.__init__(self)

        if hasattr(arg, 'read'):
            self.f = arg
        elif isinstance(arg, str):
            f = file(arg, 'rb')
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

        if self.mrt.type == MSG_T['TD']:
            as_len = 2
            self.mrt.table_dump = TableDump()
            self.mrt.table_dump.unpack(data, self.mrt.subtype)
        elif self.mrt.type == MSG_T['TD_V2']:
            if self.mrt.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
                self.mrt.peer = PeerIndexTable()
                self.mrt.peer.unpack(data)
            elif ( self.mrt.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
                or self.mrt.subtype == TD_V2_ST['RIB_IPV4_MULTICAST']):
                self.mrt.rib = AfiSpecRib()
                self.mrt.rib.unpack(data, TD_ST['AFI_IPv4'])
            elif ( self.mrt.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
                or self.mrt.subtype == TD_V2_ST['RIB_IPV6_MULTICAST']):
                self.mrt.rib = AfiSpecRib()
                self.mrt.rib.unpack(data, TD_ST['AFI_IPv6'])
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
        self.collector = self.val_addr(buf, TD_ST['AFI_IPv4'])
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
        self.bgp_id = self.val_addr(buf, TD_ST['AFI_IPv4'])
        if self.type & 0x01L:
            af = TD_ST['AFI_IPv6'] 
        else:
            af = TD_ST['AFI_IPv4']
        self.ip = self.val_addr(buf, af)
        as_len = 4 if self.type & (0x01L << 1) else 2
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

class BgpAttr(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        global as_len
        self.flag = self.val_num(buf, 1)
        self.type = self.val_num(buf, 1)

        if self.flag & 0x01L << 4:
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
        elif self.type == BGP_ATTR_T['COMMUNITIES']:
            self.unpack_communities(buf)
        elif self.type == BGP_ATTR_T['ORIGINATOR_ID']:
            self.unpack_originator_id(buf)
        elif self.type == BGP_ATTR_T['CLUSTER_LIST']:
            self.unpack_cluster_list(buf)
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
        attr_len = self.p + self.len
        self.as_path = []
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
            self.next_hop = self.val_addr(buf, TD_ST['AFI_IPv4'])
        elif self.len == 16:
            self.next_hop = self.val_addr(buf, TD_ST['AFI_IPv6'])
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
        self.aggr['id'] = self.val_addr(buf, TD_ST['AFI_IPv4'])

    def unpack_communities(self, buf):
        attr_len = self.p + self.len
        self.comm = []
        while self.p < attr_len:
            val = self.val_num(buf, 4)
            self.comm.append('%d:%d' % 
                ((val & 0xffff0000L) >> 16, val & 0x0000ffffL))

    def unpack_originator_id(self, buf):
        self.org_id= self.val_addr(buf, TD_ST['AFI_IPv4'])

    def unpack_cluster_list(self, buf):
        attr_len = self.p + self.len
        self.cl_list = []
        while self.p < attr_len:
            self.cl_list.append(self.val_addr(buf, TD_ST['AFI_IPv4']))

    def unpack_extended_communities(self, buf):
        attr_len = self.p + self.len
        self.ext_comm = []
        while self.p < attr_len:
            ext_comm = self.val_num(buf, 8)
            self.ext_comm.append(ext_comm)

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
        msg_len = self.len = self.val_num(buf, 2)
        self.type = self.val_num(buf, 1)
        if self.type == BGP_MSG_T['UPDATE']:
            wd_len = self.wd_len = self.val_num(buf, 2)
            self.withdrawn = []
            while wd_len > 0:
                withdrawn = Nlri()
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

            nlri_len = self.len - self.p
            self.nlri = []
            while nlri_len > 0:
                nlri = Nlri()
                self.p += nlri.unpack(buf[self.p:], af)
                self.nlri.append(nlri)
                nlri_len -= nlri.p
        else:
            self.p += self.len - 19
        return self.p

class Nlri(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf, af):
        self.plen = self.val_num(buf, 1)
        self.prefix = self.val_addr(buf, af, self.plen)
        return self.p
