import urlparse

from staccato.common import utils, config
from staccato import db
from staccato.xfer.constants import Events
from staccato.xfer import events


def xfer_new(CONF, srcurl, dsturl, src_opts, dst_opts, start_ndx=0,
                 end_ndx=None):
    srcurl_parts = urlparse.urlparse(srcurl)
    dsturl_parts = urlparse.urlparse(dsturl)

    plugin_policy = config.get_protocol_policy(CONF)
    src_module_name = utils.find_protocol_module_name(plugin_policy,
                                                      srcurl_parts)
    dst_module_name = utils.find_protocol_module_name(plugin_policy,
                                                      dsturl_parts)

    src_module = utils.load_protocol_module(src_module_name, CONF)
    dst_module = utils.load_protocol_module(dst_module_name, CONF)

    write_info = dst_module.new_write(dsturl_parts, dst_opts)
    read_info = src_module.new_write(srcurl_parts, src_opts)

    db_con = db.StaccatoDB(CONF)
    xfer = db_con.get_new_xfer(srcurl,
                               dsturl,
                               src_module_name,
                               dst_module_name,
                               start_ndx=start_ndx,
                               end_ndx=end_ndx,
                               read_info=read_info,
                               write_info=write_info)
    return xfer


def xfer_start(conf, xfer_id):
    db_con = db.StaccatoDB(conf)
    request = db_con.lookup_xfer_request_by_id(xfer_id)
    events.g_my_states.event_occurred(Events.EVENT_START,
                                      conf=conf,
                                      xfer_request=request,
                                      db=db_con)


def xfer_cancel(conf, xfer_id):
    db_con = db.StaccatoDB(conf)
    request = db_con.lookup_xfer_request_by_id(xfer_id)
    events.g_my_states.event_occurred(Events.EVENT_CANCEL,
                                      conf=conf,
                                      xfer_request=request,
                                      db=db_con)


def xfer_delete(conf, xfer_id):
    db_con = db.StaccatoDB(conf)
    request = db_con.lookup_xfer_request_by_id(xfer_id)
    events.g_my_states.event_occurred(Events.EVENT_DELETE,
                                      conf=conf,
                                      xfer_request=request,
                                      db=db_con)
