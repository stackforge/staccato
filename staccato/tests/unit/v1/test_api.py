import json
import mox
import uuid

import webob.exc

from staccato.tests import utils
import staccato.api.v1.xfer as v1_xfer
import staccato.db.models as db_models
import staccato.xfer.constants as constants
import staccato.common.config as config


def _make_xfer_request():
    x = db_models.XferRequest()
    x.id = str(uuid.uuid4())
    x.state = constants.States.STATE_RUNNING
    x.srcurl = "http://%s.com/path" % str(uuid.uuid4())
    x.dsturl = "file://%s.com/path" % str(uuid.uuid4())
    x.start_ndx = 0
    x.end_ndx = 150
    x.source_opts = {'somevalue': str(uuid.uuid4())}
    x.dest_opts = {'destvalue': str(uuid.uuid4())}
    return x


class TestDeserializer(utils.TempFileCleanupBaseTest):

    def test_new_transfer_good_required(self):
        xd = v1_xfer.XferDeserializer()
        body_json = {"source_url": "file://", "destination_url": "file:///"}
        body = json.dumps(body_json)
        results = xd.newtransfer(body)
        self.assertEqual(results, body_json)

    def test_new_transfer_good_options(self):
        xd = v1_xfer.XferDeserializer()
        body_json = {"source_url": "file://",
                     "destination_url": "file:///",
                     "source_options": {'hello': 'world'},
                     "start_offset": 10,
                     "end_offset": 100,
                     "destination_options": {}}
        body = json.dumps(body_json)
        results = xd.newtransfer(body)
        self.assertEqual(results, body_json)

    def test_new_transfer_missing_required(self):
        xd = v1_xfer.XferDeserializer()
        body_json = {"source_url": "file://"}
        body = json.dumps(body_json)
        self.assertRaises(webob.exc.HTTPBadRequest,
                          xd.newtransfer,
                          body)

    def test_new_transfer_bad_option(self):
        xd = v1_xfer.XferDeserializer()
        body_json = {"source_url": "file://",
                     "destination_url": "file:///",
                     "not_good": 10},
        body = json.dumps(body_json)
        self.assertRaises(webob.exc.HTTPBadRequest,
                          xd.newtransfer,
                          body)

    def test_default(self):
        xd = v1_xfer.XferDeserializer()
        results = xd.default('{}')
        self.assertEqual(results, {'body': {}})

    def test_xferaction(self):
        xd = v1_xfer.XferDeserializer()
        body_json = {"xferaction": "cancel"}
        body = json.dumps(body_json)
        results = xd.xferaction(body)
        self.assertEqual(results, body_json)

    def test_bad_xferaction(self):
        xd = v1_xfer.XferDeserializer()
        body_json = {"xferaction": "notreal"}
        body = json.dumps(body_json)
        self.assertRaises(webob.exc.HTTPBadRequest,
                          xd.xferaction,
                          body)


class TestSerializer(utils.TempFileCleanupBaseTest):

    def setUp(self):
        super(TestSerializer, self).setUp()
        self.serializer = v1_xfer.XferSerializer()

    def _check_xfer(self, xfer, d):
        self.assertEqual(xfer.id, d['id'])
        self.assertEqual(xfer.srcurl, d['source_url'])
        self.assertEqual(xfer.dsturl, d['destination_url'])
        self.assertEqual(xfer.state, d['state'])
        self.assertEqual(xfer.start_ndx, d['start_offset'])
        self.assertEqual(xfer.end_ndx, d['end_offset'])
        self.assertEqual(xfer.source_opts, d['source_options'])
        self.assertEqual(xfer.dest_opts, d['destination_options'])

    def test_default(self):
        x = _make_xfer_request()
        ds = self.serializer.default(x)
        d = json.loads(ds)
        self._check_xfer(x, d)

    def test_list(self):
        x1 = _make_xfer_request()
        x2 = _make_xfer_request()
        x3 = _make_xfer_request()
        x4 = _make_xfer_request()
        xfer_list = [x1, x2, x3, x4]
        lookup = {}
        for x in xfer_list:
            lookup[x.id] = x
        result_str = self.serializer.list(xfer_list)
        result_list = json.loads(result_str)
        for x_d in result_list:
            x = lookup[x_d['id']]
            self._check_xfer(x, x_d)


class TestController(utils.TempFileCleanupBaseTest):

    def setUp(self):
        super(TestController, self).setUp()
        self.mox = mox.Mox()
        self.sm = self.mox.CreateMockAnything()
        self.db = self.mox.CreateMockAnything()
        self.request = self.mox.CreateMockAnything()
        self.conf = config.get_config_object(args=[])
        self.controller = v1_xfer.XferController(self.db, self.sm, self.conf)

    def tearDown(self):
        super(TestController, self).tearDown()
        self.mox.UnsetStubs()

    def test_status(self):
        xfer = _make_xfer_request()

        self.db.lookup_xfer_request_by_id(
            xfer.id, owner='admin').AndReturn(xfer)

        self.mox.ReplayAll()
        result = self.controller.status(self.request, xfer.id, 'admin')
        self.mox.VerifyAll()
        self.assertEqual(result, xfer)

    def test_status(self):
        xfer = _make_xfer_request()

        self.db.lookup_xfer_request_by_id(
            xfer.id, owner='admin').AndReturn(xfer)

        self.mox.ReplayAll()
        result = self.controller.status(self.request, xfer.id, 'admin')
        self.mox.VerifyAll()
        self.assertEqual(result, xfer)

    def test_delete(self):
        xfer = _make_xfer_request()

        self.db.lookup_xfer_request_by_id(
            xfer.id, owner='admin').AndReturn(xfer)
        self.sm.event_occurred(constants.Events.EVENT_DELETE,
                               xfer_request=xfer,
                               db=self.db)
        self.mox.ReplayAll()
        self.controller.delete(self.request, xfer.id, 'admin')
        self.mox.VerifyAll()

    def test_new_request(self):
        xfer = _make_xfer_request()
        xfer.srcurl = "http://someplace.com"
        xfer.dsturl = "file://path/to/no/where"

        self.mox.StubOutWithMock(config, 'get_protocol_policy')

        config.get_protocol_policy(self.conf).AndReturn(
            {
                "file": [{"module": "staccato.protocols.file.FileProtocol"}],
                "http": [{"module": "staccato.protocols.http.HttpProtocol"}]
            })

        self.db.get_new_xfer('admin',
                             xfer.srcurl,
                             xfer.dsturl,
                             "staccato.protocols.http.HttpProtocol",
                             "staccato.protocols.file.FileProtocol",
                             start_ndx=0,
                             end_ndx=None,
                             source_opts={},
                             dest_opts={}).AndReturn(xfer)
        self.mox.ReplayAll()
        res = self.controller.newtransfer(self.request, xfer.srcurl,
                                          xfer.dsturl, 'admin')
        self.mox.VerifyAll()
        self.assertEqual(res, xfer)
