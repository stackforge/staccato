import threading
import urlparse

from staccato import db
from staccato.common import utils
from staccato.xfer import constants
import staccato.xfer.utils as xfer_utils


def do_transfer(CONF, xfer_id, state_machine):
    """
    This function does a transfer.  It will create its own DB.  This should be
    run in its own thread.
    """
    db_con = db.StaccatoDB(CONF)
    try:
        request = db_con.lookup_xfer_request_by_id(xfer_id)

        checkpointer = xfer_utils.XferCheckpointer(request, {}, db_con)
        monitor = xfer_utils.XferReadMonitor(db_con, request.id)

        src_module = utils.load_protocol_module(request.src_module_name, CONF)
        dst_module = utils.load_protocol_module(request.dst_module_name, CONF)

        dsturl_parts = urlparse.urlparse(request.dsturl)
        writer = dst_module.get_writer(dsturl_parts,
                                        checkpointer=checkpointer)

        # it is up to the reader/writer to put on the bw limits
        srcurl_parts = urlparse.urlparse(request.srcurl)
        reader = src_module.get_reader(srcurl_parts,
                                       writer,
                                       monitor,
                                       request.next_ndx,
                                       request.end_ndx)

        reader.process()
    except Exception, ex:
        state_machine.event_occurred(constants.Events.EVENT_ERROR,
                                    exception=ex,
                                    conf=CONF,
                                    xfer_request=request,
                                    db=db_con)
        raise
    finally:
        state_machine.event_occurred(constants.Events.EVENT_COMPLETE,
                                   conf=CONF,
                                   xfer_request=request,
                                   db=db_con)


class SimpleThreadExecutor(threading.Thread):

    def __init__(self, xfer_id, conf, state_machine):
        super(SimpleThreadExecutor, self).__init__()
        self.conf = conf
        self.xfer_id = xfer_id
        self.state_machine = state_machine
        self.start()

    def run(self):
        do_transfer(self.conf, self.xfer_id, self.state_machine)
