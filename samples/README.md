##Sample MRT format Data
###
|File Name|Type|Subtype|Description|
|:--|:--|:--|:--|
|bird6_bgp|BGP4MP|BGP4MP_MESSAGE<br>BGP4MP_MESSAGE_AS4<br>BGP4MP_STATE_CHANGE_AS4|IPv6 Peer<br>IPv6 Prefix<br>All BGP Message Types<br>ADD-PATH Capability|
|bird_bgp|BGP4MP|BGP4MP_MESSAGE<br>BGP4MP_MESSAGE_AS4<br>BGP4MP_STATE_CHANGE_AS4|IPv4 Peer<br>IPv4 Prefix<br>All BGP Message Types<br>ADD-PATH Capability|
|openbgpd_bgp|BGP4MP|BGP4MP_MESSAGE<br>BGP4MP_MESSAGE_AS4<br>BGP4MP_STATE_CHANGE<br>BGP4MP_STATE_CHANGE_AS4|IPv4/IPv6 Peer<br>IPv4/IPv6/VPNv4 Prefix<br>All BGP Message Types|
|openbgpd_rib_table|TABLE_DUMP|AFI_IPv4<br>AFI_IPv6|IPv4/IPv6 Peer<br>IPv4/IPv6 Prefix|
|openbgpd_rib_table-mp|BGP4MP|BGP4MP_ENTRY|Unsupported Subtype|
|openbgpd_rib_table-v2|TABLE_DUMP_V2|PEER_INDEX_TABLE<br>RIB_IPV4_UNICAST<br>RIB_IPV6_UNICAST<br>RIB_GENERIC|IPv4/IPv6 Peer<br>IPv4/IPv6/VPNv4 Prefix|
|quagga_bgp|BGP4MP|BGP4MP_MESSAGE<br>BGP4MP_MESSAGE_AS4<br>BGP4MP_STATE_CHANGE_AS4|IPv4/IPv6 Peer<br>IPv4/IPv6/VPNv4 Prefix<br>All BGP Message Types|
|quagga_rib|TABLE_DUMP_V2|PEER_INDEX_TABLE<br>RIB_IPV4_UNICAST<br>RIB_IPV6_UNICAST|IPv4/IPv6 Peer<br>IPv4/IPv6 Prefix| 


##Authors
Tetsumune KISO <t2mune@gmail.com>  
Yoshiyuki YAMAUCHI <info@greenhippo.co.jp>  
Nobuhiro ITOU <js333123@gmail.com>  

License
----------
Licensed under the [Apache License, Version 2.0][Apache]  
Copyright &copy; 2015 [greenHippo, LLC.][greenHippo]  
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[greenHippo]: http://greenhippo.co.jp
