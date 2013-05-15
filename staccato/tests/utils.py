import tempfile
import testtools
import staccato.db as db
import os
import json

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


class TempFileCleanupBaseTest(testtools.TestCase):

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
        return tempfile.mkstemp()[1]
