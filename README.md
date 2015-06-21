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
 + Python2 or Python3 or PyPy
 + `enum` module (either built in since Python3.4 or the backported version [`enum34`](https://pypi.python.org/pypi/enum34))

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
This script displays the contents of a MRT format file.
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
This script converts MRT format to [ExaBGP][exabgp_git] config format and displays it.
[exabgp_git]: https://github.com/Exa-Networks/exabgp
####Usage
    usage: exabgp_conf.py [-h] [-r ROUTER_ID] [-l LOCAL_AS] [-p PEER_AS]
                          [-L LOCAL_ADDR] [-n NEIGHBOR] [-4 [NEXT_HOP]]
                          [-6 [NEXT_HOP]] [-a]
                          path_to_file

    This script converts to ExaBGP format config.
    
    positional arguments:
      path_to_file          specify path to MRT-fomatted file
    
    optional arguments:
      -h, --help            show this help message and exit
      -r ROUTER_ID, --router-id ROUTER_ID
                            specify router-id (default: 192.168.0.1)
      -l LOCAL_AS, --local-as LOCAL_AS
                            specify local AS number (default: 64512)
      -p PEER_AS, --peer-as PEER_AS
                            specify peer AS number (default: 65000)
      -L LOCAL_ADDR, --local-addr LOCAL_ADDR
                            specify local address (default: 192.168.1.1)
      -n NEIGHBOR, --neighbor NEIGHBOR
                            specify neighbor address (default: 192.168.1.100)
      -4 [NEXT_HOP], --ipv4 [NEXT_HOP]
                            convert IPv4 entries and specify IPv4 next-hop if exists
      -6 [NEXT_HOP], --ipv6 [NEXT_HOP]
                            convert IPv6 entries and specify IPv6 next-hop if exists
      -a, --all-entries     convert all entries
                            (default: convert only first entry per one prefix)
####Result
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
####Description
This script outputs the following data of a MRT format file.  
1. The data for the interval of the specified seconds from the specified start time to the specified end time.  
2. The data from the specified start time to the specified end time.  
3. The data for the interval of the specified seconds.  
####Usage
    usage: slice.py [-h] [-s START_TIME] [-e END_TIME] [-i INTERVAL] [-c {gz,bz2}]
                    path_to_file
    
    This script slices MRT format data.
    
    positional arguments:
      path_to_file          specify path to MRT format file
    
    optional arguments:
      -h, --help            show this help message and exit
      -s START_TIME, --start-time START_TIME
                            specify start time in format YYYY-MM-DD HH:MM:SS
      -e END_TIME, --end-time END_TIME
                            specify end time in format YYYY-MM-DD HH:MM:SS
      -i INTERVAL, --interval INTERVAL
                            specify interval in seconds
      -c {gz,bz2}, --compress-type {gz,bz2}
                            specify compress type (gz, bz2)

####Result
    # slice.py -s '2015-04-26 03:26:00' -e '2014-04-26 03:27:00' -i 10 -c bz2 -f latest-update.gz
    # ls
    latest-update-20150426-032600.bz2
    latest-update-20150426-032610.bz2
    latest-update-20150426-032620.bz2
    latest-update-20150426-032630.bz2
    latest-update-20150426-032640.bz2
    latest-update-20150426-032650.bz2


###summary.py
####Description
This script displays the summary of a MRT format file.
####Usage
    summary.py <path to the file>
####Result
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
