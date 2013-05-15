

class SimpleCountSchedler(object):

    def __init__(self, db_obj, max_at_once=4):
        self.max_at_once = max_at_once
        self.db_obj = db_obj
        self.running = 0

    def _new_transfer(self, request):
        self.running += 1
        # todo start the transfer

    def _transfer_complete(self):
        self.running -= 1

    def _check_for_transfers(self):
        avail = self.max_at_once - self.running
        xfer_request_ready = self.db_obj.get_all_ready(limit=avail)
        for request in xfer_request_ready:
            self._new_transfer(request)

    def poll(self):
        self._check_for_transfers()
