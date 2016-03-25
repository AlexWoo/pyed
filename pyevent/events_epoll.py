from select import EPOLLIN, EPOLLOUT, EPOLLHUP, EPOLLET, epoll

class events_epoll(object):
    def __init__(self):
        self._ep = epoll()
        self._events = {}
    
    def addevent(self, fd, ev, etype):
        if fd in self._events.keys():
            et = self._events[fd][0]
            newe = 0
        else:
            et = EPOLLET
            self._events[fd] = [EPOLLET, ev]
            newe = 1

        if etype & events_epoll.EVENT_READ:
            et |= (EPOLLIN | EPOLLHUP)
        
        if etype & events_epoll.EVENT_WRITE:
            et |= EPOLLOUT

        self._events[fd][0] = et
        self._events[fd][1] = ev

        if newe:
            self._ep.register(fd, et)
        else:
            self._ep.modify(fd, et)

    def delevent(self, fd, etype):
        if fd not in self._events.keys():
            return
        et = self._events[fd][0]

        delete = 0
        if etype & events_epoll.EVENT_READ:
            if et & EPOLLOUT:
                et = EPOLLET & EPOLLOUT
            else:
                delete = 1

        if etype & events_epoll.EVENT_WRITE:
            if et & (EPOLLIN | EPOLLHUP):
                et = EPOLLET & EPOLLIN | EPOLLHUP
            else:
                delete = 1

        if delete:
            self._ep.unregister(fd)
            del self._events[fd]
        else:
            self._ep.modify(fd, et)
            self._events[fd][0] = et

    def processevent(self, ms):
        elist = self._ep.poll(float(ms) / 1000)
        for e in elist:
            fd = e[0]
            etype = e[1]
            ev = self._events[fd][1]
            if etype & (EPOLLIN | EPOLLHUP):
                ev.readhandler(ev)
            if etype & EPOLLOUT:
                ev.writehandler(ev)
