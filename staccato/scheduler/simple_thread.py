import time

import staccato.openstack.common.service as os_service
import staccato.xfer.events as s_events
import staccato.xfer.executor as s_executor
import staccato.xfer.constants as s_constants
from  staccato.xfer.constants import Events
import staccato.db as s_db


class SimpleCountSchedler(os_service.Service):

    def __init__(self, conf):
        super(SimpleCountSchedler, self).__init__()
        self.max_at_once = 1
        self.db_obj = s_db.StaccatoDB(conf)
        self.executor = s_executor.SimpleThreadExecutor(conf) # todo, pull from conf
        self.state_machine = s_events.XferStateMachine(self.executor)
        self.running = 0
        self.done = False
        self._started_ids = []

    def _poll_db(self):
        while not self.done:
            time.sleep(1)
            self._check_for_transfers()

    def _new_transfer(self, request):
        self.running += 1
        self._started_ids.append(request.id)
        self.state_machine.event_occurred(Events.EVENT_START,
                                   xfer_request=request,
                                   db=self.db_obj)

    def _transfer_complete(self):
        self.running -= 1

    def _check_for_transfers(self):
        requests = self.db_obj.get_xfer_requests(self._started_ids)
        for r in requests:
            if s_constants.is_state_done_running(r.state) :
                self._started_ids.remove(r.id)
        avail = self.max_at_once - len(self._started_ids)
        xfer_request_ready = self.db_obj.get_all_ready(limit=avail)
        for request in xfer_request_ready:
            self._new_transfer(request)

    def start(self):
        self.tg.add_thread(self._poll_db)
