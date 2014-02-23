mrtparse
========

MRT形式のデータを読み込み、解析するためのモジュールです。
MRT形式は、ルーティング情報（メッセージ、状態遷移、経路情報）を保存するためのフォーマットで、RFC6396で標準化されています。

##何ができる？
[RIPE][ripe]などで取得したMRT形式の経路情報をパースすることができます。
もちろん、全経路のパースもできます。
[ripe]: http://data.ris.ripe.net/rrc00/

##動作環境
Python2、Python3

##対応タイプ(RFC6396)
###TableDump
BGPルーティング情報ベース（RIB）の内容をエンコードするために使用されるデータフォーマット。  
###TableDumpV2
ASNのサポートとのBGPマルチプロトコル拡張のためのフルサポートを含むようにTABLE_DUMPタイプを更新するデータフォーマット。 
###BGP4MP
Multiprotocol Extensions for BGP-4のデータを定義しているデータフォーマット。
###BGP4MP_ET
Multiprotocol Extensions for BGP-4のデータを定義していて、マイクロ秒での測定をサポートするデータフォーマット。


##インストール方法
    $ cd mrtparse-master
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
mrtparse内の定義をすべて現時点の名前空間に上書きします。 
    
    from mrtparse import *
    
もしくは、
    
    import mrtparse
    

##スクリプトの作成方法
mrtparse内の定義をすべて現時点の名前空間に上書きします。
    
    from mrtparse import *
    
ファイルまたはファイルオブジェクトを引数でReader()に渡し、1エントリずつループ処理する。  
    
    d = Reader(f)
        for m in d:
            処理内容を記述する
    
##Example
###print_all.py
####内容
MRT形式のファイルをパースして出力するスクリプト
####実行例
    $ cd example
    $ ./print_all.py MRT形式のファイル名
####出力例
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
####内容
MRT形式のファイルをパースしてコンフィグ形式に出力するスクリプト
####実行例
    $ ./exabgp_conf.py MRT形式のファイル名
####出力例
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
Licensed under the [Apache License, Version 2.0][Apache]  
Copyright &copy; 2014 [greenHippo, LLC.][greenHippo]  
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[greenHippo]: http://greenhippo.co.jp
