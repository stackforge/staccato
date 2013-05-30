import testtools

import staccato.xfer.utils as xfers_utils


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
