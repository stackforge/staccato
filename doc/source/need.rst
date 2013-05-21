
The Need For Staccato
=====================

In this document we describe why a transfer service like Staccato is 
needed.  This need breaks down into three major areas:

Robustness
Efficiency
Workload

Robust Transfers
----------------

Data transfers fail.  Transmitting large amount of data can be 
expensive. Ideally transfers are check pointed along the way so that 
when the inevitable failure occurs, the transfer can be restarted from 
the last known checkpoint thus minimizing the redundant data that is 
sent.

Unfortunately performing such check-pointing is non trivial.  The 
information needs to be consistently stored in a way that will survive 
the termination of both source and destination transfer endpoints. 
Locking mechanisms and consistency measures must be in place to be 
certain that only one transfer takes place at a time. Certain protocols 
do not allow for partial transfer in which case a cache is needed to 
minimize the potential of transmission.

There are many more complications that make the job of monitoring a 
transfer difficult.  Rather than trying to embed all of the needed 
complicated logic into a traditional client, this is the kind of thing 
best implemented with a service.

Efficient Transfers
-------------------

Commonly the protocol used for data transfer is defined by the storage 
system in which the source data lives.  This is not always the best 
choice, and it conflates the concepts of an access protocol and a 
transfer protocol.  Often times the best protocol to use is determined 
not only by the architecture and workload of the source storage system, 
but also that of the destination as well as that of the network.

A service like Staccato is in a architectural position to know more 
about what is happening on all three of these components, the source 
storage system, the destination storage system, and the network. It can 
avoid thrashing and overheating of resources by scheduling transfers at 
optimal times, select optimal protocols (think of bittorrent when a 
single source is requested for download to many destinations), and 
setting more optimal parameters on protocols for the transfer at hand 
(think of TCP buffer sizes).

Having this knowledge and functionality in a traditional client would be 
overly complicated it not impossible.

Workload
--------

Clients often wish to do download a data set to a local file, or upload a 
local file to a more well managed storage system.  Such clients are the 
target users for this service.  As it commonly stands today clients 
download files by connecting to a remote storage system by speaking its 
protocol and marshaling ever byte of that protocol (including security 
signing and other potentially processor intensive work).  The workload 
put upon the client scales with the size of the image and the protocol 
in use.  Rarely does the client plan its resources and time outs around 
these things.  In these case the client really just wants file, it 
doesn't want to do the work or contribute the resources (CPU, NIC, 
memory) to do it.

Because of this a service that offloads this burden makes sense.
