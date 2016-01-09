from select import EPOLLIN, EPOLLOUT, EPOLLHUP, EPOLLET, epoll

class events_epoll(object):
    EVENT_READ = 1
    EVENT_WRITE = 2
    __instance = None
    __firstinit = 1

    def __new__(cls, *args, **kwargs):
        if events_epoll.__instance == None:
            events_epoll.__instance = object.__new__(cls, *args, **kwargs)
        return events_epoll.__instance

    def __init__(self):
        if not events_epoll.__firstinit:
            return
        events_epoll.__firstinit = 0

        self.__ep = epoll()
        self.__events = {}
    
    def addevent(self, fd, ev, etype):
        if fd in self.__events.keys():
            et = self.__events[fd][0]
            newe = 0
        else:
            et = EPOLLET
            self.__events[fd] = [EPOLLET, ev]
            newe = 1

        if etype & events_epoll.EVENT_READ:
            et |= (EPOLLIN | EPOLLHUP)
        
        if etype & events_epoll.EVENT_WRITE:
            et |= EPOLLOUT

        self.__events[fd][0] = et
        self.__events[fd][1] = ev

        if newe:
            self.__ep.register(fd, et)
        else:
            self.__ep.modify(fd, et)

    def delevent(self, fd, etype):
        if fd not in self.__events.keys():
            return
        et = self.__events[fd][0]

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
            self.__ep.unregister(fd)
            del self.__events[fd]
        else:
            self.__ep.modify(fd, et)
            self.__events[fd][0] = et

    def processevent(self, ms):
        elist = self.__ep.poll(float(ms) / 1000)
        for e in elist:
            fd = e[0]
            etype = e[1]
            ev = self.__events[fd][1]
            if etype & (EPOLLIN | EPOLLHUP):
                ev.readhandler(ev)
            if etype & EPOLLOUT:
                ev.writehandler(ev)
