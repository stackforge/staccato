import staccato.protocols.interface as base
from staccato.common import exceptions


class FileProtocol(base.BaseProtocolInterface):

    def __init__(self, service_config):
        self.conf = service_config

    def _validate_url(self, url_parts):
        pass

    def new_write(self, dsturl_parts, dst_opts):
        return dst_opts

    def new_read(self, srcurl_parts, src_opts):
        return src_opts

    def get_reader(self, url_parts, writer, monitor, source_opts, start=0,
                   end=None, **kwvals):
        self._validate_url(url_parts)

        return FileReadConnection(url_parts.path,
                                  writer,
                                  monitor,
                                  start=start,
                                  end=end,
                                  buflen=65536,
                                  **kwvals)

    def get_writer(self, url_parts, dest_opts, checkpointer, **kwvals):
        self._validate_url(url_parts)

        return FileWriteConnection(url_parts.path, checkpointer=checkpointer,
                                   **kwvals)


class FileReadConnection(base.BaseReadConnection):

    def __init__(self,
                 path,
                 writer,
                 monitor,
                 start=0,
                 end=None,
                 buflen=65536,
                 **kwvals):

        try:
            self.fptr = open(path, 'rb')
        except IOError, ioe:
            raise exceptions.StaccatoProtocolConnectionException(
                ioe.message)
        self.pos = start
        self.eof = False
        self.writer = writer
        self.path = path
        self.buflen = buflen
        self.end = end
        self.monitor = monitor

    def _read(self, buflen):
        current_pos = self.fptr.tell()
        if current_pos != self.pos:
            self.fptr.seek(self.pos)

        if self.end and self.pos + buflen > self.end:
            buflen = self.end - self.pos
        buf = self.fptr.read(buflen)
        if not buf:
            return True, 0
        self.writer.write(buf, self.pos)

        self.pos = self.pos + len(buf)
        if self.end and self.pos >= self.end:
            return True, len(buf)
        if len(buf) < buflen:
            return True, len(buf)
        return False, len(buf)

    def process(self):
        if isinstance(self.writer, FileWriteConnection):
            # TODO here we can do a system copy optimization
            pass

        try:
            while not self.monitor.is_done() and not self.eof:
                self.eof, read_len = self._read(self.buflen)
        finally:
            self.fptr.close()


class FileWriteConnection(base.BaseWriteConnection):

    def __init__(self, path, checkpointer=None, **kwvals):
        self.count = 0
        self.persist = checkpointer
        try:
            self.fptr = open(path, 'wb')
        except IOError, ioe:
            raise exceptions.StaccatoProtocolConnectionException(
                ioe.message)

    def write(self, buffer, offset):
        self.fptr.seek(offset, 0)
        rc = self.fptr.write(buffer)
        if self.persist:
            self.persist.update(offset, offset + len(buffer))
        self.count = self.count + 1
        if self.count > 10:
            self.count = 0
            self.fptr.flush()
            if self.persist:
                self.persist.sync({})

        return rc

    def close(self):
        return self.fptr.close()
