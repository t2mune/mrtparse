mrtparse
========

| mrtparse is a module to read and analyze the MRT format data.
| The MRT format can be used to export routing protocol messages, state changes, and routing information base contents, and is defined in RFC6396_.
| Programs like Quagga_ / Zebra_, BIRD_, OpenBGPD_ and PyRT_ can dump the MRT format data.
| You can also download archives from `the Route Views Projects`_, `RIPE NCC`_.

.. _RFC6396: https://tools.ietf.org/html/rfc6396
.. _Quagga: http://www.nongnu.org/quagga/
.. _Zebra: https://www.gnu.org/software/zebra/
.. _BIRD: http://bird.network.cz/
.. _OpenBGPD: http://www.openbgpd.org/
.. _PyRT: https://github.com/mor1/pyrt
.. _`the Route Views Projects`: http://archive.routeviews.org/
.. _`RIPE NCC`: https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris/ris-raw-data

Supported MRT types
-------------------

+-------------------+---------+
| Name              | Value   |
+===================+=========+
| TABLE\_DUMP       | 12      |
+-------------------+---------+
| TABLE\_DUMP\_V2   | 13      |
+-------------------+---------+
| BGP4MP            | 16      |
+-------------------+---------+
| BGP4MP\_ET        | 17      |
+-------------------+---------+

Supported TABLE_DUMP subtypes
------------------------------

+-------------------+---------+
| Name              | Value   |
+===================+=========+
| AFI\_IPv4         | 1       |
+-------------------+---------+
| AFI\_IPv6         | 2       |
+-------------------+---------+

Supported TABLE_DUMP_V2 subtypes
--------------------------------

+-------------------------------+---------+
| Name                          | Value   |
+===============================+=========+
| PEER_INDEX_TABLE              | 1       |
+-------------------------------+---------+
| RIB\_IPV4\_UNICAST            | 2       |
+-------------------------------+---------+
| RIB\_IPV4\_MULTICAST          | 3       |
+-------------------------------+---------+
| RIB\_IPV6\_UNICAST            | 4       |
+-------------------------------+---------+
| RIB\_IPV6\_MULTICAST          | 5       |
+-------------------------------+---------+
| RIB\_GENERIC                  | 6       |
+-------------------------------+---------+
| RIB\_IPV4\_UNICAST\_ADDPATH   | 8       |
+-------------------------------+---------+
| RIB\_IPV4\_MULTICAST\_ADDPATH | 9       |
+-------------------------------+---------+
| RIB\_IPV6\_UNICAST\_ADDPATH   | 10      |
+-------------------------------+---------+
| RIB\_IPV6\_MULTICAST\_ADDPATH | 11      |
+-------------------------------+---------+
| RIB\_GENERIC\_ADDPATH         | 12      |
+-------------------------------+---------+

Supported BGP4MP/BGP4MP_ET subtypes
-----------------------------------

+--------------------------------------+---------+
| Name                                 | Value   |
+======================================+=========+
| BGP4MP\_STATE\_CHANGE                | 0       |
+--------------------------------------+---------+
| BGP4MP\_MESSAGE                      | 1       |
+--------------------------------------+---------+
| BGP4MP\_MESSAGE\_AS4                 | 4       |
+--------------------------------------+---------+
| BGP4MP\_STATE\_CHANGE\_AS4           | 5       |
+--------------------------------------+---------+
| BGP4MP\_MESSAGE\_LOCAL               | 6       |
+--------------------------------------+---------+
| BGP4MP\_MESSAGE\_AS4\_LOCAL          | 7       |
+--------------------------------------+---------+
| BGP4MP\_MESSAGE\_ADDPATH             | 8       |
+--------------------------------------+---------+
| BGP4MP\_MESSAGE\_AS4\_ADDPATH        | 9       |
+--------------------------------------+---------+
| BGP4MP\_MESSAGE\_LOCAL\_ADDPATH      | 10      |
+--------------------------------------+---------+
| BGP4MP\_MESSAGE\_AS4\_LOCAL\_ADDPATH | 11      |
+--------------------------------------+---------+

Supported BGP capabilities
--------------------------

+--------------------------------------------+---------+
| Name                                       | Value   |
+============================================+=========+
| Multiprotocol Extensions for BGP-4         | 1       |
+--------------------------------------------+---------+
| Route Refresh Capability for BGP-4         | 2       |
+--------------------------------------------+---------+
| Outbound Route Filtering Capability        | 3       |
+--------------------------------------------+---------+
| Graceful Restart Capability                | 64      |
+--------------------------------------------+---------+
| Support for 4-octet AS number capability   | 65      |
+--------------------------------------------+---------+
| ADD-PATH Capability                        | 69      |
+--------------------------------------------+---------+

Supported BGP attributes
------------------------

+-------------------------+---------+
| Name                    | Value   |
+=========================+=========+
| ORIGIN                  | 1       |
+-------------------------+---------+
| AS\_PATH                | 2       |
+-------------------------+---------+
| NEXT\_HOP               | 3       |
+-------------------------+---------+
| MULTI\_EXIT\_DISC       | 4       |
+-------------------------+---------+
| LOCAL\_PREF             | 5       |
+-------------------------+---------+
| ATOMIC\_AGGREGATE       | 6       |
+-------------------------+---------+
| AGGREGATOR              | 7       |
+-------------------------+---------+
| COMMUNITY               | 8       |
+-------------------------+---------+
| ORIGINATOR\_ID          | 9       |
+-------------------------+---------+
| CLUSTER\_LIST           | 10      |
+-------------------------+---------+
| MP\_REACH\_NLRI         | 14      |
+-------------------------+---------+
| MP\_UNREACH\_NLRI       | 15      |
+-------------------------+---------+
| EXTENDED\_COMMUNITIES   | 16      |
+-------------------------+---------+
| AS4\_PATH               | 17      |
+-------------------------+---------+
| AS4\_AGGREGATOR         | 18      |
+-------------------------+---------+
| AIGP                    | 26      |
+-------------------------+---------+
| LARGE\_COMMUNITY        | 32      |
+-------------------------+---------+
| ATTR\_SET               | 128     |
+-------------------------+---------+

Requirements
------------

Python2 or Python3 or PyPy or PyPy3

Installation
------------

::

    $ pip install mrtparse

or

::

    $ git clone https://github.com/YoshiyukiYamauchi/mrtparse.git
    $ cd mrtparse
    $ python setup.py install

Usage
-----

::

    from mrtparse import *

or

::

    import mrtparse

Programming
-----------

First, import the module.

::

    from mrtparse import *

| And pass a MRT format data as a filepath string or file object to a class Reader().
| It is also supported gzip and bzip2 format.
| You can retrieve each entry from the returned object using a loop and then process it.

::

    d = Reader(f)
    for m in d:
        <statements>

We have prepared some example scripts and sample data in `"examples"`_ and `"samples"`_ directory.

.. _`"examples"`: https://github.com/YoshiyukiYamauchi/mrtparse/tree/master/examples
.. _`"samples"`: https://github.com/YoshiyukiYamauchi/mrtparse/tree/master/samples

Authors
-------

| Tetsumune KISO t2mune@gmail.com
| Yoshiyuki YAMAUCHI info@greenhippo.co.jp
| Nobuhiro ITOU js333123@gmail.com

License
-------

| Licensed under the `Apache License, Version 2.0`_
| Copyright © 2018 Tetsumune KISO

.. _`Apache License, Version 2.0`: http://www.apache.org/licenses/LICENSE-2.0
