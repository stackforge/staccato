from staccato.common import utils


class BaseProtocolInterface(object):

    @utils.not_implemented_decorator
    def get_reader(self, url_parts, writer, monitor, start=0, end=None,
                   **kwvals):
        pass

    @utils.not_implemented_decorator
    def get_writer(self, url_parts, checkpointer, **kwvals):
        pass

    @utils.not_implemented_decorator
    def new_write(self, dsturl_parts, dst_opts):
        pass

    @utils.not_implemented_decorator
    def new_read(self, srcurl_parts, src_opts):
        pass


class BaseReadConnection(object):

    @utils.not_implemented_decorator
    def process(self):
        pass


class BaseWriteConnection(object):

    @utils.not_implemented_decorator
    def write(self, buffer, offset):
        pass

    @utils.not_implemented_decorator
    def close(self):
        pass
