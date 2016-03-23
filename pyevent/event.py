from pyed.timers import timers
try:
    from pyed.events_epoll import events_epoll as events
except:
    from pyed.events_select import events_select as events
from time import time


class event:
    def __init__(self, sock=None):
        self.sock = sock
        if sock != None:
            self.__fd = sock.fileno()
        else:
            self.__fd = -1
        self.__timeout = -1
        self.__timerset = 0
        self.__readset = 0
        self.__writeset = 0

    def add_read(self, readhandler):
        self.readhandler = readhandler
        if 0 == self.__readset:
            evs = events()
            self.__readset = 1
            evs.addevent(self.__fd, self, events.EVENT_READ)

    def del_read(self):
        if 1 == self.__readset:
            evs = events()
            self.__readset = 0
            evs.delevent(self.__fd, events.EVENT_READ)

    def add_write(self, writehandler):
        self.writehandler = writehandler
        if 0 == self.__writeset:
            evs = events()
            self.__writeset = 1
            evs.addevent(self.__fd, self, events.EVENT_WRITE)

    def del_write(self):
        if 1 == self.__writeset:
            evs = events()
            self.__writeset = 0
            evs.addevent(self.__fd, events.EVENT_WRITE)

    def add_timer(self, timeout, timeouthandler):
        tms = timers()
        self.__timeout = time() + timeout / 1000
        self.__timerset = 1
        self.timeouthandler = timeouthandler
        tms.addtimer(self, self.__timeout)

    def del_timer(self):
        self.__timerset = 0

    def timerset(self):
        return self.__timerset

    def timeout(self):
        return self.__timeout