'''
mrtparse - MRT format data parser

Copyright (C) 2022 Tetsumune KISO

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

import struct
import socket
import collections
import sys
from .params import *

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

def af_num(afi=None, safi=None):
    '''
    the values of AFI/SAFI.
    '''
    if afi is not None:
        af_num.afi = afi
        af_num.safi = safi
    try:
        return (af_num.afi, af_num.safi)
    except AttributeError:
        return (0, 0)

def is_add_path(f=None):
    '''
    Flag for add-path.
    '''
    if f is not None:
        is_add_path.f = f
    try:
        return is_add_path.f
    except AttributeError:
        return False

class MrtFormatError(Exception):
    '''
    Exception for invalid MRT formatted data.
    '''
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg

class _Base:
    '''
    Super class for all other classes.
    '''
    __slots__ = ['data', 'buf', 'p']

    def __init__(self):
        for slot in self.__slots__:
            setattr(self, slot, None)
        self.data = collections.OrderedDict()
        self.p = 0

    def chk_buf(self, n):
        '''
        Check whether there is sufficient buffers.
        '''
        if len(self.buf) - self.p < n:
            raise MrtFormatError(
                'Insufficient buffer %d < %d byte' % (len(self.buf) - self.p, n)
            )

    def val_num(self, n):
        '''
        Convert buffers to integer.
        '''
        pass

    def val_bytes(self, n):
        '''
        Convert buffers to bytes.
        '''
        pass

    def val_str(self, n):
        '''
        Convert buffers to string.
        '''
        pass

    def val_addr(self, af, plen=-1):
        '''
        Convert buffers to IP address.
        '''
        pass

    def val_as(self, n):
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
            if is_add_path():
                raise MrtFormatError
            p = self.p
            nlri_list = []
            while p < n:
                nlri = Nlri(self.buf[p:])
                p += nlri.unpack(af, saf)
                nlri_list.append(nlri.data)

            # Check whether duplicate routes exist in NLRI
            if len(nlri_list) > 0 and len(nlri_list) != \
                len(set(map(lambda x: str(x.values()), nlri_list))):
                raise MrtFormatError
            self.p = p
        except MrtFormatError:
            nlri_list = []
            while self.p < n:
                nlri = Nlri(self.buf[self.p:])
                self.p += nlri.unpack(af, saf, add_path=1)
                nlri_list.append(nlri.data)
        return nlri_list

class _BasePy2(_Base):
    '''
    Super class for all other classes in Python2.
    '''
    __slots__ = []

    def __init__(self):
        _Base.__init__(self)

    def val_num(self, n):
        '''
        Convert buffers to integer.
        '''
        self.chk_buf(n)
        val = 0
        for i in self.buf[self.p:self.p+n]:
            val = (val << 8) + struct.unpack('>B', i)[0]
        self.p += n
        return val

    def val_bytes(self, n):
        '''
        Convert buffers to bytes.
        '''
        self.chk_buf(n)
        val = ' '.join(['%02x' % ord(buf) for buf in self.buf[self.p:self.p+n]])
        self.p += n
        return val

    def val_str(self, n):
        '''
        Convert buffers to string.
        '''
        self.chk_buf(n)
        val = self.buf[self.p:self.p+n]
        self.p += n
        return val

    def val_addr(self, af, plen=-1):
        '''
        Convert buffers to IP address.
        '''
        if af == AFI_T['IPv4']:
            plen_max = 32
            _af = socket.AF_INET
        elif af == AFI_T['IPv6']:
            plen_max = 128
            _af = socket.AF_INET6
        else:
            raise MrtFormatError('Unsupported AFI %d(%s)' % (af, AFI_T[af]))
        if plen < 0:
            plen = plen_max
        elif plen > plen_max:
            raise MrtFormatError(
                'Invalid prefix length %d (%s)' % (plen, AFI_T[af])
            )
        n = (plen + 7) // 8
        self.chk_buf(n)
        buf = self.buf[self.p:self.p+n]
        addr = socket.inet_ntop(_af, buf + b'\x00'*(plen_max // 8 - n))
        # A prefix like "192.168.0.0/9" is invalid
        if plen % 8:
            num = int(buf.encode('hex'), 16)
            if num & ~(-1 << (n * 8 - plen)):
                raise MrtFormatError('Invalid prefix %s/%d' % (addr, plen))
        self.p += n
        return addr

class _BasePy3(_Base):
    '''
    Super class for all other classes in Python3.
    '''
    __slots__ = []

    def __init__(self):
        _Base.__init__(self)

    def val_num(self, n):
        '''
        Convert buffers to integer.
        '''
        self.chk_buf(n)
        val = 0
        for i in self.buf[self.p:self.p+n]:
            val = (val << 8) + i
        self.p += n
        return val

    def val_bytes(self, n):
        '''
        Convert buffers to bytes.
        '''
        self.chk_buf(n)
        val = ' '.join(['%02x' % buf for buf in self.buf[self.p:self.p+n]])
        self.p += n
        return val

    def val_str(self, n):
        '''
        Convert buffers to string.
        '''
        self.chk_buf(n)
        val = self.buf[self.p:self.p+n].decode('utf-8')
        self.p += n
        return val

    def val_addr(self, af, plen=-1):
        '''
        Convert buffers to IP address.
        '''
        if af == AFI_T['IPv4']:
            plen_max = 32
            _af = socket.AF_INET
        elif af == AFI_T['IPv6']:
            plen_max = 128
            _af = socket.AF_INET6
        else:
            raise MrtFormatError('Unsupported AFI %d(%s)' % (af, AFI_T[af]))
        if plen < 0:
            plen = plen_max
        elif plen > plen_max:
            raise MrtFormatError(
                'Invalid prefix length %d (%s)' % (plen, AFI_T[af])
            )
        n = (plen + 7) // 8
        self.chk_buf(n)
        buf = self.buf[self.p:self.p+n]
        addr = socket.inet_ntop(_af, buf + b'\x00'*(plen_max // 8 - n))
        # A prefix like "192.168.0.0/9" is invalid
        if plen % 8:
            num = int.from_bytes(buf, 'big')
            if num & ~(-1 << (n * 8 - plen)):
                raise MrtFormatError('Invalid prefix %s/%d' % (addr, plen))
        self.p += n
        return addr

if sys.version_info.major == 3:
    Base = _BasePy3
else:
    Base = _BasePy2

class Nlri(Base):
    '''
    Class for NLRI.
    '''
    __slots__ = []

    def __init__(self, buf):
        Base.__init__(self)
        self.buf = buf

    def unpack(self, af, saf=0, add_path=0):
        '''
        Decoder for NLRI.
        '''
        if add_path:
            self.data['path_id'] = self.val_num(4)
        self.data['length'] = plen = self.val_num(1)
        if saf == SAFI_T['L3VPN_UNICAST'] or saf == SAFI_T['L3VPN_MULTICAST']:
            plen = self.unpack_l3vpn(plen)
        if af == AFI_T['IPv4'] and plen > 32 \
            or af == AFI_T['IPv6'] and plen > 128:
            raise MrtFormatError(
                'Invalid prefix length %d (%s)'
                % (self.data['length'], AFI_T[af])
            )
        self.data['prefix'] = self.val_addr(af, plen)
        return self.p

    def unpack_l3vpn(self, plen):
        '''
        Decoder for L3VPN NLRI.
        '''
        self.data['label'] = []
        while True:
            label = self.val_num(3)
            self.data['label'].append(label)
            if label & LBL_BOTTOM or label == LBL_WITHDRAWN:
                break
        self.data['route_distinguisher'] = self.val_rd()
        plen -= (3 * len(self.data['label']) + 8) * 8
        return plen
