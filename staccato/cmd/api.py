import eventlet
import gettext
import sys

from staccato.common import config
import staccato.openstack.common.wsgi as os_wsgi
import staccato.openstack.common.pastedeploy as os_pastedeploy

# Monkey patch socket and time
eventlet.patcher.monkey_patch(all=False, socket=True, time=True)

gettext.install('staccato', unicode=1)


def fail(returncode, e):
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(returncode)


def main():
    try:
        conf = config.get_config_object()
        paste_file = conf.find_file(conf.paste_deploy.config_file)
        wsgi_app = os_pastedeploy.paste_deploy_app(paste_file,
                                                   'staccato-api',
                                                   conf)
        server = os_wsgi.Service(wsgi_app, conf.bind_port)
        server.start()
        server.wait()
    except RuntimeError as e:
        fail(1, e)

main()
