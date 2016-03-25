from time import time


class timers(object):
    def __init__(self):
        self._timers = []
        self._timeinterval = 1000

    def addtimer(self, ev, timeout):   
        if len(self._timers) == 0:
            self._timers.append(ev)
            return

        beg, end = 0, len(self._timers)
        idx = (beg + end) / 2

        while True:
            if beg == idx:
                if self._timers[beg].timeout < timeout:
                    self._timers.insert(idx + 1, ev)
                else:
                    self._timers.insert(idx, ev)
                return

            if self._timers[idx].timeout > timeout:
                end = idx
                idx = (beg + end) / 2
            elif self._timers[idx].timeout < timeout:
                beg = idx
                idx = (beg + end) / 2
            else:
                self._timers.insert(idx, ev)
                return

    def processtimer(self):
        currtime = time()
        idx = 0
        for ev in self._timers:
            if ev.timeout() > currtime:
                break
            idx += 1

            if not ev.timerset():
                continue

            ev.timeouthandler(ev)

        self._timers = self._timers[idx:]
        if len(self._timers) > 0:
            currtime = time()
            difftime = self._timers[0].timeout() - currtime
            if difftime < self._timeinterval:
                return difftime * 1000

        return self._timeinterval
    
    def printtimers(self):
        print "["
        for ev in self._timers:
            print "\t", ev, ev.timeout()
        print "]"
