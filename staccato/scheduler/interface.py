import staccato.scheduler.simple_thread as simple_thread


def get_scheduler(conf):
    # todo: pull this from the configuration information
    return simple_thread.SimpleCountSchedler(conf)
