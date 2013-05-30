import eventlet
import gettext
import sys

from staccato.common import config
import staccato.scheduler.interface as scheduler

# Monkey patch socket and time
eventlet.patcher.monkey_patch(all=False, socket=True, time=True)

gettext.install('staccato', unicode=1)


def fail(returncode, e):
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(returncode)


def main():
    try:
        conf = config.get_config_object()
        sched = scheduler.get_scheduler(conf)
        sched.start()
        sched.wait()
    except RuntimeError as e:
        fail(1, e)
