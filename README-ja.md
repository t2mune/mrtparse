mrtparse
========

MRT形式のデータを読み込み、解析するためのモジュールです。  
MRT形式は、ルーティング情報（メッセージ、状態遷移、経路情報）を保存するためのフォーマットで、RFC6396で標準化されています。  
この形式のデータを出力できるプログラムとしては、Quagga/Zebra、BIRD、OpenBGPD、PyRTなどがあります。

##解析可能なタイプ
Table_Dump(12), Table_Dump_V2(13), BGP4MP(16), BGP4MP_ET(17)

##動作環境
Python2、Python3

##取得方法
###gitコマンド
    
    $ git clone https://github.com/YoshiyukiYamauchi/mrtparse.git
    
###ブラウザ
[https://github.com/YoshiyukiYamauchi/mrtparse.git][mrtparse_git]にアクセスして「Download ZIP」をクリック。
[mrtparse_git]: https://github.com/YoshiyukiYamauchi/mrtparse.git
    

##インストール方法
    $ cd クローンディレクトリ
    $ python setup.py install
    running install
    running build
    running build_py
    running install_lib
    copying build/lib/mrtparse.py -> /Library/Python/2.7/site-packages
    byte-compiling /Library/Python/2.7/site-packages/mrtparse.py to mrtparse.pyc
    running install_egg_info
    Writing /Library/Python/2.7/site-packages/mrtparse-0.8-py2.7.egg-info


##使い方
    
    from mrtparse import *
    
もしくは、
    
    import mrtparse
    

##スクリプトの作成方法
はじめにモジュールを読み込む。
    
    from mrtparse import *
    
MRT形式のファイル（gzip、bzip2にも対応）を文字列（ファイルへのパス）、 またはファイルオブジェクトでReader()に渡す。  
返ってきたオブジェクトをループで1エントリずつ取り出して処理する。  

    
    d = Reader(f)
    for m in d:
        処理内容を記述する
    
##スクリプトの作成例
これらのスクリプトは、examples内に収録。
###print_all.py
####内容
MRT形式のファイルの内容を出力する
####実行例
    print_all.py ファイルへのパス
####出力例
    ---------------------------------------------------------------
    MRT Header
        Timestamp: 1392828028(2014-02-20 01:40:28)
        Type: 16(BGP4MP)
        Subtype: 5(BGP4MP_STATE_CHANGE_AS4)
        Length: 24
    BGP4MP_STATE_CHANGE_AS4
        Peer AS Number: 100
        Local AS Number: 64512
        Interface Index: 0
        Address Family: 1(AFI_IPv4)
        Peer IP Address: 192.168.1.21
        Local IP Address: 192.168.1.100
        Old State: 5(OpenConfirm)
        New State: 6(Established)
    ---------------------------------------------------------------
    MRT Header
        Timestamp: 1392828028(2014-02-20 01:40:28)
        Type: 16(BGP4MP)
        Subtype: 4(BGP4MP_MESSAGE_AS4)
        ....
        

###exabgp_conf.py
####内容
MRT形式のファイルをexabgp用のコンフィグ形式に変換して出力する。
####実行例
    exabgp_conf.py ファイルへのパス
####出力例
    neighbor 192.168.1.100 {
        router-id 192.168.0.20;
        local-address 192.168.1.20;
        local-as 65000;
        peer-as 64512;
        graceful-restart;

        static {
                route 1.0.0.0/24 origin IGP as-path [29049 15169 ] next-hop 192.168.1.254;
                route 1.0.4.0/24 origin IGP as-path [29049 6939 7545 56203 ] next-hop 192.168.1.254;
                route 1.0.5.0/24 origin IGP as-path [29049 6939 7545 56203 ] next-hop 192.168.1.254;
                route 1.0.6.0/24 origin IGP as-path [29049 20485 4826 38803 56203 ] community [20485:31701] next-hop 192.168.1.254;
                route 1.0.7.0/24 origin IGP as-path [29049 20485 4826 38803 56203 ] community [20485:31701] next-hop 192.168.1.254;
                route 1.0.20.0/23 origin IGP as-path [29049 2914 2519 ] community [2914:410 2914:1403 2914:2401 2914:3400] next-hop 192.168.1.254;
                route 1.0.22.0/23 origin IGP as-path [29049 2914 2519 ] community [2914:410 2914:1403 2914:2401 2914:3400] next-hop 192.168.1.254;
                route 1.0.24.0/23 origin IGP as-path [29049 2914 2519 ] community [2914:410 2914:1403 2914:2401 2914:3400] next-hop 192.168.1.254;
                route 1.0.26.0/23 origin IGP as-path [29049 2914 2519 ] community [2914:410 2914:1403 2914:2401 2914:3400] next-hop 192.168.1.254;
                route 1.0.28.0/22 origin IGP as-path [29049 2914 2519 ] community [2914:410 2914:1403 2914:2401 2914:3400] next-hop 192.168.1.254;
                ...
        }
    }


ライセンス
----------
Licensed under the [Apache License, Version 2.0][Apache]  
Copyright &copy; 2014 [greenHippo, LLC.][greenHippo]  
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[greenHippo]: http://greenhippo.co.jp
