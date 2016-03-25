import socket, sys
from event import event


class tcpserver(object):
    def __init__(self, accepthandler, srvconf, evs, tms):
        self._evs = evs
        self._tms = tms
        self._host = srvconf["host"]
        self._port = srvconf["port"]
        self._blocking = srvconf["blocking"]
        self._reuseaddr = srvconf["reuseaddr"]
        self._backlog = srvconf["backlog"]
        self._reuseport = srvconf["reuseport"]
        self._accepthandler = accepthandler

        try:
            self._port = int(self._port)
        except:
            try:
                self._port = socket.getservbyname(self._port, "tcp")
            except Exception, e:
                sys.stdout.write("Error occur when getservbyname(%d): %s\n" % (self._port, e))
                raise e

        self._initserver()

    def _initserver(self):
        try:
            self._sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self._sock.setblocking(self._blocking)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self._reuseaddr)
            self._sock.bind((self._host, self._port))
            self._sock.listen(self._backlog)
            self._ev = event(self._evs, self._tms, self._sock)
            self._ev.add_read(self._accepthandler)
        except socket.error, e:
            sys.stdout.write("Error occur when initserver: %s\n" % e)
            raise e
