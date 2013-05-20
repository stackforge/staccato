import json
import logging
import urlparse

import routes
from webob.exc import (HTTPError,
                       HTTPNotFound,
                       HTTPConflict,
                       HTTPBadRequest,
                       HTTPForbidden,
                       HTTPRequestEntityTooLarge,
                       HTTPInternalServerError,
                       HTTPServiceUnavailable)

import staccato.openstack.common.wsgi as os_wsgi
import staccato.openstack.common.middleware.context as os_context
import staccato.xfer.executor as executor
import staccato.xfer.events as xfer_events
from staccato import db
from staccato.xfer.constants import Events
from staccato.common import config, exceptions
from staccato.common import utils



class UnauthTestMiddleware(os_context.ContextMiddleware):
    def __init__(self, app, options):
        self.options = options
        super(UnauthTestMiddleware, self).__init__(app, options)

    def process_request(self, req):
        req.context = self.make_context(is_admin=True,
                                        user='admin')
        req.context.owner = 'admin'


class XferController(object):

    def __init__(self, db_con, sm, conf):
        self.sm = sm
        self.db_con = db_con
        self.log = logging
        self.conf = conf

    def _xfer_from_db(self, xfer_id, request):
        try:
            return self.db_con.lookup_xfer_request_by_id(
                xfer_id, owner=request.context.owner)
        except exceptions.StaccatoNotFoundInDBException, db_ex:
            raise HTTPNotFound(explanation="No such ID %s" % xfer_id,
                               content_type="text/plain")

    def _to_state_machine(self, event, xfer_request, name):
        try:
            self.sm.event_occurred(event,
                                   xfer_request=xfer_request,
                                   db=self.db_con)
        except exceptions.StaccatoInvalidStateTransitionException, ex:
            msg = _('You cannot %s a transfer that is in the %s '
                    'state. %s' % (name, xfer_request.state, ex))
            self._log_request(logging.INFO, msg)
            raise HTTPBadRequest(explanation=msg,
                                 content_type="text/plain")

    def urlxfer(self, request, srcurl, dsturl, dstopts=None, srcopts=None,
                start_ndx=0, end_ndx=None):
        srcurl_parts = urlparse.urlparse(srcurl)
        dsturl_parts = urlparse.urlparse(dsturl)

        plugin_policy = config.get_protocol_policy(self.conf)
        src_module_name = utils.find_protocol_module_name(plugin_policy,
                                                          srcurl_parts)
        dst_module_name = utils.find_protocol_module_name(plugin_policy,
                                                          dsturl_parts)

        src_module = utils.load_protocol_module(src_module_name, self.conf)
        dst_module = utils.load_protocol_module(dst_module_name, self.conf)

        write_info = dst_module.new_write(dsturl_parts, dstopts)
        read_info = src_module.new_write(srcurl_parts, srcopts)

        db_con = db.StaccatoDB(self.conf)
        xfer = db_con.get_new_xfer(request.context.owner,
                                   srcurl,
                                   dsturl,
                                   src_module_name,
                                   dst_module_name,
                                   start_ndx=start_ndx,
                                   end_ndx=end_ndx,
                                   read_info=read_info,
                                   write_info=write_info)
        return xfer

    def status(self, request, xfer_id):
        xfer = self._xfer_from_db(xfer_id, request)
        return xfer

    def list(self, request, limit=None):
        return self.db_con.lookup_xfer_request_all(owner=request.context.owner)

    def _xfer_to_dict(self, x):
        d = {}
        d['id'] = x.id
        d['srcurl'] = x.srcurl
        d['dsturl'] = x.dsturl
        d['state'] = x.state
        d['progress'] = x.next_ndx
        return d

    def delete(self, request, xfer_id):
        xfer_request = self._xfer_from_db(xfer_id, request)
        self._to_state_machine(Events.EVENT_DELETE,
                               xfer_request,
                               'delete')

    def cancel(self, request, xfer_id):
        xfer_request = self._xfer_from_db(xfer_id, request)
        self._to_state_machine(Events.EVENT_CANCEL,
                               xfer_request,
                               'cancel')

    def _log_request(self, level, msg, ex=None):
        # reformat the exception with context, user info, etc
        if ex:
            self.log.exception(msg)
        self.log.log(level, msg)


class XferDeserializer(os_wsgi.RequestHeadersDeserializer):
    """Default request headers deserializer"""

    meta_string = 'x-xfer-'

    def _pullout_xxfers(self, request):
        d = {}
        for h in request.headers:
           if h.lower().startswith(self.meta_string):
                key = h[len(self.meta_string):].lower().replace("-", "_")
                val = request.headers[h]
                d[key] = val
        return d

    def default(self, request):
        return self._pullout_xxfers(request)


class XferSerializer(os_wsgi.DictSerializer):

    def serialize(self, data, action='default', *args):
        return super(XferSerializer, self).serialize(data, args[0])

    def status(self, data):
        return self._xfer_to_json(data)

    def cancel(self, data):
        return self._xfer_to_json(data)

    def delete(self, data):
        return self._xfer_to_json(data)

    def urlxfer(self, data):
        return self._xfer_to_json(data)

    def _xfer_to_json(self, data):
        x = data
        d = {}
        d['id'] = x.id
        d['srcurl'] = x.srcurl
        d['dsturl'] = x.dsturl
        d['state'] = x.state
        d['progress'] = x.next_ndx
        return json.dumps(d)

    def list(self, data):
        xfer_list = []
        for xfer in data:
            xfer_list.append(xfer.id)
        return json.dumps(xfer_list)


class API(os_wsgi.Router):

    def __init__(self, conf):

        self.conf = conf
        self.db_con = db.StaccatoDB(conf)

        self.executor = executor.SimpleThreadExecutor(self.conf)
        self.sm = xfer_events.XferStateMachine(self.executor)

        controller = XferController(self.db_con, self.sm, self.conf)
        mapper = routes.Mapper()

        deserializer = os_wsgi.RequestDeserializer(
            headers_deserializer=XferDeserializer())
        serializer = XferSerializer()
        sc = os_wsgi.Resource(controller,
                              deserializer=deserializer,
                              serializer=serializer)

        mapper.connect(None,
                       "/urlxfer",
                       controller=sc,
                       action="urlxfer")
        mapper.connect(None,
                       "/status/{xfer_id}",
                       controller=sc,
                       action="status")
        mapper.connect(None,
                       "/cancel/{xfer_id}",
                       controller=sc,
                       action="cancel")
        mapper.connect(None,
                       "/delete/{xfer_id}",
                       controller=sc,
                       action="delete")
        mapper.connect(None,
                       "/list",
                       controller=sc,
                       action="list")

        super(API, self).__init__(mapper)
