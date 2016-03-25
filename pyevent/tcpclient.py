import socket, sys
from tcpconnection import tcpconnection


class tcpclient(object):
    def __init__(self, cliconf):
        self._peerhost = cliconf["host"]
        self._peerport = cliconf["port"]
        self._cliconf = cliconf

    def connect(self):
        try:
            addrs = socket.getaddrinfo(self._peerhost, self._peerport, 0, socket.SOCK_STREAM)
            addr = addrs[0][4]
        except socket.error, e:
            sys.stdout.write("get addr info(%s: %d) error: %s\n" % (self._peerhost, self._peerport, e))
            raise e

        try:
            self._sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self._sock.connect((addr[0], addr[1]))
            c = tcpconnection(self._sock, self._cliconf)
            return c
        except socket.error, e:
            sys.stdout.write("Error occur connect to TCPServer(%s: %d): %s\n" % (addr[0], addr[1], e))
            raise e
