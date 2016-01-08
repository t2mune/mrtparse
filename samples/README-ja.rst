MRTデータサンプル
----------------------

+-------------------------+-----------------+----------------------------+------------------------+
| ファイル名              | タイプ          | サブタイプ                 | 内容                   |
|                         |                 |                            |                        |
|                         |                 |                            |                        |
+=========================+=================+============================+========================+
| bird6\_bgp              | BGP4MP          | BGP4MP\_MESSAGE            | IPv6 Peer              |
|                         |                 | BGP4MP\_MESSAGE\_AS4       | IPv6 Prefix            |
|                         |                 | BGP4MP\_STATE\_CHANGE\_AS4 | All BGP Message Types  |
|                         |                 |                            | ADD-PATH Capability    |
+-------------------------+-----------------+----------------------------+------------------------+
| bird\_bgp               | BGP4MP          | BGP4MP\_MESSAGE            | IPv4 Peer              |
|                         |                 | BGP4MP\_MESSAGE\_AS4       | IPv4 Prefix            |
|                         |                 | BGP4MP\_STATE\_CHANGE\_AS4 | All BGP Message Types  |
|                         |                 |                            | ADD-PATH Capability    |
+-------------------------+-----------------+----------------------------+------------------------+
| openbgpd\_bgp           | BGP4MP          | BGP4MP\_MESSAGE            | IPv4/IPv6 Peer         |
|                         |                 | BGP4MP\_MESSAGE\_AS4       | IPv4/IPv6/VPNv4 Prefix |
|                         |                 | BGP4MP\_STATE\_CHANGE      | All BGP Message Types  |
|                         |                 | BGP4MP\_STATE\_CHANGE\_AS4 |                        |
+-------------------------+-----------------+----------------------------+------------------------+
| openbgpd\_rib\_table    | TABLE\_DUMP     | AFI\_IPv4                  | IPv4/IPv6 Peer         |
|                         |                 | AFI\_IPv6                  | IPv4/IPv6 Prefix       |
+-------------------------+-----------------+----------------------------+------------------------+
| openbgpd\_rib\_table-mp | BGP4MP          | BGP4MP\_ENTRY              | Unsupported Subtype    |
+-------------------------+-----------------+----------------------------+------------------------+
| openbgpd\_rib\_table-v2 | TABLE\_DUMP\_V2 | PEER\_INDEX\_TABLE         | IPv4/IPv6 Peer         |
|                         |                 | RIB\_IPV4\_UNICAST         | IPv4/IPv6/VPNv4 Prefix |
|                         |                 | RIB\_IPV6\_UNICAST         |                        |
|                         |                 | RIB\_GENERIC               |                        |
+-------------------------+-----------------+----------------------------+------------------------+
| quagga\_bgp             | BGP4MP          | BGP4MP\_MESSAGE            | IPv4/IPv6 Peer         |
|                         |                 | BGP4MP\_MESSAGE\_AS4       | IPv4/IPv6/VPNv4 Prefix |
|                         |                 | BGP4MP\_STATE\_CHANGE\_AS4 | All BGP Message Types  |
+-------------------------+-----------------+----------------------------+------------------------+
| quagga\_rib             | TABLE\_DUMP\_V2 | PEER\_INDEX\_TABLE         | IPv4/IPv6 Peer         |
|                         |                 | RIB\_IPV4\_UNICAST         | IPv4/IPv6 Prefix       |
|                         |                 | RIB\_IPV6\_UNICAST         |                        |
+-------------------------+-----------------+----------------------------+------------------------+

作者
-------

| Tetsumune KISO t2mune@gmail.com
| Yoshiyuki YAMAUCHI info@greenhippo.co.jp
| Nobuhiro ITOU js333123@gmail.com

ライセンス
----------

| Licensed under the `Apache License, Version 2.0`_
| Copyright © 2016 `greenHippo, LLC.`_

.. _`Apache License, Version 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`GreenHippo, LLC.`: http://greenhippo.co.jp
