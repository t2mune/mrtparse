mrtparse
========

mrtparse is a module to read and analyze the MRT format data.
The MRT format can be used to export routing protocol messages, state changes, and routing information base contents, and was standardized in [RFC6396][rfc6396].
Programs like [Quagga / Zebra][quagga], [BIRD][bird], [OpenBGPD][openbgpd] and [PyRT][pyrt] can dump the MRT fotmat data.
You can also download archives from [the Route Views Project][route views], [RIPE NCC][ripe ncc].
[rfc6396]: https://tools.ietf.org/html/rfc6396
[quagga]: http://www.nongnu.org/quagga/
[bird]: http://bird.network.cz/
[openbgpd]: http://www.openbgpd.org/
[pyrt]: https://github.com/mor1/pyrt
[route views]: http://archive.routeviews.org/
[ripe ncc]: https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris/ris-raw-data

##Supported MRT types

| Name          | Value |
| ------------- | ----- |
| Table_Dump    | 12    |
| Table_Dump_V2 | 13    |
| BGP4MP        | 16    |
| BGP4MP_ET     | 17    |

##Supported BGP capabilities

| Name                                     | Value |
| ---------------------------------------- | ----- |
| Multiprotocol Extensions for BGP-4       | 1     |
| Route Refresh Capability for BGP-4       | 2     |
| Outbound Route Filtering Capability      | 3     |
| Graceful Restart Capability              | 64    |
| Support for 4-octet AS number capability | 65    |
| ADD-PATH Capability                      | 69    |

##Supported BGP attributes

| Name                 | Value |
| -------------------- | ----- |
| ORIGIN               | 1     |
| AS_PATH              | 2     |
| NEXT_HOP             | 3     |
| MULTI_EXIT_DISC      | 4     |
| LOCAL_PREF           | 5     |
| ATOMIC_AGGREGATE     | 6     |
| AGGREGATOR           | 7     |
| COMMUNITY            | 8     |
| ORIGINATOR_ID        | 9     |
| CLUSTER_LIST         | 10    |
| MP_REACH_NLRI        | 14    |
| MP_UNREACH_NLRI      | 15    |
| EXTENDED_COMMUNITIES | 16    |
| AS4_PATH             | 17    |
| AS4_AGGREGATOR       | 18    |
| AIGP                 | 26    |
| ATTR_SET             | 128   |

##Requirements
Python2 or Python3 or PyPy or PyPy3 

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

We have prepared some example scripts in ["examples" directory][examples].
[examples]: https://github.com/YoshiyukiYamauchi/mrtparse/tree/master/examples
    

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
