Stacatto REST API
=================

This document describes the current v1 Stacatto REST API

Data Types
----------

States
******

- STATE_NEW
- STATE_RUNNING
- STATE_CANCELING
- STATE_CANCELED
- STATE_ERRORING
- STATE_ERROR
- STATE_COMPLETE
- STATE_DELETED

Xfer Document Type
******************

* id : UUID

* source_url : string

  The URL of the source of the data to be transferred. 

* destination_url : string 

  The URL of the destination where the source URL will be copied.

* state : State

  The current state of the transfer.

* progress : integer

  The number of bytes safely transferred to the destination storage system
  thus far.

* start_offset

  The offset into the source data set from which the transfer will begin.

* end_offset : integer

  The offset into the source data set at which the transfer will end.

* destination_options : JSON document

  A JSON document that is defined by the transfer service protocol plugin
  in use.  That plugin is determined by the scheme portion of the
  destination URL.

* source_options : JSON document

  A JSON document that is defined by the transfer service protocol plugin
  in use.  That plugin is determined by the scheme portion of the
  source URL.


Example::

{"start_offset": 0, 
 "id": "590edf8c-1b2b-44d0-af6a-d9190753b6eb", 
 "state": "STATE_NEW", 
 "progress": 0, 
 "end_offset": -1,
 "source_url": "file:///bin/bash",
 "destination_options": {},
 "destination_url": "file:///tmp/ooo",
 "source_options": {}}



List All Transfers
------------------

GET /v1/transfers

Options: 
- limit
- next...

response: 200
List of xfer document types

Request a Transfer
------------------

POST /v1/transfers

Required Parameters

- source_url <string url>
- destination_url <string url>

Optional

- source_options <json doc>
- destination_options <json doc>
- start_offset <int>
- end_offset <int>

Response:
201
xfer document type

Check Transfer Status
---------------------

GET /v1/transfers/{transfer id}

response: 200
xfer document types

Cancel A Transfer
-----------------

POST /v1/transfers/{transfer id}/action

Required Parameters:
- xferaction: cancel

"Content-Type: application/json"

Response: 202 (if async)
          204 (if sync)

Delete A Transfer
-----------------

DELETE /v1/transfers/{transfer id}


Response: 202 (if async)
          204 (if sync)


xfer Document Type
------------------

    id
    source_url
    destination_url
    state
    start_offset
    end_offset
    progress
    source_options
    destination_options

