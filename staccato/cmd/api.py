import eventlet
import gettext
import sys

from staccato.common import utils
from staccato import wsgi

# Monkey patch socket and time
eventlet.patcher.monkey_patch(all=False, socket=True, time=True)

gettext.install('staccato', unicode=1)


def fail(returncode, e):
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(returncode)


class CONF(object):
    def __init__(self):
        self.bind_host = "0.0.0.0"
        self.bind_port = 9876
        self.cert_file = None
        self.key_file = None
        self.backlog = -1
        self.tcp_keepidle = False
        self.id = "deadbeef"
        self.version = "v1"


def main():
    try:
        #config.parse_args(sys.argv)
        conf = CONF()
        wsgi_app = utils.load_paste_app(
            'staccato-api',
            '/home/jbresnah/Dev/OpenStack/staccato/etc/glance-api-paste.ini',
            {'conf': conf})

        server = wsgi.Server(CONF=conf)
        server.start(wsgi_app, default_port=9292)
        server.wait()
    except RuntimeError as e:
        fail(1, e)


main()
