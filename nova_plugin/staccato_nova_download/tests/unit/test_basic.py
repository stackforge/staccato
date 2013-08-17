import httplib
import json
import urlparse

import mox
from nova import exception
from oslo.config import cfg

from staccato.common import config
import staccato_nova_download

import staccato_nova_download.tests.base as base


CONF = cfg.CONF

CONF.import_opt('auth_strategy', 'nova.api.auth')


class TestBasic(base.BaseTest):

    def setUp(self):
        super(TestBasic, self).setUp()
        self.mox = mox.Mox()

    def tearDown(self):
        super(TestBasic, self).tearDown()
        self.mox.UnsetStubs()

    def test_get_schemes(self):
        start_protocols = ["file", "http", "somethingelse"]
        version_info_back = {'protocols': start_protocols}
        self.mox.StubOutClassWithMocks(httplib, 'HTTPConnection')
        http_obj = httplib.HTTPConnection('127.0.0.1', 5309)
        response = self.mox.CreateMockAnything()
        http_obj.request('GET', '/').AndReturn(response)
        response.read().AndReturn(json.dumps(version_info_back))

        self.mox.ReplayAll()
        protocols = staccato_nova_download.get_schemes()
        self.mox.VerifyAll()
        self.assertEqual(start_protocols, protocols)

    def test_get_schemes_failed_connection(self):
        start_protocols = ["file", "http", "somethingelse"]
        self.mox.StubOutClassWithMocks(httplib, 'HTTPConnection')
        http_obj = httplib.HTTPConnection('127.0.0.1', 5309)
        http_obj.request('GET', '/').AndRaise(Exception("message"))

        self.mox.ReplayAll()
        self.assertRaises(exception.ImageDownloadModuleError,
                          staccato_nova_download.get_schemes)
        self.mox.VerifyAll()

    def test_successfull_download(self):
        class FakeResponse(object):
            def __init__(self, status, reply):
                self.status = status
                self.reply = reply

            def read(self):
                return json.dumps(self.reply)

        self.config(auth_strategy='notkeystone')

        xfer_id = 'someidstring'
        src_url = 'file:///etc/group'
        dst_url = 'file:///tmp/group'
        data = {'source_url': src_url, 'destination_url': dst_url}

        headers = {'Content-Type': 'application/json'}

        self.mox.StubOutClassWithMocks(httplib, 'HTTPConnection')
        http_obj = httplib.HTTPConnection('127.0.0.1', 5309)

        http_obj.request('POST', '/v1/transfers',
                         headers=headers, body=data)
        http_obj.getresponse().AndReturn(FakeResponse(201, {'id': xfer_id}))

        path = '/v1/transfers/%s' % xfer_id
        http_obj.request('GET', path, headers=headers)
        http_obj.getresponse().AndReturn(
            FakeResponse(200, {'status': 'STATE_COMPLETE'}))

        self.mox.ReplayAll()
        st_plugin = staccato_nova_download.StaccatoTransfer()

        url_parts = urlparse.urlparse(src_url)
        dst_url_parts = urlparse.urlparse(dst_url)
        st_plugin.download(url_parts, dst_url_parts.path, {})
        self.mox.VerifyAll()

    def test_successful_download_with_keystone(self):
        class FakeContext(object):
            auth_token = 'sdfsdf'
            user = 'buzztroll'
            tenant = 'staccato'

        class FakeResponse(object):
            def __init__(self, status, reply):
                self.status = status
                self.reply = reply

            def read(self):
                return json.dumps(self.reply)

        self.config(auth_strategy='keystone')

        xfer_id = 'someidstring'
        src_url = 'file:///etc/group'
        dst_url = 'file:///tmp/group'
        data = {'source_url': src_url, 'destination_url': dst_url}

        context = FakeContext()
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': context.auth_token,
                   'X-User-Id': context.user,
                   'X-Tenant-Id': context.tenant}

        self.mox.StubOutClassWithMocks(httplib, 'HTTPConnection')
        http_obj = httplib.HTTPConnection('127.0.0.1', 5309)

        http_obj.request('POST', '/v1/transfers',
                         headers=headers, body=data)
        http_obj.getresponse().AndReturn(FakeResponse(201, {'id': xfer_id}))

        path = '/v1/transfers/%s' % xfer_id
        http_obj.request('GET', path, headers=headers)
        http_obj.getresponse().AndReturn(
            FakeResponse(200, {'status': 'STATE_COMPLETE'}))

        self.mox.ReplayAll()
        st_plugin = staccato_nova_download.StaccatoTransfer()

        url_parts = urlparse.urlparse(src_url)
        dst_url_parts = urlparse.urlparse(dst_url)
        st_plugin.download(url_parts, dst_url_parts.path,
                           {}, context=context)
        self.mox.VerifyAll()

    def test_download_post_error(self):
        class FakeResponse(object):
            def __init__(self, status, reply):
                self.status = status
                self.reply = reply

            def read(self):
                return json.dumps(self.reply)

        self.config(auth_strategy='notkeystone')

        xfer_id = 'someidstring'
        src_url = 'file:///etc/group'
        dst_url = 'file:///tmp/group'
        data = {'source_url': src_url, 'destination_url': dst_url}

        headers = {'Content-Type': 'application/json'}

        self.mox.StubOutClassWithMocks(httplib, 'HTTPConnection')
        http_obj = httplib.HTTPConnection('127.0.0.1', 5309)

        http_obj.request('POST', '/v1/transfers',
                         headers=headers, body=data)
        http_obj.getresponse().AndReturn(FakeResponse(400, {'id': xfer_id}))

        self.mox.ReplayAll()
        st_plugin = staccato_nova_download.StaccatoTransfer()

        url_parts = urlparse.urlparse(src_url)
        dst_url_parts = urlparse.urlparse(dst_url)

        self.assertRaises(exception.ImageDownloadModuleError,
                          st_plugin.download,
                          url_parts,
                          dst_url_parts.path,
                          {})

        self.mox.VerifyAll()

    def test_successful_error_case(self):
        class FakeResponse(object):
            def __init__(self, status, reply):
                self.status = status
                self.reply = reply

            def read(self):
                return json.dumps(self.reply)

        self.config(auth_strategy='notkeystone')

        xfer_id = 'someidstring'
        src_url = 'file:///etc/group'
        dst_url = 'file:///tmp/group'
        data = {'source_url': src_url, 'destination_url': dst_url}

        headers = {'Content-Type': 'application/json'}

        self.mox.StubOutClassWithMocks(httplib, 'HTTPConnection')
        http_obj = httplib.HTTPConnection('127.0.0.1', 5309)

        http_obj.request('POST', '/v1/transfers',
                         headers=headers, body=data)
        http_obj.getresponse().AndReturn(FakeResponse(201, {'id': xfer_id}))

        path = '/v1/transfers/%s' % xfer_id
        http_obj.request('GET', path, headers=headers)
        http_obj.getresponse().AndReturn(
            FakeResponse(200, {'status': 'STATE_ERROR'}))
        path = '/v1/transfers/%s' % xfer_id
        http_obj.request('DELETE', path, headers=headers)
        http_obj.getresponse()

        self.mox.ReplayAll()
        st_plugin = staccato_nova_download.StaccatoTransfer()

        url_parts = urlparse.urlparse(src_url)
        dst_url_parts = urlparse.urlparse(dst_url)
        self.assertRaises(exception.ImageDownloadModuleError,
                          st_plugin.download,
                          url_parts,
                          dst_url_parts.path,
                          {})
        self.mox.VerifyAll()

    def test_status_error_case(self):
        class FakeResponse(object):
            def __init__(self, status, reply):
                self.status = status
                self.reply = reply

            def read(self):
                return json.dumps(self.reply)

        self.config(auth_strategy='notkeystone')

        xfer_id = 'someidstring'
        src_url = 'file:///etc/group'
        dst_url = 'file:///tmp/group'
        data = {'source_url': src_url, 'destination_url': dst_url}

        headers = {'Content-Type': 'application/json'}

        self.mox.StubOutClassWithMocks(httplib, 'HTTPConnection')
        http_obj = httplib.HTTPConnection('127.0.0.1', 5309)

        http_obj.request('POST', '/v1/transfers',
                         headers=headers, body=data)
        http_obj.getresponse().AndReturn(FakeResponse(201, {'id': xfer_id}))

        path = '/v1/transfers/%s' % xfer_id
        http_obj.request('GET', path, headers=headers)
        http_obj.getresponse().AndReturn(
            FakeResponse(500, {'status': 'STATE_COMPLETE'}))

        path = '/v1/transfers/%s' % xfer_id
        http_obj.request('DELETE', path, headers=headers)
        http_obj.getresponse()
        self.mox.ReplayAll()
        st_plugin = staccato_nova_download.StaccatoTransfer()

        url_parts = urlparse.urlparse(src_url)
        dst_url_parts = urlparse.urlparse(dst_url)
        self.assertRaises(exception.ImageDownloadModuleError,
                          st_plugin.download,
                          url_parts,
                          dst_url_parts.path,
                          {})
        self.mox.VerifyAll()
