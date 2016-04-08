from select import select


class events_select(object):
    EVENT_READ = 1
    EVENT_WRITE = 2

    def __init__(self):
        self._events = {}
        self._rlist = []
        self._wlist = []

    def addevent(self, fd, ev, etype):
        if etype & events_select.EVENT_READ:
            self._rlist.append(fd)

        if etype & events_select.EVENT_WRITE:
            self._wlist.append(fd)

        self._events[fd] = ev

    def delevent(self, fd, etype):
        if etype & events_select.EVENT_READ:
            self._rlist.remove(fd)
            etype = etype & 0xFE

        if etype & events_select.EVENT_WRITE:
            self._wlist.remove(fd)
            etype = etype & 0xFD

        if etype == 0:
            del self._events[fd]

    def processevent(self, ms):
        rlist, wlist, _ = select(self._rlist, self._wlist, [], float(ms) / 1000)
        for fd in rlist:
            ev = self._events[fd]
            ev.readhandler(ev)

        for fd in wlist:
            ev = self._events[fd]
            ev.writehandler(ev)
