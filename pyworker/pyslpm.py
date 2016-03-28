import time
from pysys.pyloader import pyloader
from pyslp import pyslp


class pyslpm(object):
    def __init__(self, log):
        self._slps = {}
        self.log = log
        self.loader = pyloader(log)

    def loadslp(self, modulename, filepath):
        print time.time()
        m = self.loader.load(modulename, filepath)
        print time.time()
        print dir(m)
        if m == None:
            self.log.logError("Pyslpm", "compile module[%s] failed, filepath: %s"
                % (modulename, filepath))
            return
        try: # load module in slp
            slp = pyslp(self.log, self.loader, m)
        except:
            self.log.logError("Pyslpm", "load module[%s] failed, filepath: %s"
                % (modulename, filepath))
            return
        self._slps[modulename] = slp
    
    def unloadslp(self, modulename):
        if self._slps.has_key(modulename):
            del self._slps[modulename]
    
    def updateslp(self, modulename, filepath):
        self.unloadslp(modulename)
        self.loadslp(modulename, filepath)

if __name__ == "__main__":
    from pysys.pylog import pylog
    log = pylog("/Users/wujie/Work/Github/pyed/log/test.log")
    slpm = pyslpm(log)
    slpm.loadslp("conf", "/Users/wujie/Work/Github/pyed/conf/pyed.conf")