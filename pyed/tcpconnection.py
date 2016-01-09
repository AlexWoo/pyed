import sys, socket, errno
from struct import pack
from pyed.event import event


class tcpconnection(object):
    OK = 0
    ERROR = -1
    AGAIN = -2
    
    def __init__(self, sock, srvconf):
        self.__sock = sock
        self.__blocking = srvconf["blocking"]
        self.__recvbuf = srvconf["recvbuf"]
        self.__sendbuf = srvconf["sendbuf"]
        self.__linger = pack("ii", srvconf["linger"][0], srvconf["linger"][1])
        self.__sock.setblocking(self.__blocking)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.__recvbuf)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.__sendbuf)

        self.__readbuffer = ""
        self.__writebuffer = ""
        self.__readlimit = -1
        self.__readlimitnext = -1
        self.__evrlimit = None
        self.__writelimit = -1
        self.__writelimitnext = -1
        self.__evwlimit = None
        self.__setrtimeout = 0
        self.__setwtimeout = 0
        self.__closed = 0
        self.__ev = event(self.__sock)
        self.__ev.add_read(self.__readhandler)

    def set_config(self, conf):
        self.__readlimit = conf["readlimit"]
        if self.__readlimit > 0:
            self.__readlimitnext = self.__readlimit
            self.__evrlimit = event(self, self.__sock)
            self.__evrlimit.add_timer(1000, self.__timeouthandler)

        self.__writelimit = conf["writelimit"]
        if self.__writelimit > 0:
            self.__writelimitnext = self.__writelimit
            self.__evwlimit = event(self, self.__sock)
            self.__evwlimit.add_timer(1000, self.__timeouthandler)

    def set_recvmsg(self, recvmsghandler):
        self.__recvmsghandler = recvmsghandler

    def set_broken(self, brokenhandler):
        self.__brokenhandler = brokenhandler

    def read(self, size=-1):
        if size == -1:
            buf = self.__readbuffer
        else:
            size = min(size, len(self.__readbuffer))
            buf = self.__readbuffer[0: size]

        size = len(buf)
        self.__readbuffer = self.__readbuffer[size:]
        return buf

    def write(self, buf):
        self.__writebuffer += buf
        self.__send()

    def close(self):
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, self.__linger)
        self.__sock.close()

    def __readhandler(self, ev):
        ret, nread = self.__recv()
        if ret != tcpconnection.ERROR:
            if nread > 0 and hasattr(self, '_tcpconnection__recvmsghandler'):
                self.__recvmsghandler(self)
            elif self.__closed:
                self.__broken()

    def __writehandler(self, ev):
        self.__ev.del_write()
        self.write("")

    def __timeouthandler(self, ev):
        if ev == self.__evrlimit:
            if self.__setrtimeout:
                self.__setrtimeout = 0
                self.__ev.add_read(self.__readhandler)
            self.__readlimitnext = self.__readlimit
            self.__evrlimit.add_timer(1000, self.__timeouthandler)

        if ev == self.__evwlimit:
            if self.__setwtimeout:
                self.__setwtimeout = 0
                self.__writelimitnext = self.__writelimit
                self.__evwlimit.add_timer(1000, self.__timeouthandler)
                self.write("")
            else:
                self.__writelimitnext = self.__writelimit
                self.__evwlimit.add_timer(1000, self.__timeouthandler)

    def __recv(self):
        if self.__closed:
            self.__broken()

        sock = self.__sock
        nread = 0
        ret = tcpconnection.OK
        if -1 == self.__readlimit:
            size = self.__recvbuf
        else:
            size = min(self.__recvbuf, self.__readlimitnext)

        while 1:
            try:
                data = sock.recv(size)
                self.__readbuffer += data
                nread += len(data)
                self.__readlimitnext -= len(data)

                if len(data) == 0:
                    self.__closed = 1

                if len(data) < size:
                    break

                if self.__readlimitnext == 0:
                    self.__setrtimeout = 1
                    self.__evrlimit.add_timer(1000, self.__timeouthandler)
                    self.__ev.del_read()

                if self.__readlimitnext > 0:
                    size = min(self.__readbuffer, self.__readlimitnext)

            except socket.error, e:
                if e.errno == errno.EINTR:
                    sys.stdout.write("Interrupt when recv data from socket\n")
                    continue
                elif e.errno == errno.EAGAIN:
                    ret = tcpconnection.AGAIN
                    break
                else:
                    data = ""
                    ret = tcpconnection.ERROR
                    self.__closed = 1
                    self.__broken()
                    break
            except Exception, e:
                self.__closed = 1
                self.__broken()
                raise e

        return (ret, nread)


    def __send(self):
        if self.__closed:
            self.__closed = 1
            self.__broken()
            return (tcpconnection.ERROR, 0)

        if self.__setwtimeout:
            return (tcpconnection.AGAIN, 0)

        sock = self.__sock
        nwrite = 0
        ret = tcpconnection.OK

        while 1:
            if self.__writelimit == -1:
                data = self.__writebuffer
            else:
                size = min(len(self.__writebuffer), self.__writelimitnext)
                data = self.__writebuffer[0:size]
            try:
                sock.sendall(data)
                nwrite = len(data)
                self.__writebuffer = self.__writebuffer[nwrite:]
                self.__writelimitnext -= nwrite
                if self.__writelimitnext == 0:
                    self.__setwtimeout = 1
                    self.__evwlimit.add_timer(1000, self.__timeouthandler)
                break
            except socket.errno, e:
                if e.errno == errno.EINTR:
                    sys.stdout.write("Interrupt when send data to socket\n")
                    continue
                elif e.errno == errno.EAGAIN:
                    ret = tcpconnection.AGAIN
                    self.__ev.add_write(self.__writehandler)
                    break
                else:
                    ret = tcpconnection.ERROR
                    self.__closed = 1
                    self.__broken()
                    break
            except Exception, e:
                raise e
        
        return (ret, nwrite)

    def __broken(self):
        self.__ev.del_read()
        self.__ev.del_write()
        if self.__evrlimit != None:
            self.__evrlimit.del_timer()
        if self.__evwlimit != None:
            self.__evwlimit.del_timer()
        if hasattr(self, '_tcpconnection__brokenhandler'):
            self.__brokenhandler(self)
