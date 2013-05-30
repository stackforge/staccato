import os
from staccato.tests import utils
from staccato.common import config


class TestDB(utils.TempFileCleanupBaseTest):

    def setUp(self):
        super(TestDB, self).setUp()

        self.owner = 'someperson'
        self.tmp_db = self.get_tempfile()
        self.db_url = 'sqlite:///%s' % (self.tmp_db)

        conf_d = {'sql_connection': self.db_url,
                  'protocol_policy': ''}

        self.conf_file = self.make_confile(conf_d)
        self.conf = config.get_config_object(
            args=[],
            default_config_files=[self.conf_file])
        self.db = self.make_db(self.conf)

    def test_db_creation(self):
        self.assertTrue(os.path.exists(self.tmp_db))

    def test_db_new_xfer(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"
        xfer = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        self.assertEqual(src, xfer.srcurl)
        self.assertEqual(dst, xfer.dsturl)
        self.assertEqual(sm, xfer.src_module_name)
        self.assertEqual(dm, xfer.dst_module_name)

    def test_db_xfer_lookup(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.lookup_xfer_request_by_id(xfer1.id)
        self.assertEqual(xfer1.id, xfer2.id)

    def test_db_xfer_update(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer1.next_ndx = 10
        self.db.save_db_obj(xfer1)
        xfer2 = self.db.lookup_xfer_request_by_id(xfer1.id)
        self.assertEqual(xfer2.next_ndx, 10)
