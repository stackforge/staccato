import json
import testtools
import uuid

from staccato.tests import utils
import staccato.api.v1.xfer as v1_xfer
import staccato.db.models as db_models
import staccato.xfer.constants as constants

import webob.exc


class TestDeserializer(utils.TempFileCleanupBaseTest):

    def test_delete(self):
        xd = v1_xfer.XferDeserializer()
        results = xd.delete('{}')
        self.assertEqual(results, {})

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

    def test_delete(self):
        xd = v1_xfer.XferDeserializer()
        results = xd.delete('{}')
        self.assertEqual(results, {})

    def test_status(self):
        xd = v1_xfer.XferDeserializer()
        results = xd.status('{}')
        self.assertEqual(results, {})

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

    def _make_xfer_request(self):
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

    def test_default(self):
        x = self._make_xfer_request()
        ds = self.serializer.default(x)
        d = json.loads(ds)
        self._check_xfer(x, d)

    def test_list(self):
        x1 = self._make_xfer_request()
        x2 = self._make_xfer_request()
        x3 = self._make_xfer_request()
        x4 = self._make_xfer_request()
        xfer_list = [x1, x2, x3, x4]
        lookup = {}
        for x in xfer_list:
            lookup[x.id] = x
        result_str = self.serializer.list(xfer_list)
        result_list = json.loads(result_str)
        for x_d in result_list:
            x = lookup[x_d['id']]
            self._check_xfer(x, x_d)
