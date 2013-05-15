import urlparse
import testtools
from staccato.common import utils, exceptions
import staccato.protocols.file as file_protocol


class TestProtocolLoading(testtools.TestCase):

    def setUp(self):
        super(TestProtocolLoading, self).setUp()

    def test_basic_load(self):
        proto_name = "staccato.protocols.file.FileProtocol"
        inst = utils.load_protocol_module(proto_name, {})
        self.assertTrue(isinstance(inst, file_protocol.FileProtocol))

    def test_failed_load(self):
        self.assertRaises(exceptions.StaccatoParameterError,
                          utils.load_protocol_module,
                          "notAModule", {})

    def test_find_module_default(self):
        url = "file://host.com:90//path/to/file"
        url_parts = urlparse.urlparse(url)
        module_path = "just.some.thing"

        lookup_dict = {
            'file': [{'module': module_path}]
        }
        res = utils.find_protocol_module_name(lookup_dict, url_parts)
        self.assertEqual(res, module_path)

    def test_find_module_wildcards(self):
        url = "file://host.com:90//path/to/file"
        url_parts = urlparse.urlparse(url)
        module_path = "just.some.thing"

        lookup_dict = {
            'file': [{'module': module_path,
                     'netloc': '.*',
                     'path': '.*'}]
        }
        res = utils.find_protocol_module_name(lookup_dict, url_parts)
        self.assertEqual(res, module_path)

    def test_find_module_multiple_wildcards(self):
        url = "file://host.com:90//path/to/file"
        url_parts = urlparse.urlparse(url)
        bad_module_path = "just.some.bad.thing"
        good_module_path = "just.some.bad.thing"

        lookup_dict = {
            'file': [{'module': bad_module_path,
                     'netloc': '.*',
                     'path': '/sorry/.*'},
                     {'module': good_module_path}]
        }
        res = utils.find_protocol_module_name(lookup_dict, url_parts)
        self.assertEqual(res, good_module_path)

    def test_find_module_wildcards_middle(self):
        url = "file://host.com:90//path/to/file"
        url_parts = urlparse.urlparse(url)
        module_path = "just.some.thing"

        lookup_dict = {
            'file': [{'module': module_path,
                     'netloc': '.*host.com.*',
                     'path': '.*'}]
        }
        res = utils.find_protocol_module_name(lookup_dict, url_parts)
        self.assertEqual(res, module_path)

    def test_find_module_not_found(self):
        url = "file://host.com:90//path/to/file"
        url_parts = urlparse.urlparse(url)
        module_path = "just.some.thing"

        lookup_dict = {
            'file': [{'module': module_path,
                     'netloc': '.*',
                     'path': '/secure/path/only.*'}]
        }
        self.assertRaises(exceptions.StaccatoParameterError,
                          utils.find_protocol_module_name,
                          lookup_dict,
                          url_parts)

    def test_find_no_url_scheme(self):
        url = "file://host.com:90//path/to/file"
        url_parts = urlparse.urlparse(url)
        module_path = "just.some.thing"

        lookup_dict = {
            'junk': [{'module': module_path,
                     'netloc': '.*',
                     'path': '/secure/path/only.*'}]
        }
        self.assertRaises(exceptions.StaccatoParameterError,
                          utils.find_protocol_module_name,
                          lookup_dict,
                          url_parts)
