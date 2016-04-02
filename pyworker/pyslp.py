import traceback, time
from corouting import coroutine


class pyslp(object):
    def __init__(self, log, loader, m):
        self.stop = False
        self._slps = {}
        self._enter = []
        self._chains = []
        self._idx = 0
        self._loader = loader
        self._log = log
        self._nexttime = time.time()
        self._loadmodule(m)

    def _loadmodule(self, m):
        for name, item in m.modulelist.iteritems():
            path = item[0]
            funcname = item[1]
            isEnter = item[2]
            script = self._loader.load(name, path)
            func = getattr(script, funcname)
            self._slps[name] = coroutine(self._log, func, self)
            if isEnter:
                self._enter.append(name)
        m.init(self)

    '''
    func return (state, timeinterval, nextlist)
        state:
            -2: slp stop, it will delete from slpm
            -1: will exe from curr nexttime
             0: will exe from init nexttime
             1: will exe nextlist nexttime
        timeinterval:
            time(s) interval to exe next func, 0 for run right now
        nextlist:
            next func module name list like ("splittask1", "splittask2")
    '''
    def run(self):
        try:
            nexttime = 0
            if self._idx == 0:
                self._chains = self._enter[:]
            while self._idx < len(self._chains):
                name = self._chains[self._idx]
                code, interval, nextlist = self._slps[name].wait()
                print code, interval, nextlist
                nt = time.time() + interval
                if nexttime == 0 or nexttime > nt:
                    nexttime = nt
                if code == -2:
                    self.stop = True
                    self._nexttime = nexttime
                    return
                elif code == -1:
                    self._nexttime = nexttime
                    return
                elif code == 0:
                    self._idx = 0
                    self._nexttime = nexttime
                    return
                else:
                    for n in nextlist:
                        self._chains.append(n)
                    self._idx += 1
            self._idx = 0
            self._nexttime = nexttime
        except:
            self._log.logError("Pyslp", "Run SLP Error: %s" % traceback.format_exc())
            self._idx = 0
            self._nexttime = time.time()

    def getnexttime(self):
        return self._nexttime

    def lsslp(self):
        retstr = ""
        for m in self._steps:
            retstr = retstr + m + "\r\n"
        return retstr
