import json
import testtools

from staccato.tests import utils
import staccato.api.v1.xfer as v1_xfer

import webob.exc

class TestDeserializer(utils.TempFileCleanupBaseTest):

    def test_delete(self):
        xd = v1_xfer.XferDeserializer()
        results = xd.delete('{}')
        self.assertEqual(results, {})

    def test_new_transfer_good_required(self):
        xd = v1_xfer.XferDeserializer()
        body_json= {"source_url": "file://", "destination_url": "file:///"}
        body = json.dumps(body_json)
        results = xd.newtransfer(body)
        self.assertEqual(results, body_json)

    def test_new_transfer_good_options(self):
        xd = v1_xfer.XferDeserializer()
        body_json= {"source_url": "file://",
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
        body_json= {"source_url": "file://"}
        body = json.dumps(body_json)
        self.assertRaises(webob.exc.HTTPBadRequest,
                          xd.newtransfer,
                          body)

    def test_new_transfer_bad_option(self):
        xd = v1_xfer.XferDeserializer()
        body_json= {"source_url": "file://",
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