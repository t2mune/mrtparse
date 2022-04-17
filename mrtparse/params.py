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

import collections

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
    7:'GEO_PEER_TABLE',              # Defined in RFC6397
    8:'RIB_IPV4_UNICAST_ADDPATH',    # Defined in RFC8050
    9:'RIB_IPV4_MULTICAST_ADDPATH',  # Defined in RFC8050
    10:'RIB_IPV6_UNICAST_ADDPATH',   # Defined in RFC8050
    11:'RIB_IPV6_MULTICAST_ADDPATH', # Defined in RFC8050
    12:'RIB_GENERIC_ADDPATH',        # Defined in RFC8050
})

# BGP4MP,BGP4MP_ET Subtypes
# Defined in RFC6396
BGP4MP_ST = reverse_defaultdict({
    0:'BGP4MP_STATE_CHANGE',
    1:'BGP4MP_MESSAGE',
    2:'BGP4MP_ENTRY',                      # Deprecated in RFC6396
    3:'BGP4MP_SNAPSHOT',                   # Deprecated in RFC6396
    4:'BGP4MP_MESSAGE_AS4',
    5:'BGP4MP_STATE_CHANGE_AS4',
    6:'BGP4MP_MESSAGE_LOCAL',
    7:'BGP4MP_MESSAGE_AS4_LOCAL',
    8:'BGP4MP_MESSAGE_ADDPATH',            # Defined in RFC8050
    9:'BGP4MP_MESSAGE_AS4_ADDPATH',        # Defined in RFC8050
    10:'BGP4MP_MESSAGE_LOCAL_ADDPATH',     # Defined in RFC8050
    11:'BGP4MP_MESSAGE_AS4_LOCAL_ADDPATH', # Defined in RFC8050
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
    8:'COMMUNITY',                # Defined in RFC1997
    9:'ORIGINATOR_ID',            # Defined in RFC4456
    10:'CLUSTER_LIST',            # Defined in RFC4456
    11:'DPA',                     # Deprecated in RFC6938
    12:'ADVERTISER',              # Defined in RFC1863 / Deprecated in RFC6938
    13:'RCID_PATH/CLUSTER_ID',    # Defined in RFC1863 / Deprecated in RFC6938
    14:'MP_REACH_NLRI',           # Defined in RFC4760
    15:'MP_UNREACH_NLRI',         # Defined in RFC4760
    16:'EXTENDED COMMUNITIES',    # Defined in RFC4360
    17:'AS4_PATH',                # Defined in RFC6793
    18:'AS4_AGGREGATOR',          # Defined in RFC6793
    # Proposed in draft-kapoor-nalawade-idr-bgp-ssa / Deprecated 
    19:'SAFI Specific Attribute',
    20:'Connector Attribute',     # Defined in RFC6037 / Deprecated
    # Proposed in draft-ietf-idr-as-pathlimit / Deprecated
    21:'AS_PATHLIMIT',
    22:'PMSI_TUNNEL',             # Defined in RFC6514
    # Defined in RFC5512
    23:'Tunnel Encapsulation Attribute',
    24:'Traffic Engineering',     # Defined in RFC5543
    # Defined in RFC5701
    25:'IPv6 Address Specific Extended Community',
    26:'AIGP',                    # Defined in RFC7311
    27:'PE Distinguisher Labels', # Defined in RFC6514
    # Defined in RFC6790 / Deprecated in RFC7447
    28:'BGP Entropy Label Capability Attribute',
    29:'BGP-LS Attribute',        # Defined in RFC7752
    32:'LARGE_COMMUNITY',         # Defined in RFC8092
    33:'BGPsec_Path',             # Defined in RFC8205
    # Proposed in draft-ietf-idr-wide-bgp-communities
    34:'BGP Community Container Attribute',
    # Proposed in draft-ietf-idr-bgp-open-policy
    35:'Only to Customer',
    # Proposed in draft-ietf-bess-evpn-ipvpn-interworking
    36:'BGP Domain Path',
    40:'BGP Prefix-SID',          # Defined in RFC8669
    128:'ATTR_SET',               # Defined in RFC6368
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
    0xffff0000:'GRACEFUL_SHUTDOWN',          # Defined in RFC8326
    0xffff0001:'ACCEPT_OWN',                 # Defined in RFC7611
    0xffff0002:'ROUTE_FILTER_TRANSLATED_v4', # Proposed in draft-l3vpn-legacy-rtc
    0xffff0003:'ROUTE_FILTER_v4',            # Proposed in draft-l3vpn-legacy-rtc
    0xffff0004:'ROUTE_FILTER_TRANSLATED_v6', # Proposed in draft-l3vpn-legacy-rtc
    0xffff0005:'ROUTE_FILTER_v6',            # Proposed in draft-l3vpn-legacy-rtc
    0xffff0006:'LLGR_STALE',                 # Proposed in draft-uttaro-idr-bgp-persistence
    0xffff0007:'NO_LLGR',                    # Proposed in draft-uttaro-idr-bgp-persistence
    0xffff0008:'accept-own-nexthop',         # Proposed in draft-agrewal-idr-accept-own-nexthop
    0xffff0009:'Standby PE',                 # Defined in RFC9026
    0xffff029a:'BLACKHOLE',                  # Defined in RFC7999
    0xffffff01:'NO_EXPORT',
    0xffffff02:'NO_ADVERTISE',
    0xffffff03:'NO_EXPORT_SCONFED',
    0xffffff04:'NO_PEER',                    # Defined in RFC3765
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
    # Proposed in draft-ietf-idr-bgp-open-policy
    8:'Role Mismatch',
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
    2:'Administrative Shutdown',            # Updated in RFC8203
    3:'Peer De-configured',
    4:'Administrative Reset',               # Updated in RFC8203
    5:'Connection Rejected',
    6:'Other Configuration Change',
    7:'Connection Collision Resolution',
    8:'Out of Resources',
    9:'Hard Reset',                         # Defined in RFC8538
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
BGP_OPT_PARAMS_T = reverse_defaultdict({
    1:'Authentication', # Deprecated in RFC4271 / RFC5492
    2:'Capabilities',   # Defined in RFC5492
})

# Capability Codes
# Defined in RFC5492
BGP_CAP_C = reverse_defaultdict({
    1:'Multiprotocol Extensions for BGP-4',          # Defined in RFC2858
    2:'Route Refresh Capability for BGP-4',          # Defined in RFC2918
    3:'Outbound Route Filtering Capability',         # Defined in RFC5291
    4:'Multiple routes to a destination capability', # Deprecated in RFC8277
    5:'Extended Next Hop Encoding',                  # Defined in RFC5549
    6:'BGP Extended Message',                        # Defined in RFC8654
    7:'BGPsec Capability',                           # Defined in RFC8205
    8:'Multiple Labels Capability',                  # Defined in RFC8277
    # Proposed in draft-ietf-idr-bgp-open-policy
    9:'BGP Role',
    64:'Graceful Restart Capability',                # Defined in RFC4724
    65:'Support for 4-octet AS number capability',   # Defined in RFC6793
    66:'[Deprecated]',
    # Proposed in draft-ietf-idr-dynamic-cap
    67:'Support for Dynamic Capability',
    # Proposed in draft-ietf-idr-bgp-multisession
    68:'Multisession BGP Capability',
    # Defined in RFC7911
    69:'ADD-PATH Capability',
    # Defined in RFC7313
    70:'Enhanced Route Refresh Capability',
    # Proposed in draft-uttaro-idr-bgp-persistence
    71:'Long-Lived Graceful Restart (LLGR) Capability',
    # Proposed in draft-walton-bgp-hostname-capability
    73:'FQDN Capability',
})

# Outbound Route Filtering Capability
# Defined in RFC5291
ORF_T = reverse_defaultdict({
    64:'Address Prefix ORF', # Defined in RFC5292
    65: 'CP-ORF',            # Defined in RFC7543
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
