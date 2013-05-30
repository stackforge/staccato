import json
import logging
import urlparse

import routes
import webob
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

    def newtransfer(self, request, source_url, destination_url, owner,
                    source_options=None, destination_options=None,
                    start_offset=0, end_offset=None):
        srcurl_parts = urlparse.urlparse(source_url)
        dsturl_parts = urlparse.urlparse(destination_url)

        dstopts={}
        srcopts={}

        if source_options is not None:
            srcopts = source_options
        if destination_options is not None:
            dstopts = destination_options

        plugin_policy = config.get_protocol_policy(self.conf)
        src_module_name = utils.find_protocol_module_name(plugin_policy,
                                                          srcurl_parts)
        dst_module_name = utils.find_protocol_module_name(plugin_policy,
                                                          dsturl_parts)

        src_module = utils.load_protocol_module(src_module_name, self.conf)
        dst_module = utils.load_protocol_module(dst_module_name, self.conf)

        dstopts = dst_module.new_write(dsturl_parts, dstopts)
        srcopts = src_module.new_read(srcurl_parts, srcopts)

        db_con = db.StaccatoDB(self.conf)
        xfer = db_con.get_new_xfer(owner,
                                   source_url,
                                   destination_url,
                                   src_module_name,
                                   dst_module_name,
                                   start_ndx=start_offset,
                                   end_ndx=end_offset,
                                   source_opts=srcopts,
                                   dest_opts=dstopts)
        return xfer

    def status(self, request, xfer_id, owner):
        xfer = self._xfer_from_db(xfer_id, request)
        return xfer

    def list(self, request, owner):
        return self.db_con.lookup_xfer_request_all(owner=request.context.owner)

    def _xfer_to_dict(self, x):
        d = {}
        d['id'] = x.id
        d['srcurl'] = x.srcurl
        d['dsturl'] = x.dsturl
        d['state'] = x.state
        d['progress'] = x.next_ndx
        return d

    def delete(self, request, xfer_id, owner):
        xfer_request = self._xfer_from_db(xfer_id, request)
        self._to_state_machine(Events.EVENT_DELETE,
                               xfer_request,
                               'delete')

    def cancel(self, request, xfer_id, owner):
        xfer_request = self._xfer_from_db(xfer_id, request)
        self._to_state_machine(Events.EVENT_CANCEL,
                               xfer_request,
                               'cancel')

    def _log_request(self, level, msg, ex=None):
        # reformat the exception with context, user info, etc
        if ex:
            self.log.exception(msg)
        self.log.log(level, msg)

class XferHeaderDeserializer(os_wsgi.RequestHeadersDeserializer):
    def default(self, request):
        return {'owner': request.context.owner}

class XferDeserializer(os_wsgi.JSONDeserializer):
    """Default request headers deserializer"""

    def _validate(self, body, required, optional):
        body = self._from_json(body)
        request = {}
        for k in body:
            if k not in required and k not in optional:
                msg = '%s is an unknown option.' % k
                raise webob.exc.HTTPBadRequest(explanation=msg)
        for k in required:
            if k not in body:
                msg = 'The option %s must be specified.' % k
                raise webob.exc.HTTPBadRequest(explanation=msg)
            request[k] = body[k]
        for k in optional:
            if k in body:
                request[k] = body[k]
        return request

    def newtransfer(self, body):
        _required = ['source_url', 'destination_url']
        _optional = ['source_options', 'destination_options', 'start_offset',
                    'end_offset', ]
        request = self._validate(body, _required, _optional)
        return request

    def list(self, body):
        _required = []
        _optional = ['limit', 'next', 'filter',]
        request = self._validate(body, _required, _optional)
        return request

    def status(self, body):
        request = self._validate(body, [], [])
        return request

    def delete(self, body):
        request = self._validate(body, [], [])
        return request

    def cancel(self, body):
        request = self._validate(body, [], [])
        return request


class XferSerializer(os_wsgi.JSONDictSerializer):

    def serialize(self, data, action='default', *args):
        return super(XferSerializer, self).serialize(data, args[0])

    def status(self, data):
        return self._xfer_to_json(data)

    def cancel(self, data):
        return self._xfer_to_json(data)

    def delete(self, data):
        return self._xfer_to_json(data)

    def newtransfer(self, data):
        return self._xfer_to_json(data)

    def _xfer_to_json(self, data):
        x = data
        d = {}
        d['id'] = x.id
        d['source_url'] = x.srcurl
        d['destination_url'] = x.dsturl
        d['state'] = x.state
        d['start_offset'] = x.start_ndx
        d['end_offset'] = x.end_ndx
        d['progress'] = x.next_ndx
        d['source_options'] = x.source_opts
        d['destination_options'] = x.dest_opts
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

        body_deserializers = {'application/json': XferDeserializer()}
        deserializer = os_wsgi.RequestDeserializer(
            body_deserializers=body_deserializers,
            headers_deserializer=XferHeaderDeserializer())
        serializer = XferSerializer()
        transfer_resource = os_wsgi.Resource(controller,
                              deserializer=deserializer,
                              serializer=serializer)

        mapper.connect('/transfers',
                       controller=transfer_resource,
                       action='newtransfer',
                       conditions={'method': ['POST']})
        mapper.connect('/transfers',
                       controller=transfer_resource,
                       action='list',
                       conditions={'method': ['GET']})
        mapper.connect('/transfers/{xfer_id}',
                       controller=transfer_resource,
                       action='status',
                       conditions={'method': ['GET']})
        mapper.connect('/transfers/{xfer_id}',
                       controller=transfer_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})
        mapper.connect('/transfers/{xfer_id}/action',
                       controller=transfer_resource,
                       action='action',
                       conditions={'method': ['POST']})

        super(API, self).__init__(mapper)
