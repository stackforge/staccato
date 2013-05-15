import testtools

from staccato.common import config


class TestConfig(testtools.TestCase):

    def test_db_connection_default(self):
        conf = config.get_config_object(args=[])
        self.assertEquals(conf.sql_connection, 'sqlite:///staccato.sqlite')
