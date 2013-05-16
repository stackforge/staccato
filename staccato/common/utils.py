import logging
import re

from paste import deploy

from staccato.common import exceptions
from staccato.openstack.common import importutils


def not_implemented_decorator(func):
    def call(self, *args, **kwargs):
        def raise_error(func):
            raise exceptions.StaccatoNotImplementedException(
                "function %s must be implemented" % (func.func_name))
        return raise_error(func)
    return call


def load_paste_app(app_name, conf_file, conf):
    try:
        logger = logging.getLogger(__name__)
        logger.debug(_("Loading %(app_name)s from %(conf_file)s"),
                     {'conf_file': conf_file, 'app_name': app_name})

        app = deploy.loadapp("config:%s" % conf_file,
                             name=app_name,
                             global_conf={'CONF': conf})

        return app
    except (LookupError, ImportError) as e:
        msg = _("Unable to load %(app_name)s from "
                "configuration file %(conf_file)s."
                "\nGot: %(e)r") % locals()
        logger.error(msg)
        raise RuntimeError(msg)


def find_protocol_module_name(lookup_dict, url_parts):
    if url_parts.scheme not in lookup_dict:
        raise exceptions.StaccatoParameterError(
            '%s protocol not found' % url_parts.scheme)
    p_list = lookup_dict[url_parts.scheme]

    for entry in p_list:
        match_keys = ['netloc', 'path', 'params', 'query']
        ndx = 0
        found = True
        for k in match_keys:
            ndx = ndx + 1
            if k in entry:
                needle = url_parts[ndx]
                haystack = entry[k]
                found = re.match(haystack, needle)
        if found:
            return entry['module']

    raise exceptions.StaccatoParameterError(
        'The url %s is not supported' % url_parts.geturl())


def load_protocol_module(module_name, CONF):
    try:
        protocol_cls = importutils.import_class(module_name)
    except ImportError, ie:
        raise exceptions.StaccatoParameterError(
            "The protocol module %s could not be loaded. %s" %
            (module_name, ie))

    protocol_instance = protocol_cls(CONF)

    return protocol_instance
