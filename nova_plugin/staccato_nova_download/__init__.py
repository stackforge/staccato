# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
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

import httplib
import json
import logging

from oslo.config import cfg

from nova import exception
import nova.image.download.base as xfer_base
from nova.openstack.common.gettextutils import _


CONF = cfg.CONF
LOG = logging.getLogger(__name__)

opt_groups = [cfg.StrOpt(name='hostname', default='127.0.0.1',
                         help=_('The hostname of the staccato service.')),
              cfg.IntOpt(name='port', default=5309,
                         help=_('The port where the staccato service is '
                                'listening.')),
              cfg.IntOpt(name='poll_interval', default=1,
                         help=_('The amount of time in second to poll for '
                                'transfer completion'))
              ]

CONF.register_opts(opt_groups, group="staccato_nova_download_module")


class StaccatoTransfer(xfer_base.TransferBase):

    def __init__(self):
        self.conf_group = CONF['staccato_nova_download_module']
        self.client = httplib.HTTPConnection(self.conf_group.hostname,
                                             self.conf_group.port)

    def _delete(self, xfer_id, headers):
        path = '/v1/transfers/%s' % xfer_id
        self.client.request('DELETE', path, headers=headers)
        response = self.client.getresponse()
        if response.status != 204:
            msg = _('Error deleting transfer %s') % response.read()
            LOG.error(msg)
            raise exception.ImageDownloadModuleError(
                {'reason': msg, 'module': unicode(self)})

    def _wait_for_complete(self, xfer_id, headers):
        error_states = ['STATE_CANCELED', 'STATE_ERROR', 'STATE_DELETED']

        path = '/v1/transfers/%s' % xfer_id
        while True:
            self.client.request('GET', path, headers=headers)
            response = self.client.getresponse()
            if response.status != 200:
                msg = _('Error requesting a new transfer %s') % response.read()
                LOG.error(msg)
                try:
                    self._delete(xfer_id, headers)
                except Exception as ex:
                    LOG.error(ex)
                raise exception.ImageDownloadModuleError(
                    {'reason': msg, 'module': unicode(self)})

            body = response.read()
            response_dict = json.loads(body)
            if response_dict['state'] == 'STATE_COMPLETE':
                break

            if response_dict['state'] in error_states:
                try:
                    self._delete(xfer_id, headers)
                except Exception as ex:
                    LOG.error(ex)
                msg = (_('The transfer could not be completed in state %s')
                       % response_dict['state'])
                raise exception.ImageDownloadModuleError(
                    {'reason': msg, 'module': unicode(self)})

    def download(self, context, url_parts, dst_file, metadata, **kwargs):
        LOG.info((_('Attemption to use %(module)s to download %(url)s')) %
                 {'module': unicode(self), 'url': url_parts.geturl()})

        headers = {'Content-Type': 'application/json'}
        if CONF.auth_strategy == 'keystone':
            headers['X-Auth-Token'] = getattr(context, 'auth_token', None)
            headers['X-User-Id'] = getattr(context, 'user', None)
            headers['X-Tenant-Id'] = getattr(context, 'tenant', None)

        data = {'source_url': url_parts.geturl(),
                'destination_url': 'file://%s' % dst_file}
        try:
            self.client.request('POST', '/v1/transfers',
                                headers=headers, body=json.dumps(data))
            response = self.client.getresponse()
            if response.status != 200:
                msg = (_('Error requesting a new transfer %s.  Status = %d') %
                       (response.read(), response.status))
                LOG.error(msg)
                raise exception.ImageDownloadModuleError(
                    {'reason': msg, 'module': unicode(self)})
            body = response.read()
            response_dict = json.loads(body)

            self._wait_for_complete(response_dict['id'], headers)
        except exception.ImageDownloadModuleError:
            raise
        except Exception as ex:
            msg = unicode(ex.message)
            LOG.exception(ex)
            raise exception.ImageDownloadModuleError(
                {'reason': msg, 'module': u'StaccatoTransfer'})


def get_download_hander(**kwargs):
    return StaccatoTransfer()


def get_schemes():
    conf_group = CONF['staccato_nova_download_module']
    try:
        LOG.info(("Staccato get_schemes(): %s:%s" %
                  (conf_group.hostname, conf_group.port)))
        client = httplib.HTTPConnection(conf_group.hostname, conf_group.port)
        client.request('GET', '/')
        response = client.getresponse()
        body = response.read()
        LOG.info("Staccato version info %s" % body)
        json_body = json.loads(body)
        version_json = json_body['versions']
        if 'v1' not in version_json:
            reason = 'The staccato service does not support v1'
            LOG.error(reason)
            raise exception.ImageDownloadModuleError({'reason': reason,
                                                      'module': u'staccato'})

        version_json = version_json['v1']
        LOG.info("Staccato offers %s" % str(version_json))
        return version_json['protocols']
    except Exception as ex:
        LOG.exception(ex)
        reason = str(ex)
        LOG.error(reason)
        return []
#NOTE(jbresnah) nova doesn't properly handle this yet
#        raise exception.ImageDownloadModuleError({'reason': reason,
#                                                  'module': u'staccato'})
