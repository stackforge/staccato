import httplib
import json

import webob.dec
import webob.exc

import staccato.openstack.common.wsgi as os_wsgi
import staccato.db as db

class XferApp(object):
    """
    A single WSGI application that just returns version information
    """
    def __init__(self, conf):
        self.conf = conf
        self.db = db.StaccatoDB(self.conf)

    @webob.dec.wsgify(RequestClass=os_wsgi.Request)
    def __call__(self, req):
        version_info = {
                'id': self.conf.id,
                'version': self.conf.version,
                'status': 'active'
            }
        version_objs = [version_info]

        response = webob.Response(request=req,
                                  status=httplib.MULTIPLE_CHOICES,
                                  content_type='application/json')
        response.body = json.dumps(dict(versions=version_objs))
        return response


