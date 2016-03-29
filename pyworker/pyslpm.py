import traceback, time
from pysys.pyloader import pyloader
from pyslp import pyslp
from pyevent.event import event


class pyslpm(object):
    def __init__(self, evs, tms, log):
        self._slps = {}
        self._timeout = {}
        self.log = log
        self.ev = event(evs, tms)
        self.loader = pyloader(log)

    def loadslp(self, modulename, filepath):
        m = self.loader.load(modulename, filepath)
        if m == None:
            self.log.logError("Pyslpm", "compile module[%s:%s] failed: %s"
                % (filepath, modulename, traceback.format_exc()))
            return
        try: # load module in slp
            slp = pyslp(self.log, self.loader, m)
        except:
            self.log.logError("Pyslpm", "load module[%s:%s] failed: %s"
                % (filepath, modulename, traceback.format_exc()))
            return
        timeout = time.time() + 1 # delay 1 sec to run slp
        self._slps[modulename] = slp
        self._slps[modulename] = timeout
        if self.ev.timeout() > timeout:
            self.ev.add_timer(timeout, self.runslp)

    def unloadslp(self, modulename):
        if self._slps.has_key(modulename):
            del self._slps[modulename]
    
    def updateslp(self, modulename, filepath):
        self.unloadslp(modulename)
        self.loadslp(modulename, filepath)

    def runslp(self, ev):
        to = 0
        while 1:
            nowtime = time.time()
            count = 0
            for name, slp in self._slps.iteritems():
                if self._timeout[name] < nowtime:
                    ret, timeout = slp.runslp()
                    if to == 0:
                        to = timeout
                    elif to < timeout:
                        to = timeout
                    count += 1
                    if ret == -1:
                        self._timeout[name] = timeout
                    else:
                        self._timeout[name] = nowtime
            if count == 0:
                break
        if to == 0:
            tolist = self._timeout.itervalues()
            tolist.sort()
            self.ev.add_timer(tolist[0], self.runslp)
        else:
            self.ev.add_timer(to, self.runslp)

if __name__ == "__main__":
    from pysys.pylog import pylog
    log = pylog("/Users/wujie/Work/Github/pyed/log/test.log")
    slpm = pyslpm(log)
    slpm.loadslp("test", "/Users/wujie/Work/Github/pyed/test/init.py")