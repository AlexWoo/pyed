from timers import timers
try:
    from pyevent.events_epoll import events_epoll as events
except:
    from pyevent.events_select import events_select as events
from time import time


class event:
    def __init__(self, evs, tms, sock=None):
        self.sock = sock
        if sock != None:
            self._fd = sock.fileno()
        else:
            self._fd = -1
        self._evs = evs
        self._tms = tms

        self._timeout = -1
        self._timerset = 0
        self._readset = 0
        self._writeset = 0

        self.readhandler = None
        self.writehandler = None
        self.timeouthandler = None

    def add_read(self, readhandler):
        self.readhandler = readhandler
        if 0 == self._readset:
            self._readset = 1
            self._evs.addevent(self._fd, self, events.EVENT_READ)

    def del_read(self):
        if 1 == self._readset:
            self._readset = 0
            self._evs.delevent(self._fd, events.EVENT_READ)

    def add_write(self, writehandler):
        self.writehandler = writehandler
        if 0 == self._writeset:
            self._writeset = 1
            self._evs.addevent(self._fd, self, events.EVENT_WRITE)

    def del_write(self):
        if 1 == self._writeset:
            self._writeset = 0
            self._evs.addevent(self._fd, events.EVENT_WRITE)

    def add_timer(self, timeout, timeouthandler):
        self._timeout = time() + timeout / 1000
        self._timerset = 1
        self.timeouthandler = timeouthandler
        self._tms.addtimer(self, self._timeout)

    def del_timer(self):
        self._timerset = 0

    def timerset(self):
        return self._timerset

    def timeout(self):
        return self._timeout
