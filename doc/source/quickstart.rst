
Stacatto Quick Start
====================

This document describes the fastest way to get the transfer service 
rolling.

Installation
------------

create a python virtual environment and install staccatto into it::

    $ virtualenv --no-site-packages staccattoVE
    $ source staccattoVE/bin/activate
    $ python setup.py install

Configuration Files
-------------------

There are three major configuration files:

- staccato-api.conf
- staccato-api-paste.ini
- staccato-protocols.json

sample files that will work for the purposes of this quick start
guide are included in the etc directory.

API Program
-----------

The API program runs the REST interpreter.  To start it run::

    $ staccato-api --config-file etc/staccato-api.conf 

Scheduler Program
-----------------

The scheduler program checks for transfers that are ready to go and
starts them.  To start the scheduler run the following::

    $ staccato-scheduler --config-file etc/staccato-api.conf 

Interact With curl
------------------

Request a transfer::

    $ curl   localhost:9595/v1/urlxfer -H 'x-xfer-srcurl:file:///bin/bash' -H 'x-xfer-dsturl:file:///tmp/test1' {"progress": 0, "dsturl": "file:///tmp/test1", "srcurl": "file:///bin/bash", "id": "b7901019-dc33-4abc-be55-76ce2b2206a5", "state": "STATE_NEW"}

Check the status::

    $ curl localhost:9595/v1/status/b7901019-dc33-4abc-be55-76ce2b2206a5
    {"progress": 0, "dsturl": "file:///tmp/test1", "srcurl": "file:///bin/bash", "id": "b7901019-dc33-4abc-be55-76ce2b2206a5", "state": "STATE_COMPLETE"}

Clean up::

    $ curl localhost:9595/v1/delete/b7901019-dc33-4abc-be55-76ce2b2206a5
