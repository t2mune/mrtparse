mrtparse
========

##mrtparseとは
MRT形式のファイルをパースするモジュール

##何ができる？
[RIPE][ripe]などで取得したMRT形式のルート情報をパースすることができます。
フルルートのパースもできます。
[ripe]: http://data.ris.ripe.net/rrc00/

##動作環境
Python2、Python3

##対応タイプ
TableDump, TableDumpV2, BGP4MP, BGP4MP_ET

##オブジェクト樹形図
view pdf

##インストール方法
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
    $


##使い方
    from mrtparse import *

##exampleのスクリプトの説明
###print_all.py ※MRT形式のファイルを解析して出力するスクリプトの出力例
    $ cd example
    $ ./print_all.py MRT形式のファイル名
    ---------------------------------------------------------------
    MRT Header
    Timestamp: 1392552061(2014-02-16 21:01:01)
        Type: 16(BGP4MP)
        Subtype: 1(BGP4MP_MESSAGE)
        Length: 94
    BGP4MP_MESSAGE
        Peer AS Number: 100
        Local AS Number: 64512
        Interface Index: 0
        Address Family: 1(AFI_IPv4)
        Peer IP Address: 192.168.1.21
        Local IP Address: 192.168.1.100
    BGP Message
        Marker: -- ignored --
        Length: 78
        Type: 1(OPEN)
        Version: 4
        My AS: 100
        Hold Time: 90
        BGP Identifier: 192.168.0.21
        Optional Parameter Length: 49
        Parameter Type/Length: 2/6
            Capabilities
                Capability Code: 1(Multiprotocol Extensions for BGP-4)
                Capability Length: 4
                AFI: 1(AFI_IPv4)
                Reserved: 0
                SAFI: 1(SAFI_UNICAST)
        Parameter Type/Length: 2/6
            Capabilities
                Capability Code: 1(Multiprotocol Extensions for BGP-4)
                Capability Length: 4
                AFI: 2(AFI_IPv6)
                Reserved: 0
                SAFI: 1(SAFI_UNICAST)
        Parameter Type/Length: 2/2
            Capabilities
                Capability Code: 128(Unassigned)
                Capability Length: 0
        Parameter Type/Length: 2/2
            Capabilities
                Capability Code: 2(Route Refresh Capability for BGP-4)
                Capability Length: 0
        Parameter Type/Length: 2/4
            Capabilities
                Capability Code: 64(Graceful Restart Capability)
                Capability Length: 2
                Restart Timers: 120
        Parameter Type/Length: 2/9
            Capabilities
                Capability Code: 3(Outbound Route Filtering Capability)
                Capability Length: 7
                AFI: 1(AFI_IPv4)
                Reserved: 0
                SAFI: 1(SAFI_UNICAST)
                Number: 1
                Type: 64
                Send Receive: 1
        Parameter Type/Length: 2/6
            Capabilities
                Capability Code: 65(Support for 4-octet AS number capability)
                Capability Length: 4
                AS Number: 100
    ---------------------------------------------------------------
###exabgp_conf.py
    $ ./exabgp_conf.py MRT形式のファイル名
     neighbor 192.168.1.100 {
            router-id 192.168.0.20;
            local-address 192.168.1.20;
            local-as 65000;
            peer-as 64512;
            graceful-restart;
        
            static {

            }
        }

ライセンス
----------
Copyright &copy; 2014 [greenHippo, LLC.][greenHippo]  
Licensed under the [Apache License, Version 2.0][Apache]
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[greenHippo]: http://greenhippo.co.jp
