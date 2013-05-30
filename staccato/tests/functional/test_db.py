import os
from staccato.tests import utils
from staccato.common import config
import staccato.common.exceptions as exceptions
import staccato.xfer.constants as constants


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

    def test_db_xfer_lookup_with_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.lookup_xfer_request_by_id(xfer1.id, owner=self.owner)
        self.assertEqual(xfer1.id, xfer2.id)

    def test_db_xfer_lookup_with_wrong_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        self.assertRaises(exceptions.StaccatoNotFoundInDBException,
                          self.db.lookup_xfer_request_by_id,
                          xfer1.id, **{'owner': 'someoneelse'})

    def test_db_xfer_lookup_not_there(self):
        self.assertRaises(exceptions.StaccatoNotFoundInDBException,
                          self.db.lookup_xfer_request_by_id,
                          "notthere")

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

    def test_lookup_all_no_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        xfer_list = self.db.lookup_xfer_request_all()
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)

    def test_lookup_all_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        xfer_list = self.db.lookup_xfer_request_all(owner=self.owner)
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)

    def test_lookup_all_wrong_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        xfer_list = self.db.lookup_xfer_request_all(owner='notme')
        self.assertEqual(len(xfer_list), 0)

    def test_lookup_all_many_owners(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer3 = self.db.get_new_xfer('notme', src, dst, sm, dm)
        xfer4 = self.db.get_new_xfer('notme', src, dst, sm, dm)
        xfer5 = self.db.get_new_xfer('someoneelse', src, dst, sm, dm)

        xfer_list = self.db.lookup_xfer_request_all(owner=self.owner)
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)

    def test_get_all_ready_new_no_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        xfer_list = self.db.get_all_ready()
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)

    def test_get_all_ready_new_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        xfer_list = self.db.get_all_ready(owner=self.owner)
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)

    def test_get_all_ready_wrong_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        xfer_list = self.db.get_all_ready(owner='notme')
        self.assertEqual(len(xfer_list), 0)

    def test_get_all_ready_some_not(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer3 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        xfer3.state = constants.States.STATE_RUNNING
        self.db.save_db_obj(xfer3)

        xfer_list = self.db.get_all_ready()
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)

    def test_get_all_ready_some_error(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        xfer2.state = constants.States.STATE_ERROR
        self.db.save_db_obj(xfer2)


        xfer_list = self.db.get_all_ready()
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)

    def test_get_all_running(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer3 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        for x in [xfer1, xfer2, xfer3]:
            x.state = constants.States.STATE_RUNNING
            self.db.save_db_obj(x)

        xfer_list = self.db.get_all_running()
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 3)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)
        self.assertTrue(xfer3.id in id_list)

    def test_get_all_running_some_not(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer3 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        for x in [xfer1, xfer3]:
            x.state = constants.States.STATE_RUNNING
            self.db.save_db_obj(x)

        xfer_list = self.db.get_all_running()
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer3.id in id_list)

    def test_delete_from_db(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer3 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        self.db.delete_db_obj(xfer2)

        xfer_list = self.db.get_all_ready()
        id_list = [x.id for x in xfer_list]

        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer3.id in id_list)

    def test_get_many_requests_no_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer3 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        id_list = [xfer1.id, xfer2.id, xfer3.id]
        xfer_list = self.db.get_xfer_requests(ids=id_list)
        self.assertEqual(len(xfer_list), 3)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)
        self.assertTrue(xfer3.id in id_list)

    def test_get_many_requests_owner(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer3 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        id_list = [xfer1.id, xfer2.id, xfer3.id]
        xfer_list = self.db.get_xfer_requests(ids=id_list, owner=self.owner)
        self.assertEqual(len(xfer_list), 3)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)
        self.assertTrue(xfer3.id in id_list)

    def test_get_many_requests_owner_subset(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer3 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        id_list = [xfer1.id, xfer3.id]
        xfer_list = self.db.get_xfer_requests(ids=id_list, owner=self.owner)
        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer3.id in id_list)

    def test_get_many_requests_some_wrong_owner_subset(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer3 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer4 = self.db.get_new_xfer('notme', src, dst, sm, dm)

        id_list = [xfer1.id, xfer3.id]
        xfer_list = self.db.get_xfer_requests(ids=id_list, owner=self.owner)
        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer3.id in id_list)

    def test_get_many_requests_get_invalid(self):
        src = "src://url"
        dst = "dst://url"
        sm = "src.module"
        dm = "dst.module"

        xfer1 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)
        xfer2 = self.db.get_new_xfer(self.owner, src, dst, sm, dm)

        id_list = [xfer1.id, xfer2.id, 'nothereatall']
        xfer_list = self.db.get_xfer_requests(ids=id_list, owner=self.owner)
        self.assertEqual(len(xfer_list), 2)
        self.assertTrue(xfer1.id in id_list)
        self.assertTrue(xfer2.id in id_list)
