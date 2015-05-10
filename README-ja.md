mrtparse
========

MRT形式のデータを読み込み、解析するためのモジュール。  
MRT形式とは、ルーティング情報（メッセージ、状態遷移、経路情報）を保存するためのフォーマットで、RFC6396で標準化されている。  
Quagga/Zebra、BIRD、OpenBGPD、PyRTなどでMRT形式のデータを出力することができる。

##現在対応しているMRT形式
Table_Dump(12), Table_Dump_V2(13), BGP4MP(16), BGP4MP_ET(17)

##現在対応しているBGPアトリビュート
ORIGIN(1), AS_PATH(2), NEXT_HOP(3), MULTI_EXIT_DISC(4), LOCAL_PREF(5), ATOMIC_AGGREGATE(6), AGGREGATOR(7), COMMUNITY(8), ORIGINATOR_ID(9), CLUSTER_LIST(10), MP_REACH_NLRI(14), MP_UNREACH_NLRI(15), EXTENDED_COMMUNITIES(16), AS4_PATH(17), AS4_AGGREGATOR(18), AIGP(26), ATTR_SET(128)

##動作環境
Python2 または Python3 または PyPy

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
####使用方法
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
        ...
        

###exabgp_conf.py
####内容
MRT形式のファイルを[exabgp][exabgp_git]用のコンフィグ形式に変換して出力する。
[exabgp_git]: https://github.com/Exa-Networks/exabgp
####使用方法
    使用方法: exabgp_conf.py [-h] [-r ルータID] [-l ローカルAS] [-p ピアAS]
                             [-L ローカルアドレス] [-n ネイバーアドレス] [-4 [ネクストホップ]]
                             [-6 [ネクストホップ]] [-a]
                             ファイルのパス
 
    このスクリプトはExaBGP形式の設定ファイルに変換する

    オプションなし引数:
      ファイルのパス        MRT形式のファイルのパスを指定する
    
    オプションあり引数:
      -h, --help            ヘルプメッセージを表示して終了する
      -r ルータID, --router-id ルータID
                            ルータIDを設定する (初期値: 192.168.0.1)
      -l ローカルAS, --local-as ローカルAS
                            ローカルAS番号を設定する (初期値: 64512)
      -p ピアAS, --peer-as ピアAS
                            ピアAS番号を設定する (初期値: 65000)
      -L ローカルアドレス, --local-addr ローカルアドレス
                            ローカルのアドレスを設定する (初期値: 192.168.1.1)
      -n ネイバーアドレス, --neighbor ネイバーアドレス
                            ネイバーのアドレスを設定する (初期値: 192.168.1.100)
      -4 [ネクストホップ], --ipv4 [ネクストホップ]
                            IPv4のエントリーを変換し、指定があればネクストホップを変更する
      -6 [ネクストホップ], --ipv6 [ネクストホップ]
                            IPv6のエントリーを変換し、指定があればネクストホップを変更する
      -a, --all-entries     全てのエントリーを変換する
                            (初期動作: 同じ経路に対して、最初のエントリーのみ変換する)
####出力例
    neighbor 192.168.1.100 {
        router-id 192.168.0.20;
        local-address 192.168.1.20;
        local-as 65000;
        peer-as 64512;
        graceful-restart;
        aigp enable;

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

###slice.py
####内容
MRT形式のファイルについて、下記データをファイル出力する  
1. 指定された開始時間から終了時間までの指定された秒単位の間隔についてのデータ  
2. 指定された開始時間から終了時間までのデータ  
3. 指定された秒単位の間隔についてのデータ  
####使用方法
    使用方法: slice.py [-h] [-s 開始時間] [-e 終了時間] [-i 間隔] [-c {gz,bz2}]
                    ファイルのパス
    
    このスクリプトはMRT形式のファイルを分割する
    
    オプションなし引数:
      ファイルのパス        MRT形式のファイルのパスを指定する
    
    オプションあり引数:
      -h, --help            ヘルプメッセージを表示して終了する
      -s 開始時間, --start-time 開始時間
                            開始時間を YYYY-MM-DD HH:MM:SS の形式で指定する
      -e 終了時間, --end-time 終了時間
                            終了時間を YYYY-MM-DD HH:MM:SS の形式で指定する
      -i 間隔, --interval 間隔
                            ファイルを分割する間隔(秒)を指定する
      -c {gz,bz2}, --compress-type {gz,bz2}
                            分割ファイルの圧縮形式(gz, bz2)を指定する
####出力例
    # slice.py -s '2015-04-26 03:26:00' -e '2014-04-26 03:27:00' -i 10 -c bz2 -f latest-update.gz
    # ls
    latest-update-20150426-032600.bz2
    latest-update-20150426-032610.bz2
    latest-update-20150426-032620.bz2
    latest-update-20150426-032630.bz2
    latest-update-20150426-032640.bz2
    latest-update-20150426-032650.bz2


###summary.py
####内容
MRT形式のファイルのサマリーを出力する
####使用方法
    summary.py ファイルへのパス
####出力例
    [2014-08-11 03:45:00 - 2014-08-11 03:49:59]
    BGP4MP:                             5973
        BGP4MP_MESSAGE:                   34
            UPDATE:                       24
            KEEPALIVE:                    10
        BGP4MP_MESSAGE_AS4:             5896
            UPDATE:                     5825
            KEEPALIVE:                    71
        BGP4MP_STATE_CHANGE_AS4:          43
            Idle:                          1
            Connect:                      20
            Active:                       18
            OpenSent:                      4


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
