
Only One Executor At A Time
===========================

It is important that only 1 process is ever working on a transfer at a time.
It is further important that no one transfer is stalled out because the
executor that began it failed part of the way through.  This document describes
the plan to achieve this.

The Problem
-----------

Say that Staccato is configured with multiple executors.  Partially through
a transfer one of the executors fails, however the other executor is running
perfectly well.  We need something to detect that the transfer which was
running (and which is still in the running state) is no longer active and
needs to be placed back into a pending state (NEW or ERROR at the time of
this writing).  Once placed in such a state it will be active for scheduling
again.

We also want to avoid the situation where there are two executors and they
both select the same transfer and thus work is redundantly done.  This could
happen via a race, or it could happen when it appears that an executor has
died but in reality it is (or will soon be) transferring data.

Redundant Transfer
------------------

At the time of this writing staccato does allow for the possibility of
redundant transfers.  The contract with the user is that some (or all)
of the data set may be transfers twice.  This contract is there to release
the staccato implementation and architecture from complicated and slow
inter-process locking mechanisms which would needed to avoid every single
case.  However, this contract is not there to allow staccato to entirely
ignore the problem.  Redundant transfers are unwelcome because they use
resource.  By the very nature of this problem, redudnant transfer will only
happen when the system is unaware of all but one of the unneeded transfers
(if we know about them, we would kill them) thus staccato cannot properly
manage the resources.

Solution
--------

Each executor will be associated with a UUID that lives in the process space
of that executor (it is not written to the database).  Each row in the database
represents a requested transfer.  When the state column in that row moves to
RUNNING the executor ID will be recorded in another column in that row.  As
the executor is performing a transfer it periodically checks the row on which
it is working to verify that its UUID is still the one in the database.  If it
is not, it must immediately terminate its workload without making any further
updates to the database.  The time window in which it checks the database is
configurable and will define the window of possibility for redundant transfers.

The executor UUID will be some combination of hostname and pid.  This will make
it easier for an operator to determine what is happening.

Clean Up
~~~~~~~~

We also need to determine if a transfer is marked as running, but the executor
has unexpectedly died.  In order to determine this we will look at the
'updated_at' time stamp that is associated with every transfer row.  If the
row has not been updated in N times the configurable update window then
staccato assumes that the executor is dead, it clears the executor UUID from
the row, and moves the transfer back to a pending state.


