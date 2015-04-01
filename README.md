mrtparse
========

mrtparse is a module to read and analyze the MRT format data.  
The MRT format data can be used to export routing protocol messages, state changes, and routing information base contents, and is standardized in RFC6396.  
Programs like Quagga / Zebra, BIRD, OpenBGPD and PyRT can dump the MRT fotmat data.

##Currently supported MRT types
Table_Dump(12), Table_Dump_V2(13), BGP4MP(16), BGP4MP_ET(17)

##Currently supported BGP attributes
ORIGIN(1), AS_PATH(2), NEXT_HOP(3), MULTI_EXIT_DISC(4), LOCAL_PREF(5), ATOMIC_AGGREGATE(6), AGGREGATOR(7), COMMUNITY(8), ORIGINATOR_ID(9), CLUSTER_LIST(10), MP_REACH_NLRI(14), MP_UNREACH_NLRI(15), EXTENDED_COMMUNITIES(16), AS4_PATH(17), AS4_AGGREGATOR(18), AIGP(26), ATTR_SET(128)

##Requirements
Python2 or Python3 or PyPy

##Download
###git command
    
    $ git clone https://github.com/YoshiyukiYamauchi/mrtparse.git
    
###Browser
Access [https://github.com/YoshiyukiYamauchi/mrtparse.git][mrtparse_git], and click 'Download ZIP'.
[mrtparse_git]: https://github.com/YoshiyukiYamauchi/mrtparse.git
    

##Install
    $ cd <Clone Directory>
    $ python setup.py install
    running install
    running build
    running build_py
    running install_lib
    copying build/lib/mrtparse.py -> /Library/Python/2.7/site-packages
    byte-compiling /Library/Python/2.7/site-packages/mrtparse.py to mrtparse.pyc
    running install_egg_info
    Writing /Library/Python/2.7/site-packages/mrtparse-0.8-py2.7.egg-info


##Usage
    
    from mrtparse import *
    
or
    
    import mrtparse
    
##Programming
First, import the module.
    
    from mrtparse import *
    
And pass a MRT format data as a filepath string or file object to a class Reader().   
It is also supported gzip and bzip2 format.  
You can retrieve each entry from the returned object using a loop and then process it.  

    
    d = Reader(f)
    for m in d:
        <statements>
    

##Example
These scripts are included in 'examples' directory.
###print_all.py
####Description
It displays the contents of a MRT format file.
####Usage
    print_all.py <path to the file>
####Result
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
####Description
It converts MRT format to [exabgp][exabgp_git] config format and displays it.
[exabgp_git]: https://github.com/Exa-Networks/exabgp
####Usage
    exabgp_conf.py <path to the file>
####Result
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


###slice.py
####Description
It outputs the following data of a MRT format file.  
1. The data for the interval of the specified seconds from the specified start time to the specified end time.  
2. The data from the specified start time to the specified end time.  
3. The data for the interval of the specified seconds.  
####Usage
    slice.py [-h] [-s START_TIME] [-e END_TIME] [-i INTERVAL] [-c {gz,bz2}] -f <path to the file>
####Result
    # slice.py -s '2014-08-11 03:46:40' -e '2014-08-11 03:46:50' -i 2 -f latest-update.gz
    # ls
    latest-update.gz-20140811-034640
    latest-update.gz-20140811-034642
    latest-update.gz-20140811-034644
    latest-update.gz-20140811-034646
    latest-update.gz-20140811-034648


###summary.py
####Description
It displays the summary of a MRT format file.
####Usage
    summary.py <path to the file>
####Result
    [2014-08-11 03:45:00 - 2014-08-11 03:49:59]
    BGP4MP:                         5973
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
