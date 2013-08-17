import tempfile
import testtools
import os
import json
import webob

import staccato.db as db

TEST_CONF = """
[DEFAULT]

sql_connection = %(sql_connection)s
db_auto_create = True
log_level = DEBUG
protocol_policy = %(protocol_policy)s
"""

FILE_ONLY_PROTOCOL = {
    "file": [{"module": "staccato.protocols.file.FileProtocol"}]
}


class BaseTestCase(testtools.TestCase):
    pass


class TempFileCleanupBaseTest(BaseTestCase):

    def setUp(self):
        super(TempFileCleanupBaseTest, self).setUp()
        self.files_to_delete = []

    def make_db(self, conf):
        return db.StaccatoDB(conf)

    def make_confile(self, d, protocol_policy=None):
        conf_file = self.get_tempfile()

        if protocol_policy is not None:
            protocol_policy_file = self.get_tempfile()
            f = open(protocol_policy_file, 'w')
            json.dump(protocol_policy, f)
            f.close()
            d.update({'protocol_policy': protocol_policy_file})

        out_conf = TEST_CONF % d
        fout = open(conf_file, 'w')
        fout.write(out_conf)
        fout.close()

        return conf_file

    def tearDown(self):
        super(TempFileCleanupBaseTest, self).tearDown()
        for f in self.files_to_delete:
            try:
                pass
                os.remove(f)
            except:
                pass

    def get_tempfile(self):
        fname = tempfile.mkstemp()[1]
        self.files_to_delete.append(fname)
        return fname

    def get_tempdir(self):
        return tempfile.mkdtemp()


class Httplib2WsgiAdapter(object):
    def __init__(self, app):
        self.app = app

    def request(self, uri, method="GET", body=None, headers=None):
        req = webob.Request.blank(uri, method=method, headers=headers)
        req.body = body
        resp = req.get_response(self.app)
        return Httplib2WebobResponse(resp), resp.body


class Httplib2WebobResponse(object):
    def __init__(self, webob_resp):
        self.webob_resp = webob_resp

    @property
    def status(self):
        return self.webob_resp.status_code

    def __getitem__(self, key):
        return self.webob_resp.headers[key]

    def get(self, key):
        return self.webob_resp.headers[key]


class HttplibWsgiAdapter(object):
    def __init__(self, app):
        self.app = app
        self.req = None

    def request(self, method, url, body=None, headers={}):
        self.req = webob.Request.blank(url, method=method, headers=headers)
        self.req.body = body

    def getresponse(self):
        response = self.req.get_response(self.app)
        return FakeHTTPResponse(response.status_code, response.headers,
                                response.body)
