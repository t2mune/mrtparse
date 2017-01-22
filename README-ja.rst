mrtparse
========

| MRT形式のデータを読み込み、解析するためのモジュール。
| MRT形式とは、ルーティング情報（メッセージ、状態遷移、経路情報）を保存するためのフォーマットで、RFC6396_で定義されている。
| Quagga_ / Zebra_, BIRD_, OpenBGPD_, PyRT_ などでMRT形式のデータを出力することができる。
| また、アーカイブを `Route Views Projects`_ や `RIPE NCC`_ からダウンロードすることもできる。

.. _RFC6396: https://tools.ietf.org/html/rfc6396
.. _Quagga: http://www.nongnu.org/quagga/
.. _Zebra: https://www.gnu.org/software/zebra/
.. _BIRD: http://bird.network.cz/
.. _OpenBGPD: http://www.openbgpd.org/
.. _PyRT: https://github.com/mor1/pyrt
.. _`Route Views Projects`: http://archive.routeviews.org/
.. _`RIPE NCC`: https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris/ris-raw-data

サポートしているMRTのタイプ
---------------------------

+-------------------+---------+
| Name              | Value   |
+===================+=========+
| Table\_Dump       | 12      |
+-------------------+---------+
| Table\_Dump\_V2   | 13      |
+-------------------+---------+
| BGP4MP            | 16      |
+-------------------+---------+
| BGP4MP\_ET        | 17      |
+-------------------+---------+

サポートしているTABLE_DUMPのサブタイプ
--------------------------------------

+-------------------+---------+
| Name              | Value   |
+===================+=========+
| AFI\_IPv4         | 1       |
+-------------------+---------+
| AFI\_IPv6         | 2       |
+-------------------+---------+

サポートしているTABLE_DUMP_V2のサブタイプ
-----------------------------------------

+-------------------------------+---------+
| Name                          | Value   |
+===============================+=========+
| PEER_INDEX_TABLE              | 1       |
+-------------------------------+---------+
| RIB\_IPV4\_UNICAST            | 2       |
+-------------------------------+---------+
| RIB\_IPV4\_MULTICAST          | 3       |
+-------------------------------+---------+
| RIB\_IPV6\_UNICAST            | 4       |
+-------------------------------+---------+
| RIB\_IPV6\_MULTICAST          | 5       |
+-------------------------------+---------+
| RIB\_GENERIC                  | 6       |
+-------------------------------+---------+
| RIB\_IPV4\_UNICAST\_ADDPATH   | 8       |
+-------------------------------+---------+
| RIB\_IPV4\_MULTICAST\_ADDPATH | 9       |
+-------------------------------+---------+
| RIB\_IPV6\_UNICAST\_ADDPATH   | 10      |
+-------------------------------+---------+
| RIB\_IPV6\_MULTICAST\_ADDPATH | 11      |
+-------------------------------+---------+
| RIB\_GENERIC\_ADDPATH         | 12      |
+-------------------------------+---------+

サポートしているBGP4MP/BGP4MP-ETのサブタイプ
--------------------------------------------

+--------------------------------------+---------+
| Name                                 | Value   |
+======================================+=========+
| BGP4MP\_STATE\_CHANGE                | 0       |
+--------------------------------------+---------+
| BGP4MP\_MESSAGE                      | 1       |
+--------------------------------------+---------+

対応しているBGPの機能
---------------------

+--------------------------------------------+---------+
| Name                                       | Value   |
+============================================+=========+
| Multiprotocol Extensions for BGP-4         | 1       |
+--------------------------------------------+---------+
| Route Refresh Capability for BGP-4         | 2       |
+--------------------------------------------+---------+
| Outbound Route Filtering Capability        | 3       |
+--------------------------------------------+---------+
| Graceful Restart Capability                | 64      |
+--------------------------------------------+---------+
| Support for 4-octet AS number capability   | 65      |
+--------------------------------------------+---------+
| ADD-PATH Capability                        | 69      |
+--------------------------------------------+---------+

対応しているBGPの属性
---------------------

+-------------------------+---------+
| Name                    | Value   |
+=========================+=========+
| ORIGIN                  | 1       |
+-------------------------+---------+
| AS\_PATH                | 2       |
+-------------------------+---------+
| NEXT\_HOP               | 3       |
+-------------------------+---------+
| MULTI\_EXIT\_DISC       | 4       |
+-------------------------+---------+
| LOCAL\_PREF             | 5       |
+-------------------------+---------+
| ATOMIC\_AGGREGATE       | 6       |
+-------------------------+---------+
| AGGREGATOR              | 7       |
+-------------------------+---------+
| COMMUNITY               | 8       |
+-------------------------+---------+
| ORIGINATOR\_ID          | 9       |
+-------------------------+---------+
| CLUSTER\_LIST           | 10      |
+-------------------------+---------+
| MP\_REACH\_NLRI         | 14      |
+-------------------------+---------+
| MP\_UNREACH\_NLRI       | 15      |
+-------------------------+---------+
| EXTENDED\_COMMUNITIES   | 16      |
+-------------------------+---------+
| AS4\_PATH               | 17      |
+-------------------------+---------+
| AS4\_AGGREGATOR         | 18      |
+-------------------------+---------+
| AIGP                    | 26      |
+-------------------------+---------+
| LARGE\_COMMUNITY        | 32      |
+-------------------------+---------+
| ATTR\_SET               | 128     |
+-------------------------+---------+

動作環境
--------

Python2, Python3, PyPy, PyPy3

インストール方法
----------------

::

    $ pip install mrtparse

or

::

    $ git clone https://github.com/YoshiyukiYamauchi/mrtparse.git
    $ cd mrtparse
    $ python setup.py install
    running install
    running build
    running build_py
    running install_lib
    copying build/lib/mrtparse.py -> /Library/Python/2.7/site-packages
    byte-compiling /Library/Python/2.7/site-packages/mrtparse.py to mrtparse.pyc
    running install_egg_info
    Writing /Library/Python/2.7/site-packages/mrtparse-0.8-py2.7.egg-info

使用方法
--------

::

    from mrtparse import *

または、

::

    import mrtparse

スクリプトの作成方法
--------------------

はじめにモジュールを読み込む。

::

    from mrtparse import *

| MRT形式のファイル（gzip、bzip2にも対応）を文字列（ファイルへのパス）、 またはファイルオブジェクトでReader()に渡す。
| 返ってきたオブジェクトをループで1エントリずつ取り出して処理する。  

::

    d = Reader(f)
    for m in d:
        処理内容を記述する

`"examples"`_ にスクリプト作成例と `"samples"`_ にサンプルデータがある。

.. _`"examples"`: https://github.com/YoshiyukiYamauchi/mrtparse/tree/master/examples
.. _`"samples"`: https://github.com/YoshiyukiYamauchi/mrtparse/tree/master/samples

作者
----

| Tetsumune KISO t2mune@gmail.com
| Yoshiyuki YAMAUCHI info@greenhippo.co.jp
| Nobuhiro ITOU js333123@gmail.com

ライセンス
----------

| Licensed under the `Apache License, Version 2.0`_
| Copyright © 2017 Tetsumune KISO

.. _`Apache License, Version 2.0`: http://www.apache.org/licenses/LICENSE-2.0
