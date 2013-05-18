import json
import urlparse

import routes

import staccato.openstack.common.wsgi as os_wsgi
import staccato.xfer.executor as executor
import staccato.xfer.events as xfer_events
from staccato import db
from staccato.xfer.constants import Events
from staccato.common import config
from staccato.common import utils


class XferController(object):

    def __init__(self, conf, sm):
        self.sm = sm
        self.conf = conf
        self.db_con = db.StaccatoDB(conf)

    def _xfer_from_db(self, xfer_id):
        return self.db_con.lookup_xfer_request_by_id(xfer_id)

    def _to_state_machine(self, event, xfer_request):
        self.sm.event_occurred(event,
                               conf=self.conf,
                               xfer_request=xfer_request,
                               db=self.db_con)

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
        xfer = db_con.get_new_xfer(srcurl,
                                   dsturl,
                                   src_module_name,
                                   dst_module_name,
                                   start_ndx=start_ndx,
                                   end_ndx=end_ndx,
                                   read_info=read_info,
                                   write_info=write_info)
        return xfer

    def status(self, request, xfer_id):
        xfer = self._xfer_from_db(xfer_id)
        return self._xfer_to_dict(xfer)

    def _xfer_to_dict(self, x):
        d = {}
        d['id'] = x.id
        d['srcurl'] = x.srcurl
        d['dsturl'] = x.dsturl
        d['state'] = x.state
        d['progress'] = x.next_ndx
        return d

    def delete(self, request, xfer_id):
        xfer_request = self._xfer_from_db(xfer_id)
        self._to_state_machine(Events.EVENT_DELETE, xfer_request)

    def cancel(self, request, xfer_id):
        xfer_request = self._xfer_from_db(xfer_id)
        self._to_state_machine(Events.EVENT_CANCEL, xfer_request)


class LDeserial(os_wsgi.RequestHeadersDeserializer):
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


class LSerial(os_wsgi.DictSerializer):

    def serialize(self, data, action='default', *args):
        return super(LSerial, self).serialize(data, args[0])

    def urlxfer(self, data):
        x = data
        d = {}
        d['id'] = x.id
        d['srcurl'] = x.srcurl
        d['dsturl'] = x.dsturl
        d['state'] = x.state
        d['progress'] = x.next_ndx
        return json.dumps(d)

class API(os_wsgi.Router):

    def __init__(self, conf):

        self.conf = conf
        self.executor = executor.SimpleThreadExecutor(self.conf)
        self.sm = xfer_events.XferStateMachine(self.executor)

        controller = XferController(self.conf, self.sm)
        mapper = routes.Mapper()

        deserializer = os_wsgi.RequestDeserializer(
            headers_deserializer=LDeserial())
        serializer = LSerial()
        sc = os_wsgi.Resource(controller,
                              deserializer=deserializer,
                              serializer=serializer)

        mapper.connect(None, "/urlxfer", controller=sc, action="urlxfer")
        mapper.connect(None, "/status", controller=sc, action="status")

        # Actions are all implicitly defined
        #mapper.resource("server", "servers", controller=controller)

        super(API, self).__init__(mapper)
