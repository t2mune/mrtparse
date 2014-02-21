mrtparse
========

##mrtparseとは
MRT形式のファイルをパースするモジュール

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
###print_all.py MRT形式のファイルを解析して出力するスクリプト
    $ cd example
    $ ./print_all.py MRT形式のファイル名
###exabgp_conf.py

ライセンス
----------
Copyright &copy; 2014 [greenHippo, LLC.][greenHippo]  
Licensed under the [Apache License, Version 2.0][Apache]
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[greenHippo]: http://greenhippo.co.jp
