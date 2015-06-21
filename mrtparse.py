'''
mrtparse.py - MRT format data parser

Copyright (C) 2015 greenHippo, LLC.

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

from abc import ABCMeta
import enum
import gzip, bz2
import inspect
import signal
import sys, struct, socket
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# mrtparse information
__pyname__  = 'mrtparse'
__version__ = '1.2'
__descr__   = 'parse a MRT-format data'
__url__     = 'https://github.com/YoshiyukiYamauchi/mrtparse'
__author__  = 'Tetsumune KISO, Yoshiyuki YAMAUCHI, Nobuhiro ITOU'
__email__   = 't2mune@gmail.com, info@greenhippo.co.jp, js333123@gmail.com'
__license__ = 'Apache License, Version 2.0'
__all__     = (['Reader', 'val_dict'] +
               ['AFI_T', 'SAFI_T', 'MSG_T', 'BGP_ST', 'TD_ST', 'TD_V2_ST',
                'BGP4MP_ST', 'MSG_ST', 'BGP_FSM', 'BGP_ATTR_T', 'ORIGIN_T',
                'AS_PATH_SEG_T', 'COMM_T', 'BGP_MSG_T', 'BGP_ERR_C',
                'BGP_HDR_ERR_SC', 'BGP_OPEN_ERR_SC', 'BGP_UPDATE_ERR_SC',
                'BGP_FSM_ERR_SC', 'BGP_CEASE_ERR_SC', 'BGP_OPT_PARAMS_T',
                'BGP_CAP_C', 'ORF_T', 'ORF_SEND_RECV', 'AS_REP'] +
               ['AfiT', 'SafiT', 'MsgT', 'BgpSt', 'TdSt', 'TdV2St',
                'Bgp4mpSt', 'MsgSt', 'BgpFsm', 'BgpAttrT', 'OriginT',
                'AsPathSegT', 'CommT', 'BgpMsgT', 'BgpErrC',
                'BgpHdrErrSc', 'BgpOpenErrSc', 'BgpUpdateErrSc',
                'BgpFsmErrSc', 'BgpCeaseErrSc', 'BgpOptParamsT', 'BgpCapC',
                'OrfT', 'OrfSendRecv', 'AsRep'])

# Magic Number
GZIP_MAGIC = b'\x1f\x8b'
BZ2_MAGIC  = b'\x42\x5a\x68'

# MRT header length
MRT_HDR_LEN = 12

class _FillEnum(object):

    """This Decorator returns an Enum, which contains all values in `values`.

    Values, which the passed class not include, will be auto generated with
    `prefix` + value as name if they are in the `values` list.

    Args:
        enum_cls: The Enum class or a subclass of it.
        values: An iterable list of values for the Enum members.
        prefix: The prefix for the name of the auto generated Enum members.
        *args: Will be passed to the `enum_cls` constructor.
        **kwargs: Will be passed to the `enum_cls` constructor.
    """

    def __init__(self, enum_cls, values, prefix, *args, **kwargs):
        self.enum_cls = enum_cls
        self.values = values
        self.prefix = prefix
        self.args = args
        self.kwargs = kwargs

    def __call__(self, cls):
        members = []
        cls_values = set()  # set of values present in `cls`

        # Copy members of passed class `cls`
        attributes = inspect.getmembers(cls)
        for attr in attributes:
            if attr[0].startswith('__') and attr[0].endswith('__'):
                continue
            cls_values.add(attr[1])
            members.append(attr)
            any_member = attr[0]  # Any arbitrary member of the new Enum

        # set members, which are in `values` and not already present in `cls`
        for value in self.values:
            if value in cls_values:
                continue
            members.append((self.prefix + str(value), value))
            any_member = self.prefix + str(value)

        new_enum_cls = self.enum_cls(cls.__name__, members,
                                     *self.args, **self.kwargs)

        # copy docstring
        getattr(new_enum_cls, any_member).__class__.__doc__ = cls.__doc__

        return new_enum_cls

class _BaseEnum(int, enum.Enum):
    """This class is the abstract Base for Type and Code Enums here.

    It Provides a customized __str__ and __repr__ string prints.
    It overwrites the __new__ method to allow tuple as input.

    Args:
        value: The associated value to the member. Must be a subclass of int.
        nice (optional): A for humans nice readable and short description.
    """
    __metaclass__ = ABCMeta

    def __new__(cls, value, nice=None):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.nice = nice
        return obj

    def __str__(self):
        return (str(self.value) +
                " (" + str(getattr(self, 'nice', self.name)) + ")"
                )

    def __repr__(self):
        nice_str = getattr(self, 'nice', None)
        nice_str_prepend = ""
        if nice_str is not None:
            nice_str_prepend = " (" + nice_str + ")"

        return ("<" + self.__class__.__name__ + "." + self.name +
                ": " + repr(self.value) + nice_str_prepend + ">")

# a variable to reverse the keys and values of dictionaries below
dl = []

# AFI Types
# Assigend by IANA
AFI_T = {
    1:'IPv4',
    2:'IPv6',
}
dl += [AFI_T]

@enum.unique
class AfiT(_BaseEnum):
    """AFI Types. Assigend by IANA"""
    ipv4 = 1
    ipv6 = 2


# SAFI Types
# Assigend by IANA
SAFI_T = {
    1:'UNICAST',
    2:'MULTICAST',
    128:'L3VPN_UNICAST',
    129:'L3VPN_MULTICAST',
}
dl += [SAFI_T]

@enum.unique
class SafiT(_BaseEnum):
    """SAFI Types. Assigend by IANA"""
    unicast = 1
    multicast = 2
    l3vpn_unicast = 128
    l3vpn_multicast = 129


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

@enum.unique
# The field has a length of 16bit. However we only use here 8bit for faster
# class level initialization until we need more bits.
@_FillEnum(_BaseEnum, range(2**8), prefix='val', module=__name__)
class MsgT(object):
    """MRT Message Types. Defined in RFC6396."""
    null = 0           # Deprecated in RFC6396
    start = 1          # Deprecated in RFC6396
    die = 2            # Deprecated in RFC6396
    i_am_dead = 3      # Deprecated in RFC6396
    peer_down = 4      # Deprecated in RFC6396
    bgp = 5            # Deprecated in RFC6396
    rip = 6            # Deprecated in RFC6396
    idrp = 7           # Deprecated in RFC6396
    ripng = 8          # Deprecated in RFC6396
    bgp4plus = 9       # Deprecated in RFC6396
    bgp4plus_01 = 10   # Deprecated in RFC6396
    ospfv2 = 11
    table_dump = 12
    table_dump_v2 = 13
    bgp4mp = 16
    bgp4mp_et = 17
    isis = 32
    isis_et = 33
    ospfv3 = 48
    ospfv3_et = 49


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

@enum.unique
class BgpSt(_BaseEnum):
    """BGP,BGP4PLUS,BGP4PLUS_01 Subtypes. Deprecated in RFC6396."""
    bgp_null = 0
    bgp_update = 1
    bgp_pref_update = 2
    bgp_state_change = 3
    bgp_sync = 4
    bgp_open = 5
    bgp_notify = 6
    bgp_keepalive = 7


# TABLE_DUMP Subtypes
# Defined in RFC6396
TD_ST = {
    1:'AFI_IPv4',
    2:'AFI_IPv6',
}
dl += [AFI_T]

@enum.unique
class TdSt(_BaseEnum):
    """TABLE_DUMP Subtypes. Defined in RFC6396."""
    afi_ipv4 = 1
    afi_ipv6 = 2


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

@enum.unique
class TdV2St(_BaseEnum):
    """TABLE_DUMP_V2 Subtypes. Defined in RFC6396."""
    peer_index_table = 1
    rib_ipv4_unicast = 2
    rib_ipv4_multicast = 3
    rib_ipv6_unicast = 4
    rib_ipv6_multicast = 5
    rib_generic = 6


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

@enum.unique
class Bgp4mpSt(_BaseEnum):
    """BGP4MP,BGP4MP_ET Subtypes. Defined in RFC6396."""
    bgp4mp_state_change = 0
    bgp4mp_message = 1
    bgp4mp_entry = 2             # Deprecated in RFC6396
    bgp4mp_snapshot = 3          # Deprecated in RFC6396
    bgp4mp_message_as4 = 4
    bgp4mp_state_change_as4 = 5
    bgp4mp_message_local = 6
    bgp4mp_message_as4_local = 7


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

@enum.unique
# The field has a length of 16bit. However we only use here 8bit for faster
# class level initialization until we need more bits.
@_FillEnum(_BaseEnum, range(2**8), prefix='val', module=__name__)
class MsgSt(object):
    """MRT Message Subtypes. Defined in RFC6396."""
    bgp_st9 = 9
    bgp_st10 = 10
    afi_t = 12
    td_v2_st = 13
    bgp4mp_st16 = 16
    bgp4mp_st17 = 17

MsgSt.bgp_st9.enum = BgpSt
MsgSt.bgp_st10.enum = BgpSt
MsgSt.afi_t.enum = AfiT
MsgSt.td_v2_st.enum = TdV2St
MsgSt.bgp4mp_st16.enum = Bgp4mpSt
MsgSt.bgp4mp_st17.enum = Bgp4mpSt

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

@enum.unique
class BgpFsm(_BaseEnum):
    """BGP FSM States. Defined in RFC4271."""
    idle = 1
    connect = 2
    active = 3
    opensent = 4
    openconfirm = 5
    established = 6
    clearing = 7    # Used only in quagga?
    deleted = 8     # Used only in quagga?


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
    26:'AIGP',                 # Defined in RFC7311
    128:'ATTR_SET',            # Defined in RFC6368
}
dl += [BGP_ATTR_T]

@enum.unique
class BgpAttrT(_BaseEnum):
    """BGP Attribute Types. Defined in RFC4271 and others."""
    reserved = 0
    origin = 1
    as_path = 2
    next_hop = 3
    multi_exit_disc = 4
    local_pref = 5
    atomic_aggregate = 6
    aggregator = 7
    community = 8                      # Defined in RFC1997
    originator_id = 9                  # Defined in RFC4456
    cluster_list = 10                  # Defined in RFC4456
    dpa = 11                           # Deprecated in RFC6938
    advertiser = 12                    # Deprecated in RFC6938
    rcid_path_cluster_id = 13          # Deprecated in RFC6938
    mp_reach_nlri = 14                 # Defined in RFC4760
    mp_unreach_nlri = 15               # Defined in RFC4760
    extended_communities = 16          # Defined in RFC4360
    as4_path = 17                      # Defined in RFC6793
    as4_aggregator = 18                # Defined in RFC6793
    # Deprecated in [Gargi_Nalawade][draft-kapoor-nalawade-idr-bgp-ssa-00]
    #     [draft-nalawade-idr-mdt-safi-00][draft-wijnands-mt-discovery-00]
    safi_specific_attr = (19,
        "SAFI Specific Attribute (SSA) (deprecated)")
    connector_attr = (20,              # Deprecated in RFC6037
        "Connector Attribute (deprecated)")
    as_pathlimit = (21,           # Deprecated in [draft-ietf-idr-as-pathlimit]
        "AS_PATHLIMIT (deprecated)")
    pmsi_tunnel = 22                   # Defined in RFC6514
    tunnel_encapsulation_attr = (23,   # Defined in RFC5512
        "Tunnel Encapsulation Attribute")
    traffic_engineering = 24           # Defined in RFC5543
    ipv6_addr_specific_ext_comm = (25, # Defined in RFC5701
        "IPv6 Address Specific Extended Community")
    aigp = 26                          # Defined in RFC7311
    pe_distinguisher_labels = 27       # Defined in RFC6514
    bgp_entropy_label_cap_attr = (28,  # Deprecated in RFC6790, RFC7447
        "BGP Entropy Label Capability Attribute (deprecated)")
    # Defined in [draft-ietf-idr-ls-distribution]
    # (TEMPORARY - registered 2014-03-11, expires 2016-03-11)
    bgp_ls_attr = (29,
        "BGP-LS Attribute (TEMPORARY - registered 2014-03-11, expires 2016-03-11)")
    attr_set = 128                     # Defined in RFC6368


# BGP ORIGIN Types
# Defined in RFC4271
ORIGIN_T = {
    0:'IGP',
    1:'EGP',
    2:'INCOMPLETE',
}
dl += [ORIGIN_T]

@enum.unique
class OriginT(_BaseEnum):
    """BGP ORIGIN Types. Defined in RFC4271."""
    igp = 0
    egp = 1
    incomplete = 2


# BGP AS_PATH Types
# Defined in RFC4271
AS_PATH_SEG_T = {
    1:'AS_SET',
    2:'AS_SEQUENCE',
    3:'AS_CONFED_SEQUENCE', # Defined in RFC5065
    4:'AS_CONFED_SET',      # Defined in RFC5065
}
dl += [AS_PATH_SEG_T]

@enum.unique
class AsPathSegT(_BaseEnum):
    """BGP AS_PATH Types. Defined in RFC4271."""
    as_set = 1
    as_sequence = 2
    as_confed_sequence = 3 # Defined in RFC5065
    as_confed_set = 4      # Defined in RFC5065


# Reserved BGP COMMUNITY Types
# Defined in RFC1997
COMM_T = {
    0xffffff01:'NO_EXPORT',
    0xffffff02:'NO_ADVERTISE',
    0xffffff03:'NO_EXPORT_SCONFED',
    0xffffff04:'NO_PEER',           # Defined in RFC3765
}
dl += [COMM_T]

@enum.unique
class CommT(_BaseEnum):
    """Reserved BGP COMMUNITY Types. Defined in RFC1997."""
    no_export = 0xffffff01
    no_advertise = 0xffffff02
    no_export_sconfed = 0xffffff03
    no_peer = 0xffffff04           # Defined in RFC3765

    def __str__(self):
        return hex(self.value) + " (" + self.name + ")"

    def __repr__(self):
        return ("<" + self.__class__.__name__ + "." + self.name +
                ": " + hex(self.value) + ">")


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

@enum.unique
class BgpMsgT(_BaseEnum):
    """BGP Message Types. Defined in RFC4271."""
    reserved = 0
    open = 1
    update = 2
    notification = 3
    keepalive = 4
    route_refresh = 5 # Defined in RFC2918


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

@enum.unique
class BgpErrC(_BaseEnum):
    """BGP Error Codes. Defined in RFC4271."""
    reserved = (0,
        "Reserved")
    msg_header_err = (1,
        "Message Header Error")
    open_msg_err = (2,
        "OPEN Message Error")
    update_msg_err = (3,
        "UPDATE Message Error")
    hold_timer_expired = (4,
        "Hold Timer Expired")
    finite_state_machine_err = (5,
        "Finite State Machine Error")
    cease = (6,
        "Cease")


# BGP Message Header Error Subcodes
# Defined in RFC4271
BGP_HDR_ERR_SC = {
    0:'Reserved',
    1:'Connection Not Synchronized',
    2:'Bad Message Length',
    3:'Bad Message Type',
}
dl += [BGP_HDR_ERR_SC]

@enum.unique
class BgpHdrErrSc(_BaseEnum):
    """BGP Message Header Error Subcodes. Defined in RFC4271."""
    reserved = 0
    connection_not_sync = 1
    bad_msg_length = 2
    bad_msg_type = 3

BgpHdrErrSc.reserved.nice = "Reserved"
BgpHdrErrSc.connection_not_sync.nice = "Connection Not Synchronized"
BgpHdrErrSc.bad_msg_length.nice = "Bad Message Length"
BgpHdrErrSc.bad_msg_type.nice = "Bad Message Type"

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

@enum.unique
class BgpOpenErrSc(_BaseEnum):
    """OPEN Message Error Subcodes. Defined in RFC4271."""
    reserved = (0,
        "Reserved")
    unsupported_vers_numb = (1,
        "Unsupported Version Number")
    bad_peer_as = (2,
        "Bad Peer AS")
    bad_bgp_id = (3,
        "Bad BGP Identifier")
    unsupported_opt_parameter = (4,
        "Unsupported Optional Parameter")
    deprecated = (5,
        "[Deprecated]")
    unacceptable_hold_time = (6,
        "Unacceptable Hold Time")
    unsupported_capability = (7,       # Defined in RFC5492
        "Unsupported Capability")


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

@enum.unique
class BgpUpdateErrSc(_BaseEnum):
    """UPDATE Message Error Subcodes. Defined in RFC4271."""
    reserved = (0,
        "Reserved")
    malformed_attr_list = (1,
        "Malformed Attribute List")
    unrecognized_well_known_attr = (2,
        "Unrecognized Well-known Attribute")
    missing_well_known_attr = (3,
        "Missing Well-known Attribute")
    attr_flags_err = (4,
        "Attribute Flags Error")
    attr_length_err = (5,
        "Attribute Length Error")
    invalid_origin_attr = (6,
        "Invalid ORIGIN Attribute")
    deprecated = (7,
        "[Deprecated]")
    invalid_next_hop_attr = (8,
        "Invalid NEXT_HOP Attribute")
    optional_attr_err = (9,
        "Optional Attribute Error")
    invalid_network_field = (10,
        "Invalid Network Field")
    malformed_as_path = (11,
        "Malformed AS_PATH")


# BGP Finite State Machine Error Subcodes
# Defined in RFC6608
BGP_FSM_ERR_SC = {
    0:'Unspecified Error',
    1:'Receive Unexpected Message in OpenSent State',
    2:'Receive Unexpected Message in OpenConfirm State',
    3:'Receive Unexpected Message in Established State',
}
dl += [BGP_FSM_ERR_SC]

@enum.unique
class BgpFsmErrSc(_BaseEnum):
    """BGP Finite State Machine Error Subcodes. Defined in RFC6608."""
    unspecified_err = (0,
        "Unspecified Error")
    rcv_unexp_msg_in_opensent = (1,
        "Receive Unexpected Message in OpenSent State")
    rcv_unexp_msg_in_openconfirm = (2,
        "Receive Unexpected Message in OpenConfirm State")
    rcv_unexp_msg_in_established = (3,
        "Receive Unexpected Message in Established State")


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

@enum.unique
class BgpCeaseErrSc(_BaseEnum):
    """BGP Cease NOTIFICATION Message Subcodes. Defined in RFC4486."""
    reserved = (0,
        "Reserved")
    max_numb_of_prefixes_reached = (1,
        "Maximum Number of Prefixes Reached")
    administrative_shutdown = (2,
        "Administrative Shutdown")
    peer_de_configured = (3,
        "Peer De-configured")
    administrative_reset = (4,
        "Administrative Reset")
    connection_rejected = (5,
        "Connection Rejected")
    other_configuration_change = (6,
        "Other Configuration Change")
    connection_collision_resolution = (7,
        "Connection Collision Resolution")
    out_of_resources = (8,
        "Out of Resources")


# BGP Error Subcodes
BGP_ERR_SC = {
    1:BGP_HDR_ERR_SC,
    2:BGP_UPDATE_ERR_SC,
    3:BGP_OPEN_ERR_SC,
    4:BGP_UPDATE_ERR_SC,
    5:BGP_FSM_ERR_SC,
    6:BGP_CEASE_ERR_SC,
}

class BgpErrSc(_BaseEnum):
    """BGP Error Subcodes."""
    bgp_hdr_err_sc = 1
    bgp_update_err_sc2 = 2
    bgp_open_err_sc = 3
    bgp_update_err_sc4 = 4
    bgp_fsm_err_sc = 5
    bgp_cease_err_sc = 6

BgpErrSc.bgp_hdr_err_sc.enum = BgpHdrErrSc
BgpErrSc.bgp_update_err_sc2.enum = BgpUpdateErrSc
BgpErrSc.bgp_open_err_sc.enum = BgpOpenErrSc
BgpErrSc.bgp_update_err_sc4.enum = BgpUpdateErrSc
BgpErrSc.bgp_fsm_err_sc.enum = BgpFsmErrSc
BgpErrSc.bgp_cease_err_sc.enum = BgpCeaseErrSc


# BGP OPEN Optional Parameter Types
# Defined in RFC5492
BGP_OPT_PARAMS_T = {
    0:'Reserved',
    1:'Authentication', # Deprecated
    2:'Capabilities',
}
dl += [BGP_OPT_PARAMS_T]

@enum.unique
class BgpOptParamsT(_BaseEnum):
    """BGP OPEN Optional Parameter Types. Defined in RFC5492."""
    reserved = 0
    authentication = 1 # Deprecated
    capabilities = 2


# Capability Codes
# Defined in RFC5492
BGP_CAP_C = {
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
dl += [BGP_CAP_C]

@enum.unique
class BgpCapC(_BaseEnum):
    """Capability Codes. Defined in RFC5492."""
    reserved = (0,
        "Reserved")
    multiproto_extensions_bgp_4 = (1,      # Defined in RFC2858
        "Multiprotocol Extensions for BGP-4")
    route_refresh_cap_bgp_4 = (2,          # Defined in RFC2918
        "Route Refresh Capability for BGP-4")
    outbound_route_filtering_cap = (3,     # Defined in RFC5291
        "Outbound Route Filtering Capability")
    multiple_routes_to_a_dest_cap = (4,    # Defined in RFC3107
        "Multiple routes to a destination capability")
    extended_next_hop_encoding = (5,       # Defined in RFC5549
        "Extended Next Hop Encoding")
    graceful_restart_cap = (64,            # Defined in RFC4724
        "Graceful Restart Capability")
    support_4_octet_as_numb_cap = (65,     # Defined in RFC6793
        "Support for 4-octet AS number capability")
    deprecated = (66,
        "[Deprecated]")
    support_for_dynamic_cap = (67,         # draft-ietf-idr-dynamic-cap
        "Support for Dynamic Capability (capability specific)")
    multisession_bgp_cap = (68,            # draft-ietf-idr-bgp-multisession
        "Multisession BGP Capability")
    add_path_cap = (69,                    # draft-ietf-idr-add-paths
        "ADD-PATH Capability")
    enhanced_route_refresh_cap = (70,      # draft-keyur-bgp-enhanced-route-refresh
        "Enhanced Route Refresh Capability")
    long_lived_graceful_restart_cap = (71, # draft-uttaro-idr-bgp-persistence
        "Long-Lived Graceful Restart (LLGR) Capability")


# Outbound Route Filtering Capability
# Defined in RFC5291
ORF_T = {
    64:'Address Prefix ORF', # Defined in RFC5292
}
dl += [ORF_T]

@enum.unique
class OrfT(_BaseEnum):
    """Outbound Route Filtering Capability. Defined in RFC5291."""
    address_prefix_orf = (64, # Defined in RFC5292
        "Address Prefix ORF")


ORF_SEND_RECV = {
    1:'Receive',
    2:'Send',
    3:'Both',
}
dl += [ORF_SEND_RECV]

@enum.unique
class OrfSendRecv(_BaseEnum):
    receive = 1
    send = 2
    both = 3


# AS Number Representation
AS_REP = {
    1:'asplain',
    2:'asdot+',
    3:'asdot',
}
dl += [AS_REP]

@enum.unique
class AsRep(_BaseEnum):
    """AS Number Representation."""
    asplain = 1
    asdot_plus = 2
    asdot = 3

# reverse the keys and values of dictionaries above
for d in dl:
    for k in list(d.keys()):
        d[d[k]] = k

# a function to get a value by specified keys from dictionaries above
def val_dict(d, *args):
    k = args[0]
    if k in d:
        if isinstance(d[k], dict) and len(args) > 1:
            return val_dict(d[k], *args[1:])
        return d[k]
    return 'Unknown'

# MPLS Label
LBL_BOTTOM    = 0x01     # Defined in RFC3032
LBL_WITHDRAWN = 0x800000 # Defined in RFC3107

# AS number length for AS_PATH attribute
as_len = 4

# AS Number Notation
# Default notation is 'asplain'(Defined in RFC5396)
as_rep = AS_REP['asplain']
as_rep = AsRep.asplain

# super class for all other classes
class Base:
    def __init__(self):
        self.p = 0

    def val_num(self, buf, n):
        if n <= 0 or len(buf) - self.p < n:
            return None

        val = 0
        for i in buf[self.p:self.p+n]:
            val <<= 8
            # for python3
            if isinstance(i, int):
                val += i
            # for python2
            else:
                val += struct.unpack('>B', i)[0]
        self.p += n

        return val

    def val_str(self, buf, n):
        if n <= 0 or len(buf) - self.p < n:
            return None

        val = buf[self.p:self.p+n]
        self.p += n

        return val

    def val_addr(self, buf, af, *args):
        if af == AfiT.ipv4:
            m = 4
            _af = socket.AF_INET
        elif af == AfiT.ipv6:
            m = 16
            _af = socket.AF_INET6
        else:
            n = -1

        n = m if len(args) == 0 else (args[0] + 7) // 8

        if n < 0 or len(buf) - self.p < n:
            return None

        addr = socket.inet_ntop(
            _af, buf[self.p:self.p+n] + b'\x00'*(m - n))
        self.p += n

        return addr

    def val_asn(self, buf, n):
        global as_rep
        asn = self.val_num(buf, n)

        if  (as_rep == AsRep.asdot_plus or
            (as_rep == AsRep.asdot and asn > 0xffff)):
            asn = str(asn >> 16) + '.' + str(asn & 0xffff)
        else:
            asn = str(asn)

        return asn

    def val_rd(self, buf):
        rd = self.val_num(buf, 8)
        rd = str(rd >> 32) + ':' + str(rd & 0xffffffff)

        return rd

class Reader(Base):
    def __init__(self, arg):
        Base.__init__(self)
        self.as_rep = as_rep

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
            sys.stderr.write("error: unsupported instance type\n")

    def close(self):
        self.f.close()
        raise StopIteration

    def __iter__(self):
        global as_rep
        as_rep = self.as_rep
        return self

    def __next__(self):
        global as_len
        as_len = 4
        self.mrt = Mrt()
        self.unpack()
        return self

    # for python2 compatibility
    next = __next__

    def unpack(self):
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

        self.buf = hdr + data

        if (   self.mrt.type == MsgT.bgp4mp_et
            or self.mrt.type == MsgT.isis_et
            or self.mrt.type == MsgT.ospfv3_et):
            self.mrt.micro_ts = self.val_num(data, 4)

        if self.mrt.type == MsgT.table_dump:
            self.mrt.td = TableDump()
            self.mrt.td.unpack(data, self.mrt.subtype)
        elif self.mrt.type == MsgT.table_dump_v2:
            self.unpack_td_v2(data)
        elif ( self.mrt.type == MsgT.bgp4mp
            or self.mrt.type == MsgT.bgp4mp_et):
            self.mrt.bgp = Bgp4Mp()
            self.mrt.bgp.unpack(data, self.mrt.subtype)
        elif ( self.mrt.type == MsgT.isis_et
            or self.mrt.type == MsgT.ospfv3_et):
            self.p += self.len - 4
        else:
            self.p += self.len
        return self.p

    def unpack_td_v2(self, data):
        if self.mrt.subtype == TdV2St.peer_index_table:
            self.mrt.peer = PeerIndexTable()
            self.mrt.peer.unpack(data)
        elif ( self.mrt.subtype == TdV2St.rib_ipv4_unicast
            or self.mrt.subtype == TdV2St.rib_ipv4_multicast):
            self.mrt.rib = AfiSpecRib()
            self.mrt.rib.unpack(data, AfiT.ipv4)
        elif ( self.mrt.subtype == TdV2St.rib_ipv6_unicast
            or self.mrt.subtype == TdV2St.rib_ipv6_multicast):
            self.mrt.rib = AfiSpecRib()
            self.mrt.rib.unpack(data, AfiT.ipv6)
        else:
            self.p += self.len

class Mrt(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        self.ts = self.val_num(buf, 4)
        self.type = MsgT(self.val_num(buf, 2))
        self.subtype = MsgSt(self.val_num(buf, 2))
        self.len = self.val_num(buf, 4)
        return self.p

class TableDump(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf, subtype):
        global as_len
        as_len = 2
        self.view = self.val_num(buf, 2)
        self.seq = self.val_num(buf, 2)
        self.prefix = self.val_addr(buf, subtype)
        self.plen = self.val_num(buf, 1)
        self.status = self.val_num(buf, 1)
        self.org_time = self.val_num(buf, 4)
        self.peer_ip = self.val_addr(buf, subtype)
        self.peer_as = self.val_asn(buf, as_len)
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
        self.collector = self.val_addr(buf, AfiT.ipv4)
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
        self.type = self.val_num(buf, 1)
        self.bgp_id = self.val_addr(buf, AfiT.ipv4)
        if self.type & 0x01:
            af = AfiT.ipv6
        else:
            af = AfiT.ipv4
        self.ip = self.val_addr(buf, af)
        n = 4 if self.type & (0x01 << 1) else 2
        self.asn = self.val_asn(buf, n)
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
        if (   subtype == Bgp4mpSt.bgp4mp_state_change
            or subtype == Bgp4mpSt.bgp4mp_message
            or subtype == Bgp4mpSt.bgp4mp_message_local):
            as_len = 2
        elif ( subtype == Bgp4mpSt.bgp4mp_message_as4
            or subtype == Bgp4mpSt.bgp4mp_state_change_as4
            or subtype == Bgp4mpSt.bgp4mp_message_as4_local):
            as_len = 4

        self.peer_as = self.val_asn(buf, as_len)
        self.local_as = self.val_asn(buf, as_len)
        self.ifindex = self.val_num(buf, 2)
        self.af = AfiT(self.val_num(buf, 2))
        self.peer_ip = self.val_addr(buf, self.af)
        self.local_ip = self.val_addr(buf, self.af)

        if (   subtype == Bgp4mpSt.bgp4mp_state_change
            or subtype == Bgp4mpSt.bgp4mp_state_change_as4):
            self.old_state = BgpFsm(self.val_num(buf, 2))
            self.new_state = BgpFsm(self.val_num(buf, 2))
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
        self.type = BgpMsgT(self.val_num(buf, 1))

        if self.type == BgpMsgT.open:
            self.unpack_open(buf, af)
        elif self.type == BgpMsgT.update:
            self.unpack_update(buf, af)
        elif self.type == BgpMsgT.notification:
            self.unpack_notification(buf)
        elif self.type == BgpMsgT.route_refresh:
            self.unpack_route_refresh(buf)

        self.p += self.len - self.p
        return self.p

    def unpack_open(self, buf, af):
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

    def unpack_update(self, buf, af):
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

        self.nlri = []
        while self.p < self.len:
            nlri = Nlri()
            self.p += nlri.unpack(buf[self.p:], af)
            self.nlri.append(nlri)

    def unpack_notification(self, buf):
        self.err_code = BgpErrC(self.val_num(buf, 1))
        self.err_subcode = BgpErrSc(self.val_num(buf, 1))
        self.data = self.val_str(buf, self.len - self.p)

    def unpack_route_refresh(self, buf):
        self.afi = AfiT(self.val_num(buf, 2))
        self.rsvd = self.val_num(buf, 1)
        self.safi = SafiT(self.val_num(buf, 1))

class OptParams(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        self.type = BgpOptParamsT(self.val_num(buf, 1))
        self.len = self.val_num(buf, 1)
        if self.type == BgpOptParamsT.capabilities:
            self.unpack_capabilities(buf)
        else:
            self.p += self.len
        return self.p

    def unpack_capabilities(self, buf):
        self.cap_type = BgpCapC(self.val_num(buf, 1))
        self.cap_len = self.val_num(buf, 1)

        if self.cap_type == BgpCapC.multiproto_extensions_bgp_4:
            self.unpack_multi_ext(buf)
        elif self.cap_type == BgpCapC.route_refresh_cap_bgp_4:
            self.p += self.len - 2
        elif self.cap_type == BgpCapC.outbound_route_filtering_cap:
            self.unpack_orf(buf)
        elif self.cap_type == BgpCapC.graceful_restart_cap:
            self.unpack_graceful_restart(buf)
        elif self.cap_type == BgpCapC.support_4_octet_as_numb_cap:
            self.unpack_support_as4(buf)
        else:
            self.p += self.len - 2

    def unpack_multi_ext(self, buf):
        self.multi_ext = {}
        self.multi_ext['afi'] = AfiT(self.val_num(buf, 2))
        self.multi_ext['rsvd'] = self.val_num(buf, 1)
        self.multi_ext['safi'] = SafiT(self.val_num(buf, 1))

    def unpack_orf(self, buf):
        self.orf = {}
        self.orf['afi'] = AfiT(self.val_num(buf, 2))
        self.orf['rsvd'] = self.val_num(buf, 1)
        self.orf['safi'] = SafiT(self.val_num(buf, 1))
        self.orf['number'] = self.val_num(buf, 1)
        self.orf['entry'] = []
        for i in range(self.orf['number']):
            entry = {}
            entry['type'] = self.val_num(buf, 1)
            entry['send_recv'] = OrfSendRecv(self.val_num(buf, 1))
            self.orf['entry'].append(entry)

    def unpack_graceful_restart(self, buf):
        self.graceful_restart = {}
        n = self.val_num(buf, 2)
        self.graceful_restart['flag'] = n & 0xf000
        self.graceful_restart['sec'] = n & 0x0fff
        self.graceful_restart['entry'] = []
        cap_len = self.cap_len
        while cap_len > 2:
            entry = {}
            entry['afi'] = AfiT(self.val_num(buf, 2))
            entry['safi'] = SafiT(self.val_num(buf, 1))
            entry['flag'] = self.val_num(buf, 1)
            self.graceful_restart['entry'].append(entry)
            cap_len -= 4

    def unpack_support_as4(self, buf):
        self.support_as4 = self.val_asn(buf, 4)

class BgpAttr(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf):
        self.flag = self.val_num(buf, 1)
        self.type = BgpAttrT(self.val_num(buf, 1))

        if self.flag & 0x01 << 4:
            self.len = self.val_num(buf, 2)
        else:
            self.len = self.val_num(buf, 1)

        if self.type == BgpAttrT.origin:
            self.unpack_origin(buf)
        elif self.type == BgpAttrT.as_path:
            self.unpack_as_path(buf)
        elif self.type == BgpAttrT.next_hop:
            self.unpack_next_hop(buf)
        elif self.type == BgpAttrT.multi_exit_disc:
            self.unpack_multi_exit_disc(buf)
        elif self.type == BgpAttrT.local_pref:
            self.unpack_local_pref(buf)
        elif self.type == BgpAttrT.aggregator:
            self.unpack_aggregator(buf)
        elif self.type == BgpAttrT.community:
            self.unpack_community(buf)
        elif self.type == BgpAttrT.originator_id:
            self.unpack_originator_id(buf)
        elif self.type == BgpAttrT.cluster_list:
            self.unpack_cluster_list(buf)
        elif self.type == BgpAttrT.mp_reach_nlri:
            self.unpack_mp_reach_nlri(buf)
        elif self.type == BgpAttrT.mp_unreach_nlri:
            self.unpack_mp_unreach_nlri(buf)
        elif self.type == BgpAttrT.extended_communities:
            self.unpack_extended_communities(buf)
        elif self.type == BgpAttrT.as4_path:
            self.unpack_as4_path(buf)
        elif self.type == BgpAttrT.as4_aggregator:
            self.unpack_as4_aggregator(buf)
        elif self.type == BgpAttrT.aigp:
            self.unpack_aigp(buf)
        elif self.type == BgpAttrT.attr_set:
            self.unpack_attr_set(buf)
        else:
            self.val = self.val_str(buf, self.len)
        return self.p

    def unpack_origin(self, buf):
        self.origin = OriginT(self.val_num(buf, 1))

    def unpack_as_path(self, buf):
        global as_len
        attr_len = self.p + self.len
        self.as_path = []
        while self.p < attr_len:
            l = []
            path_seg = {}
            path_seg['type'] = AsPathSegT(self.val_num(buf, 1))
            path_seg['len'] = self.val_num(buf, 1)
            for i in range(path_seg['len']):
                l.append(self.val_asn(buf, as_len))
            path_seg['val'] = ' '.join(l)
            self.as_path.append(path_seg)

    def unpack_next_hop(self, buf):
        if self.len == 4:
            self.next_hop = self.val_addr(buf, AfiT.ipv4)
        elif self.len == 16:
            self.next_hop = self.val_addr(buf, AfiT.ipv6)
        else:
            self.p += self.len
            self.next_hop = None

    def unpack_multi_exit_disc(self, buf):
        self.med = self.val_num(buf, 4)

    def unpack_local_pref(self, buf):
        self.local_pref = self.val_num(buf, 4)

    def unpack_aggregator(self, buf):
        self.aggr = {}
        n = 2 if self.len < 8 else 4
        self.aggr['asn'] = self.val_asn(buf, n)
        self.aggr['id'] = self.val_addr(buf, AfiT.ipv4)

    def unpack_community(self, buf):
        attr_len = self.p + self.len
        self.comm = []
        while self.p < attr_len:
            val = self.val_num(buf, 4)
            self.comm.append('%d:%d' % 
                ((val & 0xffff0000) >> 16, val & 0x0000ffff))

    def unpack_originator_id(self, buf):
        self.org_id= self.val_addr(buf, AfiT.ipv4)

    def unpack_cluster_list(self, buf):
        attr_len = self.p + self.len
        self.cl_list = []
        while self.p < attr_len:
            self.cl_list.append(self.val_addr(buf, AfiT.ipv4))

    def unpack_mp_reach_nlri(self, buf):
        attr_len = self.p + self.len
        self.mp_reach = {}
        self.mp_reach['afi'] = AfiT(self.val_num(buf, 2))
        self.mp_reach['safi'] = SafiT(self.val_num(buf, 1))
        self.mp_reach['nlen'] = nlen = self.val_num(buf, 1)

        if (    self.mp_reach['afi'] != AfiT.ipv4
            and self.mp_reach['afi'] != AfiT.ipv6):
            self.p = attr_len
            return

        if (    self.mp_reach['safi'] != SafiT.unicast
            and self.mp_reach['safi'] != SafiT.multicast
            and self.mp_reach['safi'] != SafiT.l3vpn_unicast
            and self.mp_reach['safi'] != SafiT.l3vpn_multicast):
            self.p = attr_len
            return

        if (   self.mp_reach['safi'] == SafiT.l3vpn_unicast
            or self.mp_reach['safi'] == SafiT.l3vpn_multicast):
            self.mp_reach['rd'] = self.val_rd(buf)

        self.mp_reach['next_hop'] = []
        self.mp_reach['next_hop'].append(
            self.val_addr(buf, self.mp_reach['afi']))
        if (nlen == 32 and self.mp_reach['afi'] == AfiT.ipv6):
            self.mp_reach['next_hop'].append(
                self.val_addr(buf, self.mp_reach['afi']))

        self.mp_reach['rsvd'] = self.val_num(buf, 1)

        self.mp_reach['nlri'] = []
        while self.p < attr_len:
            nlri = Nlri()
            self.p += nlri.unpack(
                buf[self.p:], self.mp_reach['afi'], self.mp_reach['safi'])
            self.mp_reach['nlri'].append(nlri)

    def unpack_mp_unreach_nlri(self, buf):
        attr_len = self.p + self.len
        self.mp_unreach = {}
        self.mp_unreach['afi'] = AfiT(self.val_num(buf, 2))
        self.mp_unreach['safi'] = SafiT(self.val_num(buf, 1))

        if (    self.mp_unreach['afi'] != AfiT.ipv4
            and self.mp_unreach['afi'] != AfiT.ipv6):
            self.p = attr_len
            return

        if (    self.mp_unreach['safi'] != SafiT.unicast
            and self.mp_unreach['safi'] != SafiT.multicast
            and self.mp_unreach['safi'] != SafiT.l3vpn_unicast
            and self.mp_unreach['safi'] != SafiT.l3vpn_multicast):
            self.p = attr_len
            return

        self.mp_unreach['withdrawn'] = []
        while self.p < attr_len:
            withdrawn = Nlri()
            self.p += withdrawn.unpack(
                buf[self.p:], self.mp_unreach['afi'], self.mp_unreach['safi'])
            self.mp_unreach['withdrawn'].append(withdrawn)

    def unpack_extended_communities(self, buf):
        attr_len = self.p + self.len
        self.ext_comm = []
        while self.p < attr_len:
            ext_comm = self.val_num(buf, 8)
            self.ext_comm.append(ext_comm)

    def unpack_as4_path(self, buf):
        attr_len = self.p + self.len
        self.as4_path = []
        while self.p < attr_len:
            l = []
            path_seg = {}
            path_seg['type'] = AsPathSegT(self.val_num(buf, 1))
            path_seg['len'] = self.val_num(buf, 1)
            for i in range(path_seg['len']):
                l.append(self.val_asn(buf, 4))
            path_seg['val'] = ' '.join(l)
            self.as4_path.append(path_seg)

    def unpack_as4_aggregator(self, buf):
        self.as4_aggr = {}
        self.as4_aggr['asn'] = self.val_asn(buf, 4)
        self.as4_aggr['id'] = self.val_addr(buf, AfiT.ipv4)

    def unpack_aigp(self,buf):
        attr_len = self.p + self.len
        self.aigp = []
        while self.p < attr_len:
            aigp = {}
            aigp['type'] = self.val_num(buf, 1)
            aigp['len'] = self.val_num(buf, 2)
            aigp['val'] = self.val_num(buf, aigp['len'] - 3)
            self.aigp.append(aigp)

    def unpack_attr_set(self, buf):
        attr_len = self.p + self.len
        self.attr_set = {}
        self.attr_set['origin_as'] = self.val_asn(buf, 4)
        attr_len -= 4
        self.attr_set['attr'] = []
        while self.p < attr_len:
            attr = BgpAttr()
            self.p += attr.unpack(buf[self.p:])
            self.attr_set['attr'].append(attr)

class Nlri(Base):
    def __init__(self):
        Base.__init__(self)

    def unpack(self, buf, *args):
        af = args[0]
        saf = args[1] if len(args) > 1 else 0

        self.plen = plen = self.val_num(buf, 1)
        if (   saf == SafiT.l3vpn_unicast
            or saf == SafiT.l3vpn_multicast):
            plen = self.unpack_l3vpn(buf, plen)

        self.prefix = self.val_addr(buf, af, plen)
        return self.p

    def unpack_l3vpn(self, buf, plen):
        self.label = []
        while True:
            label= self.val_num(buf, 3)
            self.label.append(label)
            if (   label &  LBL_BOTTOM
                or label == LBL_WITHDRAWN):
                break
        self.rd = self.val_rd(buf)
        plen -= (3 * len(self.label) + 8) * 8
        return plen
