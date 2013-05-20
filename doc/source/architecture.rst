
Stacatto Architecture
=====================

This document describes the basic internal architecture of the Staccato 
system.

REST API
--------

The user facing service is a REST API implemented using WSGI.  A 
reference runner is provided with this distribution but it is also 
possible to run it using other WSGI containers like apache2+mod_wsgi and 
cherrypy.  The REST service is assembled using paste deploy

This comment takes uses requests, validates them, and then interacts 
with the database.  For new transfer requests it adds information to the 
DB about what the user has requested.  For cancels, deletes, or any 
other update the associate request is looked up in the database and 
updated. For lists or status requests the associated transfer requests 
(or set of transfer requests) is pulled out of the database and the 
relevant information is returned to the user according to the defined 
protocol.

The REST API process does no further work.  It simply vets a client and 
its request and then translates the information between the user and the 
database where the worker processes can consume it.

Scheduler
---------

The scheduler is responsible for deciding when a transfer request is 
ready to be executed.  When one is selected as ready its corresponding 
database entry will be marked.  The scheduler does no further work.

Because it is likely that various different scheduling techniques will 
evolve over time and that different deployments will require different 
scheduler, this is implemented in a plug-in fashion. The first and most 
basic scheduler will be one that allows N transfer to happen at one 
time.

Executor
--------

The executor is the process that handles the actual transfer of data.  
It connects to the database and looks for entries that the scheduler has 
marked as *ready*.  It then examines the request and opens up the 
protocol module needed for the source and the protocol module needed for 
the destination. Connections are formed and the data is routed from the 
source to the destination.  As the transfer progresses updates are 
written to the database. In this way if a transfer fails part of the way 
through it can be restarted from the last known point of progress that 
was recorded in the database.

Protocol Plugins
----------------

The implementation of each protocol that Staccato can speak is 
abstracted away into protocol modules.  This will allow maximal code 
reuse and ease of protocol creation.  Also, it will allow future 
developers to easily create protocols without having to make them part 
of the Staccato distribution.

For the sake of clarity we offer one simple and common use case.  When 
nova-compute does an boot of an instance it downloads an image from 
Glance. When using Staccato the source protocol module would be a 
*Glance* plugin and the destination protocol module would be a *file 
system* plugin.
