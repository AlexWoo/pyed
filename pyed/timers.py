from time import time


class timers(object):
    __instance = None
    __firstinit = 1

    # for singleton
    def __new__(cls, *args, **kwargs):
        if timers.__instance == None:
            timers.__instance = object.__new__(cls, *args, **kwargs)
        return timers.__instance

    def __init__(self):
        if not timers.__firstinit:
            return
        timers.__firstinit = 0

        self.__timers = []

    def addtimer(self, ev, timeout):
        if len(self.__timers) == 0:
            self.__timers.append(ev)
            return

        beg, end = 0, len(self.__timers)
        idx = (beg + end) / 2

        while True:
            if beg == idx:
                if self.__timers[beg].timeout < timeout:
                    self.__timers.insert(idx + 1, ev)
                else:
                    self.__timers.insert(idx, ev)
                return

            if self.__timers[idx].timeout > timeout:
                end = idx
                idx = (beg + end) / 2
            elif self.__timers[idx].timeout < timeout:
                beg = idx
                idx = (beg + end) / 2
            else:
                self.__timers.insert(idx, ev)
                return

    def processtimer(self):
        currtime = time()
        idx = 0
        for ev in self.__timers:
            if ev.timeout() > currtime:
                break
            idx += 1

            if not ev.timerset():
                continue

            ev.timeouthandler(ev)

        __timers = self.__timers[idx:]
        if len(__timers) > 0:
            currtime = time()
            return (__timers[0].timeout() - currtime) * 1000
        else:
            return 50
    
    def printtimers(self):
        print "["
        for ev in self.__timers:
            print "\t", ev, ev.timeout()
        print "]"
