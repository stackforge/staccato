
Welcome to Staccato's documentation!
====================================

The Staccato project provides a service for transferring data (most
commonly the data transferred are VM images) from a source end point
to a destination end point.  Staccato is does not manage or control
the storage of that data, it interacts with other services (swift,
glance, file systems, etc) which handle that.  Staccato's only job
is to manage the actual transfer of the data from one storage system
to another.  Below are a few of the tasks needed to accomplish that job:

* Monitor the progress of a transfer and restart it when needed.
* Negotiate the best possible protocol (for example bittorrent for 
  multicast).
* Manage resource (NIC, disk I/O, etc) and protect them from overheating.
* Verify data integrity and security of the bytes in flight.

Staccato is as a service that does a upload or download of an image on 
behalf of a client.  The client can issue a single, short lived request 
to move an image.  Unlike traditional upload/downloads the client does 
not have to live for the length of the transfer marshaling the protocol 
de jour for every single byte.  Instead it issues a request and then 
ends. Later it can check back in with the service to determine progress.  
Staccato does the work of protocol negotiation and optimal parameter 
setting, scheduling the transfer, error recovery, and much more.

Contents
============

.. toctree::
   :maxdepth: 1

   quickstart
   architecture
   need
   api
