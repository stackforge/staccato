import testtools

import staccato.tests.utils as tests_utils
import staccato.common.utils as common_utils

import staccato.xfer.utils as xfers_utils
import staccato.protocols.interface as proto_iface
import staccato.common.exceptions as exceptions
import staccato.common.config as config

class FakeXferRequest(object):
        next_ndx = 0


class FakeDB(object):

    def save_db_obj(self, obj):
        pass


class TestXferCheckpointerSingleSync(testtools.TestCase):

    def setUp(self):
        super(TestXferCheckpointerSingleSync, self).setUp()

        self.fake_xfer = FakeXferRequest()
        self.checker = xfers_utils.XferCheckpointer(
            self.fake_xfer, {}, FakeDB(), db_refresh_rate=0)

    def _run_blocks(self, blocks):
        for start, end in blocks:
            self.checker.update(start, end)
        self.checker.sync({})

    def test_non_continuous_zero(self):
        blocks = [(10, 20), (30, 40)]
        self._run_blocks(blocks)
        self.assertEqual(self.fake_xfer.next_ndx, 0)

    def test_join_simple(self):
        blocks = [(0, 20), (20, 40)]
        self._run_blocks(blocks)
        self.assertEqual(self.fake_xfer.next_ndx, 40)

    def test_non_continuous(self):
        blocks = [(0, 5), (10, 20)]
        self._run_blocks(blocks)
        self.assertEqual(self.fake_xfer.next_ndx, 5)

    def test_join_single(self):
        blocks = [(0, 20)]
        self._run_blocks(blocks)
        self.assertEqual(self.fake_xfer.next_ndx, 20)

    def test_join_overlap(self):
        blocks = [(0, 20), (10, 30)]
        self._run_blocks(blocks)
        self.assertEqual(self.fake_xfer.next_ndx, 30)

    def test_join_included(self):
        blocks = [(0, 20), (10, 15)]
        self._run_blocks(blocks)
        self.assertEqual(self.fake_xfer.next_ndx, 20)

    def test_join_large_later(self):
        blocks = [(10, 20), (30, 40), (0, 100)]
        self._run_blocks(blocks)
        self.assertEqual(self.fake_xfer.next_ndx, 100)

    def test_join_out_of_order(self):
        blocks = [(30, 40), (0, 10), (20, 30), (10, 25)]
        self._run_blocks(blocks)
        self.assertEqual(self.fake_xfer.next_ndx, 40)

class TestBasicUtils(tests_utils.TempFileCleanupBaseTest):

    def test_empty_interface(self):
        blank_interface = proto_iface.BaseProtocolInterface()
        kwargs = {
            'url_parts': None,
            'writer': None,
            'monitor': None,
            'source_opts': None,
            'start': 0,
            'end': None,
        }

        interface_funcs = [blank_interface.get_reader,
                           blank_interface.get_writer,
                           blank_interface.new_read,
                           blank_interface.new_write]

        for func in interface_funcs:
            self.assertRaises(
                exceptions.StaccatoNotImplementedException,
                func,
                **kwargs)

    def test_load_paste_app_error(self):
        conf = config.get_config_object(args=[])
        p_file = self.get_tempfile()
        self.assertRaises(
            RuntimeError,
            common_utils.load_paste_app,
            'notthere', p_file, conf)

    # TODO: test the loading of a good app