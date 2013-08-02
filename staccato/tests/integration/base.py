#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os.path

import json

import staccato.common.config as config
import staccato.common.utils as staccato_utils
import staccato.openstack.common.pastedeploy as os_pastedeploy
import staccato.tests.utils as test_utils

TESTING_API_PASTE_CONF = """
[pipeline:staccato-api]
pipeline = unauthenticated-context rootapp

# Use this pipeline for keystone auth
[pipeline:staccato-api-keystone]
pipeline = authtoken context rootapp

[app:rootapp]
use = egg:Paste#urlmap
/v1: apiv1app
/: apiversions

[app:apiversions]
paste.app_factory = staccato.openstack.common.pastedeploy:app_factory
openstack.app_factory = staccato.api.versions:VersionApp

[app:apiv1app]
paste.app_factory = staccato.openstack.common.pastedeploy:app_factory
openstack.app_factory = staccato.api.v1.xfer:API

[filter:unauthenticated-context]
paste.filter_factory = staccato.openstack.common.pastedeploy:filter_factory
openstack.filter_factory = staccato.api.v1.xfer:UnauthTestMiddleware

[filter:authtoken]
paste.filter_factory = keystoneclient.middleware.auth_token:filter_factory
delay_auth_decision = true

[filter:context]
paste.filter_factory = staccato.openstack.common.pastedeploy:filter_factory
openstack.filter_factory = staccato.api.v1.xfer:AuthContextMiddleware
"""


class ApiTestBase(test_utils.TempFileCleanupBaseTest):
    def setUp(self):
        super(ApiTestBase, self).setUp()
        self.test_dir = self.get_tempdir()
        self.sql_connection = 'sqlite://'
        self.conf = config.get_config_object(args=[])
        self.config(sql_connection=self.sql_connection)
        self.write_protocol_module_file()
        self.config(db_auto_create=True)
        self.needs_database = True

    def get_http_client(self):
        staccato_api = self._load_paste_app(
            'staccato-api', TESTING_API_PASTE_CONF, self.conf)
        return test_utils.Httplib2WsgiAdapter(staccato_api)

    def _load_paste_app(self, name, paste_conf, conf):
        conf_file_path = os.path.join(self.test_dir, '%s-paste.ini' % name)
        with open(conf_file_path, 'wb') as conf_file:
            conf_file.write(paste_conf)
            conf_file.flush()

        return os_pastedeploy.paste_deploy_app(conf_file_path,
                                                   name,
                                                   conf)

    def tearDown(self):
        super(ApiTestBase, self).tearDown()

    def config(self, **kw):
        group = kw.pop('group', None)
        for k, v in kw.iteritems():
            self.conf.set_override(k, v, group)

    def write_protocol_module_file(self, protocols=None):
        if protocols is None:
            protocols = {
                "file": [{"module": "staccato.protocols.file.FileProtocol"}],
                "http": [{"module": "staccato.protocols.http.HttpProtocol"}]
            }
        temp_file = self.get_tempfile()
        with open(temp_file, 'w') as fp:
            json.dump(protocols, fp)

        self.config(protocol_policy=temp_file)
        return temp_file


