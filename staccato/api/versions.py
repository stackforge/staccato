import httplib
import json
import webob

import staccato.openstack.common.wsgi as os_wsgi


class VersionApp(object):
    """
    A single WSGI application that just returns version information
    """
    def __init__(self, conf):
        self.conf = conf

    @webob.dec.wsgify(RequestClass=os_wsgi.Request)
    def __call__(self, req):
        version_info = {'id': self.conf.service_id,
                        'version': self.conf.version,
                        'status': 'active'}
        version_objs = [version_info]

        response = webob.Response(request=req,
                                  status=httplib.MULTIPLE_CHOICES,
                                  content_type='application/json')
        response.body = json.dumps(dict(versions=version_objs))
        return response
