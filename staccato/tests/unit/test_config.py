import json
import testtools

from staccato.common import config
from staccato.tests import utils


class TestConfig(utils.TempFileCleanupBaseTest):

    def test_db_connection_default(self):
        conf = config.get_config_object(args=[])
        self.assertEquals(conf.sql_connection, 'sqlite:///staccato.sqlite')

    def test_protocol_policy_retrieve_none(self):
        conf = config.get_config_object(args=[])
        conf.protocol_policy = None
        j = config.get_protocol_policy(conf)
        self.assertEqual(j, {})

    def test_protocol_policy_retrieve(self):
        conf = config.get_config_object(args=[])
        p_file = self.get_tempfile()
        policy = {"hello": "world"}
        fptr = open(p_file, 'w')
        fptr.write(json.dumps(policy))
        fptr.close()
        conf.protocol_policy = p_file
        j = config.get_protocol_policy(conf)
        self.assertEqual(j, policy)