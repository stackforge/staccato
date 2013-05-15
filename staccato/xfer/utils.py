import datetime

import staccato.xfer.constants as constants
import staccato.common.exceptions as exceptions


def _merge_one(blocks):

    if not blocks:
        return blocks.copy()
    merge = True
    while merge:
        new = {}
        merge = False
        keys = sorted(blocks.keys())
        ndx = 0
        current_key = keys[ndx]
        new[current_key] = blocks[current_key]
        ndx = ndx + 1

        while ndx < len(keys):
            next_key = keys[ndx]
            start_i = current_key
            start_j = next_key

            end_i = blocks[start_i]
            end_j = blocks[start_j]

            if end_i >= start_j:
                merge = True
                new[start_i] = max(end_i, end_j)
                #ndx = ndx + 1
            else:
                new[start_j] = end_j
                current_key = next_key

            ndx = ndx + 1
        blocks = new
    return new


class XferDBUpdater(object):

    def __init__(self, db_refresh_rate=5):
        self.db_refresh_rate = db_refresh_rate
        self._set_time()

    def _set_time(self):
        self.next_time = datetime.datetime.now() +\
            datetime.timedelta(seconds=self.db_refresh_rate)

    def _check_db_ready(self):
        n = datetime.datetime.now()
        if n > self.next_time:
            self._set_time()
            self._do_db_operation()


class XferReadMonitor(XferDBUpdater):

    def __init__(self, db, xfer_id, db_refresh_rate=5):
        super(XferReadMonitor, self).__init__(db_refresh_rate=db_refresh_rate)
        self.db = db
        self.done = True  # TODO base this on xfer_request
        self.xfer_id = xfer_id
        self._do_db_operation()

    def _do_db_operation(self):
        self.request = self.db.lookup_xfer_request_by_id(self.xfer_id)

    def is_done(self):
        self._check_db_ready()
        return constants.is_state_done_running(self.request.state)


class XferCheckpointer(XferDBUpdater):
    """
    This class is used by protocol plugins to keep track of the progress of
    a transfer.  With each write the plugin can call update() and the blocks
    will be tracked.  When the protocol plugin has safely synced some data
    to disk it can call sync().  Each call to sync may cause a write to the
    database.

    This class will help write side connections keep track fo their workload
    """
    def __init__(self, xfer_request, protocol_doc, db, db_refresh_rate=5):
        """
        :param xfer_id: The transfer ID to be tracked.
        :protocol doc: protocol specific information for tracking.  This
                       should be a dict
        """
        super(XferCheckpointer, self).__init__(db_refresh_rate=db_refresh_rate)
        self.blocks = {}
        self.db = db
        self.protocol_doc = protocol_doc
        self.xfer_request = xfer_request
        self.update(0, 0)

    def update(self, block_start, block_end):
        """
        :param block_start: the start of the block.
        :param block_end: the end of the block.
        """
        if block_end < block_start:
            raise exceptions.StaccatoParameterError()

        if block_start in self.blocks:
            self.blocks[block_start] = max(self.blocks[block_start], block_end)
        else:
            self.blocks[block_start] = block_end

        self.blocks = _merge_one(self.blocks)

    def _do_db_operation(self):
        keys = sorted(self.blocks.keys())
        self.xfer_request.next_ndx = self.blocks[keys[0]]
        self.db.save_db_obj(self.xfer_request)

    def sync(self, protocol_doc):
        """
        :param protocol_doc: A update to the protocol specific information
                             sent in by the protocol module.  This will be
                             merged with the last dict sent in.
        """
        # take the first from the list and only sync that far.
        self.protocol_doc.update(protocol_doc)
        self._check_db_ready()
