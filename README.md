mrtparse
========

mrtparse is a module to read and analyze the MRT format data.  
The MRT format data can be used to export routing protocol messages, state changes, and routing information base contents, and is standardized in RFC6396.  
Programs like Quagga / Zebra, BIRD, OpenBGPD and PyRT can dump the MRT fotmat data.

##Currently supported types
Table_Dump(12), Table_Dump_V2(13), BGP4MP(16), BGP4MP_ET(17)

##Requirements
Python2、Python3

##Download
###git command
    
    $ git clone https://github.com/YoshiyukiYamauchi/mrtparse.git
    
###Browser
Access [https://github.com/YoshiyukiYamauchi/mrtparse.git][mrtparse_git], and click 'Download ZIP'.
[mrtparse_git]: https://github.com/YoshiyukiYamauchi/mrtparse.git
    


##Install
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


##Usage
Please overwrite the name space of time all the definition of mrtparse within. 
    
    from mrtparse import *
    
Or
    
    import mrtparse
    
##Programming
Please overwrite the name space of time all the definition of mrtparse within.
    
    from mrtparse import *
    
Please passed to the Reader() in the argument file object or files, and to loop through one entry.
    
    d = Reader(f)
        for m in d:
            "Describe the processing content"
    

##Example
###print_all.py
####content
Script that outputs the parse the file format of the MRT.
####Execution example
    $ cd example
    $ ./print_all.py "File name format of the MRT"
####Example output
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
####content
Script to be output to the configuration Parse a file format of the MRT
####Execution example
    $ ./exabgp_conf.py "File name format of the MRT"
####Example output
     neighbor 192.168.1.100 {
            router-id 192.168.0.20;
            local-address 192.168.1.20;
            local-as 65000;
            peer-as 64512;
            graceful-restart;
        
            static {

            }
        }

License
----------
Licensed under the [Apache License, Version 2.0][Apache]  
Copyright &copy; 2014 [greenHippo, LLC.][greenHippo]  
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[greenHippo]: http://greenhippo.co.jp
