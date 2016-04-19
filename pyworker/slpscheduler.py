import os, traceback
from scheddata import scheddata


class slpschedmanager(object):
    def __init__(self, log, loader, cmd):
        self._log = log
        self._loader = loader
        self._conf = {}
        self.data = scheddata(cmd)
        schedcmd = {
            "loadsched": self.loadsched,
            "displaysched": self.displaysched
        }
        cmd.registercmd(schedcmd)

    def register(self, schedtype, scheclass):
        self._conf[schedtype] = scheclass

    def create(self, srvname, schedtype=None, *args):
        if schedtype in self._conf:
            return self._conf[schedtype](self, srvname, *args)
        else:
            return slpscheduler(self, srvname)

    def loadsched(self, path):
        try:
            modulename = os.path.basename(path).split('.')[0]
            m = self._loader.load(modulename, path)
            m.register(self)
            return "load sched " + modulename + " success!"
        except:
            return "load sched " + modulename + " failed!\n" + traceback.format_exc()

    def displaysched(self):
        retstr = "sched load in system:\n"
        for k, v in self._conf.iteritems():
            retstr += (k + ":\t" + str(v))
        return retstr

class slpscheduler(object):
    def __init__(self, slpsm, srvname):
        self._slpsm = slpsm
        self._srvname = srvname

    def _setdata(self, srvname, nexttime, srvlist):
        pass

    def _query(self):
        return True, None

    def _release(self):
        pass

    def callslp(self):
        return True, None

    def endslp(self, ret, nexttime, srvdict):
        pass
