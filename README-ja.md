mrtparse
========

MRT形式のデータを読み込み、解析するためのモジュール。  
MRT形式とは、ルーティング情報（メッセージ、状態遷移、経路情報）を保存するためのフォーマットで、[RFC6396][rfc6396]で標準化されている。  
[Quagga / Zebra][quagga], [BIRD][bird], [OpenBGPD][openbgpd], [PyRT][pyrt]などでMRT形式のデータを出力することができる。
また、アーカイブを[Route Views Project][route views]や[RIPE NCC][ripe ncc]からダウンロードすることもできる。
[rfc6396]: https://tools.ietf.org/html/rfc6396
[quagga]: http://www.nongnu.org/quagga/
[bird]: http://bird.network.cz/
[openbgpd]: http://www.openbgpd.org/
[pyrt]: https://github.com/mor1/pyrt
[route views]: http://archive.routeviews.org/
[ripe ncc]: https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris/ris-raw-data

##対応しているMRT形式

| 名前          | 値  |
| ------------- | --- |
| Table_Dump    | 12  |
| Table_Dump_V2 | 13  |
| BGP4MP        | 16  |
| BGP4MP_ET     | 17  |

##対応しているBGP機能

| 名前                                     | 値  |
| ---------------------------------------- | --- |
| Multiprotocol Extensions for BGP-4       | 1   |
| Route Refresh Capability for BGP-4       | 2   |
| Outbound Route Filtering Capability      | 3   |
| Graceful Restart Capability              | 64  |
| Support for 4-octet AS number capability | 65  |
| ADD-PATH Capability                      | 69  |

##対応しているBGP属性

| 名前                 | 値  |
| -------------------- | --- |
| ORIGIN               | 1   |
| AS_PATH              | 2   |
| NEXT_HOP             | 3   |
| MULTI_EXIT_DISC      | 4   |
| LOCAL_PREF           | 5   |
| ATOMIC_AGGREGATE     | 6   |
| AGGREGATOR           | 7   |
| COMMUNITY            | 8   |
| ORIGINATOR_ID        | 9   |
| CLUSTER_LIST         | 10  |
| MP_REACH_NLRI        | 14  |
| MP_UNREACH_NLRI      | 15  |
| EXTENDED_COMMUNITIES | 16  |
| AS4_PATH             | 17  |
| AS4_AGGREGATOR       | 18  |
| AIGP                 | 26  |
| ATTR_SET             | 128 |

##動作環境
Python2 または Python3 または PyPy または PyPy3

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

["examples" ディレクトリ][examples]に作成例があります。
[examples]: https://github.com/YoshiyukiYamauchi/mrtparse/tree/master/examples

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
