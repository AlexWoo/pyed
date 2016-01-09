import socket, sys
from pyed.tcpconnection import tcpconnection


class tcpclient(object):
    def __init__(self, cliconf):
        self.__peerhost = cliconf["host"]
        self.__peerport = cliconf["port"]
        self.__cliconf = cliconf

    def connect(self):
        try:
            addrs = socket.getaddrinfo(self.__peerhost, self.__peerport, 0, socket.SOCK_STREAM)
            addr = addrs[0][4]
        except socket.error, e:
            sys.stdout.write("get addr info(%s: %d) error: %s\n" % (self.__peerhost, self.__peerport, e))
            raise e

        try:
            self.__sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.__sock.connect((addr[0], addr[1]))
            c = tcpconnection(self.__sock, self.__cliconf)
            return c
        except socket.error, e:
            sys.stdout.write("Error occur connect to TCPServer(%s: %d): %s\n" % (addr[0], addr[1], e))
            raise e
