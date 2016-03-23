import socket, sys
from pyed.event import event


class tcpserver(object):
    def __init__(self, accepthandler, srvconf):
        self.__host = srvconf["host"]
        self.__port = srvconf["port"]
        self.__blocking = srvconf["blocking"]
        self.__reuseaddr = srvconf["reuseaddr"]
        self.__backlog = srvconf["backlog"]
        self.__reuseport = srvconf["reuseport"]
        self.__accepthandler = accepthandler

        try:
            self.__port = int(self.__port)
        except:
            try:
                self.__port = socket.getservbyname(self.__port, "tcp")
            except Exception, e:
                sys.stdout.write("Error occur when getservbyname(%d): %s\n" % (self.__port, e))
                raise e

        self.__initserver()

    def __initserver(self):
        try:
            self.__sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.__sock.setblocking(self.__blocking)
            self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.__reuseaddr)
            self.__sock.bind((self.__host, self.__port))
            self.__sock.listen(self.__backlog)
            self.__ev = event(self.__sock)
            self.__ev.add_read(self.__accepthandler)
        except socket.error, e:
            sys.stdout.write("Error occur when initserver: %s\n" % e)
            raise e
