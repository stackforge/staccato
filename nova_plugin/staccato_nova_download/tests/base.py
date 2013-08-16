from oslo.config import cfg

import testtools


CONF = cfg.CONF


class BaseTest(testtools.TestCase):
    def setUp(self):
        super(BaseTest, self).setUp()

    def tearDown(self):
        super(BaseTest, self).tearDown()

    def config(self, **kw):
        group = kw.pop('group', None)
        for k, v in kw.iteritems():
            CONF.set_override(k, v, group)
