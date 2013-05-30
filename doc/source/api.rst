Stacatto REST API
=================

This document describes the current v1 Staccatto REST API

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

