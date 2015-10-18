##サンプルMRTデータ
###
|ファイル名
|タイプ
|サブタイプ
|内容
|
|:-
|:-:
|:-:
|:-
|
|bird6_bgp
|BGP4MP
|BGP4MP_MESSAGE  BGP4MP_MESSAGE_AS4  BGP4MP_STATE_CHANGE_AS4
|IPv6ピア  IPv6経路  全てのBGPメッセージタイプ  ADD-PATH機能
|
|bird_bgp
|BGP4MP
|BGP4MP_MESSAGE  BGP4MP_MESSAGE_AS4  BGP4MP_STATE_CHANGE_AS4
|IPv4ピア  IPv4経路  全てのBGPメッセージタイプ  ADD-PATH機能
|
|openbgpd_bgp
|BGP4MP
|BGP4MP_MESSAGE  BGP4MP_MESSAGE_AS4  BGP4MP_STATE_CHANGE  BGP4MP_STATE_CHANGE_AS4
|IPv4/IPv6ピア  IPv4/IPv6/VPNv4経路  全てのBGPメッセージタイプ
|
|openbgpd_rib_table
|TABLE_DUMP
|AFI_IPv4  AFI_IPv6
|IPv4/IPv6ピア  IPv4/IPv6経路
|
|openbgpd_rib_table-mp
|BGP4MP
|BGP4MP_ENTRY
|Unsupported Subtype
|
|openbgpd_rib_table-v2
|TABLE_DUMP_V2
|PEER_INDEX_TABLE  RIB_IPV4_UNICAST  RIB_IPV6_UNICAST  RIB_GENERIC
|IPv4/IPv6ピア  IPv4/IPv6/VPNv4経路
|
|quagga_bgp           |BGP4MP
|BGP4MP_MESSAGE  BGP4MP_MESSAGE_AS4  BGP4MP_STATE_CHANGE_AS4
|IPv4/IPv6ピア  IPv4/IPv6/VPNv4経路  全てのBGPメッセージタイプ
|
|quagga_rib           |TABLE_DUMP_V2
|PEER_INDEX_TABLE  RIB_IPV4_UNICAST  RIB_IPV6_UNICAST
|IPv4/IPv6ピア  IPv4/IPv6/VPNv4経路
|


##作者
Tetsumune KISO <t2mune@gmail.com>  
Yoshiyuki YAMAUCHI <info@greenhippo.co.jp>  
Nobuhiro ITOU <js333123@gmail.com>  

ライセンス
----------
Licensed under the [Apache License, Version 2.0][Apache]  
Copyright &copy; 2015 [greenHippo, LLC.][greenHippo]  
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[greenHippo]: http://greenhippo.co.jp
