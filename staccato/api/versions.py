import httplib
import json
import webob

from staccato.common import wsgi


class VersionApp(object):
    """
    A single WSGI application that just returns version information
    """
    def __init__(self, conf):
        self.conf = conf

    @webob.dec.wsgify(RequestClass=wsgi.Request)
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


def create_resource(conf):
    # TODO: figure out what this has to be this way
    config_obj = conf['CONF']['conf']
    return VersionApp(conf=config_obj)
