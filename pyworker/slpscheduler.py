from scheddata import scheddata


class slpschedmanager(object):
    def __init__(self, log, cmd):
        self._log = log
        self._conf = {}
        self.data = scheddata(cmd)

    def register(self, schedtype, scheclass):
        self._conf[schedtype] = scheclass

    def create(self, srvname, schedtype=None, *args):
        if schedtype in self._conf:
            return self._conf[schedtype](self, srvname, *args)
        else:
            return slpscheduler(self, srvname)

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
