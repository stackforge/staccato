from staccato.common import utils


class BaseProtocolInterface(object):

    @utils.not_implemented_decorator
    def get_reader(self, url_parts, writer, monitor, source_opts, start=0,
                   end=None, **kwvals):
        pass

    @utils.not_implemented_decorator
    def get_writer(self, url_parts, dest_opts, checkpointer, **kwvals):
        pass

    @utils.not_implemented_decorator
    def new_write(self, request, dsturl_parts, dst_opts):
        pass

    @utils.not_implemented_decorator
    def new_read(self, request, srcurl_parts, src_opts):
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
