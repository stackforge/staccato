
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

    $ curl -X POST http://localhost:5309/v1/transfers --data '{"source_url": "file:///bin/bash", "destination_url": "file:///tmp/ooo"}' -H "Content-Type: application/json"
    {"start_offset": 0, "id": "2eade223-b11b-413b-9185-7b16c1b2ed6d", "state": "STATE_NEW", "progress": 0, "end_offset": -1, "source_url": "file:///bin/bash", "destination_options": {}, "destination_url": "file:///tmp/ooo", "source_options": {}}

Check the status::

    $ curl -X GET http://localhost:5309/v1/transfers/2eade223-b11b-413b-9185-7b16c1b2ed6d 
    {"start_offset": 0, "id": "2eade223-b11b-413b-9185-7b16c1b2ed6d", "state": "STATE_NEW", "progress": 0, "end_offset": -1, "source_url": "file:///bin/bash", "destination_options": {}, "destination_url": "file:///tmp/ooo", "source_options": {}


Cancel::

    $ curl -X POST http://localhost:5309/v1/transfers/2eade223-b11b-413b-9185-7b16c1b2ed6d/action --data '{"xferaction": "cancel"}'  -H "Content-Type: application/json"


Clean up::

    $ curl -X DELETE http://localhost:5309/v1/transfers/2eade223-b11b-413b-9185-7b16c1b2ed6d 

List all::

    $ curl -X GET http://localhost:5309/v1/transfers
