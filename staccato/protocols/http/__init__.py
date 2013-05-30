import urllib2

import staccato.protocols.interface as base
from staccato.common import exceptions


class HttpProtocol(base.BaseProtocolInterface):

    def __init__(self, service_config):
        self.conf = service_config

    def _validate_url(self, url_parts):
        pass

    def _parse_opts(self, opts):
        return opts

    def new_write(self, dsturl_parts, dst_opts):
        opts = self._parse_opts(dst_opts)
        return opts

    def new_read(self, srcurl_parts, src_opts):
        opts = self._parse_opts(src_opts)
        return opts

    def get_reader(self, url_parts, writer, monitor, source_opts, start=0,
                   end=None, **kwvals):
        self._validate_url(url_parts)

        return HttpReadConnection(url_parts,
                                  writer,
                                  monitor,
                                  start=start,
                                  end=end,
                                  **kwvals)

    def get_writer(self, url_parts, dest_opts, checkpointer, **kwvals):
        raise exceptions.StaccatoNotImplementedException(
            _('The HTTP protocol is read only'))

class HttpReadConnection(base.BaseReadConnection):

    def __init__(self,
                 url_parts,
                 writer,
                 monitor,
                 start=0,
                 end=None,
                 buflen=65536,
                 **kwvals):
        whole_url = url_parts.geturl()

        req = urllib2.Request(whole_url)
        range_str = 'bytes=%sd-' % start
        if end and end > start:
            range_str = range_str + str(end)
        req.headers['Range'] = range_str
        self.h_con = urllib2.urlopen(req)
        self.pos = start
        self.eof = False
        self.writer = writer
        self.buflen = buflen
        self.monitor = monitor

    def _read(self, buflen):
        buf = self.h_con.read(buflen)
        if not buf:
            return True, 0
        self.writer.write(buf, self.pos)

        self.pos = self.pos + len(buf)
        return False, len(buf)

    def process(self):
        try:
            while not self.monitor.is_done() and not self.eof:
                self.eof, read_len = self._read(self.buflen)
        finally:
            self.h_con.close()
