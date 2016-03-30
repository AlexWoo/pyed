import sys, socket, errno
from struct import pack
from event import event


class tcpconnection(object):
    OK = 0
    ERROR = -1
    AGAIN = -2
    
    def __init__(self, sock, srvconf, evs, tms):
        self._evs = evs
        self._tms = tms
        self._sock = sock

        self._blocking = 0
        if srvconf.has_key("blocking"):
            self._blocking = srvconf["blocking"]

        self._recvbuf = 8092
        if srvconf.has_key("recvbuf"):
            self._recvbuf = srvconf["recvbuf"]

        self._sendbuf = 8092
        if srvconf.has_key("sendbuf"):
            self._sendbuf = srvconf["sendbuf"]

        self._linger = pack("ii", 0, 0)
        if srvconf.has_key("linger"):
            self._linger = pack("ii", srvconf["linger"][0], srvconf["linger"][1])

        self._sock.setblocking(self._blocking)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self._recvbuf)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self._sendbuf)

        self._readbuffer = ""
        self._writebuffer = ""
        self._readlimit = -1
        self._readlimitnext = -1
        self._evrlimit = None
        self._writelimit = -1
        self._writelimitnext = -1
        self._evwlimit = None
        self._setrtimeout = 0
        self._setwtimeout = 0
        self._closed = 0
        self._ev = event(evs, tms, self._sock)
        self._ev.add_read(self._readhandler)

        self._recvmsghandler = None
        self._brokenhandler = None

    def set_config(self, conf):
        self._readlimit = conf["readlimit"]
        if self._readlimit > 0:
            self._readlimitnext = self._readlimit
            self._evrlimit = event(self._evs, self._tms, self._sock)
            self._evrlimit.add_timer(1000, self._timeouthandler)

        self._writelimit = conf["writelimit"]
        if self._writelimit > 0:
            self._writelimitnext = self._writelimit
            self._evwlimit = event(self._evs, self._tms, self._sock)
            self._evwlimit.add_timer(1000, self._timeouthandler)

    def set_recvmsg(self, recvmsghandler):
        self._recvmsghandler = recvmsghandler

    def set_broken(self, brokenhandler):
        self._brokenhandler = brokenhandler

    def read(self, size=-1):
        if size == -1:
            buf = self._readbuffer
        else:
            size = min(size, len(self._readbuffer))
            buf = self._readbuffer[0: size]

        size = len(buf)
        self._readbuffer = self._readbuffer[size:]
        return buf

    def write(self, buf):
        self._writebuffer += buf
        self._send()

    def close(self):
        self._ev.del_read()
        self._ev.del_write()
        if self._evrlimit != None:
            self._evrlimit.del_timer()
        if self._evwlimit != None:
            self._evwlimit.del_timer()
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, self._linger)
        self._sock.close()

    def _readhandler(self, ev):
        ret, nread = self._recv()
        if ret != tcpconnection.ERROR:
            if nread > 0 and self._recvmsghandler != None:
                self._recvmsghandler(self)
            elif self._closed:
                self._broken()

    def _writehandler(self, ev):
        self._ev.del_write()
        self.write("")

    def _timeouthandler(self, ev):
        if ev == self._evrlimit:
            if self._setrtimeout:
                self._setrtimeout = 0
                self._ev.add_read(self._readhandler)
            self._readlimitnext = self._readlimit
            self._evrlimit.add_timer(1000, self._timeouthandler)

        if ev == self._evwlimit:
            if self._setwtimeout:
                self._setwtimeout = 0
                self._writelimitnext = self._writelimit
                self._evwlimit.add_timer(1000, self._timeouthandler)
                self.write("")
            else:
                self._writelimitnext = self._writelimit
                self._evwlimit.add_timer(1000, self._timeouthandler)

    def _recv(self):
        if self._closed:
            self._broken()

        sock = self._sock
        nread = 0
        ret = tcpconnection.OK
        if -1 == self._readlimit:
            size = self._recvbuf
        else:
            size = min(self._recvbuf, self._readlimitnext)

        while 1:
            try:
                data = sock.recv(size)
                self._readbuffer += data
                nread += len(data)
                self._readlimitnext -= len(data)

                if len(data) == 0:
                    self._closed = 1

                if len(data) < size:
                    break

                if self._readlimitnext == 0:
                    self._setrtimeout = 1
                    self._evrlimit.add_timer(1000, self._timeouthandler)
                    self._ev.del_read()

                if self._readlimitnext > 0:
                    size = min(self._readbuffer, self._readlimitnext)

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
                    self._closed = 1
                    self._broken()
                    break
            except Exception, e:
                self._closed = 1
                self._broken()
                raise e

        return (ret, nread)


    def _send(self):
        if self._closed:
            self._closed = 1
            self._broken()
            return (tcpconnection.ERROR, 0)

        if self._setwtimeout:
            return (tcpconnection.AGAIN, 0)

        sock = self._sock
        nwrite = 0
        ret = tcpconnection.OK

        while 1:
            if self._writelimit == -1:
                data = self._writebuffer
            else:
                size = min(len(self._writebuffer), self._writelimitnext)
                data = self._writebuffer[0:size]
            try:
                sock.sendall(data)
                nwrite = len(data)
                self._writebuffer = self._writebuffer[nwrite:]
                self._writelimitnext -= nwrite
                if self._writelimitnext == 0:
                    self._setwtimeout = 1
                    self._evwlimit.add_timer(1000, self._timeouthandler)
                break
            except socket.errno, e:
                if e.errno == errno.EINTR:
                    sys.stdout.write("Interrupt when send data to socket\n")
                    continue
                elif e.errno == errno.EAGAIN:
                    ret = tcpconnection.AGAIN
                    self._ev.add_write(self._writehandler)
                    break
                else:
                    ret = tcpconnection.ERROR
                    self._closed = 1
                    self._broken()
                    break
            except Exception, e:
                raise e
        
        return (ret, nwrite)

    def _broken(self):
        self._ev.del_read()
        self._ev.del_write()
        if self._evrlimit != None:
            self._evrlimit.del_timer()
        if self._evwlimit != None:
            self._evwlimit.del_timer()
        if self._brokenhandler != None:
            self._brokenhandler(self)
