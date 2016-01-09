from select import select


class events_select(object):
    EVENT_READ = 1
    EVENT_WRITE = 2
    __instance = None
    __firstinit = 1

    def __new__(cls, *args, **kwargs):
        if events_select.__instance == None:
            events_select.__instance = object.__new__(cls, *args, **kwargs)
        return events_select.__instance

    def __init__(self):
        if not events_select.__firstinit:
            return
        events_select.__firstinit = 0

        self.__events = {}
        self.__rlist = []
        self.__wlist = []

    def addevent(self, fd, ev, etype):
        if etype & events_select.EVENT_READ:
            self.__rlist.append(fd)

        if etype & events_select.EVENT_WRITE:
            self.__wlist.append(fd)

        self.__events[fd] = ev

    def delevent(self, fd, etype):
        if etype & events_select.EVENT_READ:
            self.__rlist.remove(fd)
            etype = etype & 0xFE

        if etype & events_select.EVENT_WRITE:
            self.__wlist.remove(fd)
            etype = etype & 0xFD

        if etype == 0:
            del self.__events[fd]

    def processevent(self, ms):
        rlist, wlist, _ = select(self.__rlist, self.__wlist, [], float(ms) / 1000)
        for fd in rlist:
            ev = self.__events[fd]
            ev.readhandler(ev)

        for fd in wlist:
            ev = self.__events[fd]
            ev.writehandler(ev)
