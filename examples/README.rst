Example Scripts
===============

mrt2json.py
-----------

Description
~~~~~~~~~~~

| It converts MRT format to JSON.

Usage
~~~~~

::

    mrt2json.py PATH_TO_FILE

Result
~~~~~~

::

    [
      {
        "timestamp": [
          1546731000,
          "2019-01-06 08:30:00"
        ],
        "type": [
          16,
          "BGP4MP"
        ],
        "subtype": [
          4,
          "BGP4MP_MESSAGE_AS4"
        ],
        "length": 110,
        "peer_as": "64050",
        "local_as": "12654",
        "ifindex": 0,
        "afi": [
          1,
          ...

mrt2yaml.py
-----------

Description
~~~~~~~~~~~

| It converts MRT format to YAML.

Usage
~~~~~

::

    mrt2yaml.py PATH_TO_FILE

Result
~~~~~~

::

    ---
    - timestamp: [1546731000, '2019-01-06 08:30:00']
      type: [16, BGP4MP]
      subtype: [4, BGP4MP_MESSAGE_AS4]
      length: 110
      peer_as: '64050'
      local_as: '12654'
      ifindex: 0
      afi: [1, IPv4]
      peer_ip: 182.54.128.2
      local_ip: 193.0.4.28
      bgp_message:
        marker: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
        length: 90
        type: [2, UPDATE]
        withdrawn_routes_length: 0
        withdrawn_routes: []
        path_attribute_length: 47
        path_attributes:
        - flag: 64
        ...

Authors
-------

| Tetsumune KISO t2mune@gmail.com
| Yoshiyuki YAMAUCHI info@greenhippo.co.jp
| Nobuhiro ITOU js333123@gmail.com

License
-------

| Licensed under the `Apache License, Version 2.0`_
| Copyright © 2019 Tetsumune KISO

.. _`Apache License, Version 2.0`: http://www.apache.org/licenses/LICENSE-2.0
