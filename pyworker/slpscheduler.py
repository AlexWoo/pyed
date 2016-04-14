import time


class scheddata(object):
    """
    _srv = {
        "srvname1": {
            nexttime1: [srvlist, occupied],
            nexttime2: [srvlist, occupied],
            nexttime3: [srvlist, occupied],
            ...
        },
        "srvname2": {
            nexttime1: [srvlist, occupied],
            nexttime2: [srvlist, occupied],
            nexttime3: [srvlist, occupied],
            ...
        },
        ...
    }
    """
    def __init__(self):
        self._srv = {}

    def setdata(self, srvname, nexttime, srvlist):
        if srvname not in self._srv:
            self._srv[srvname] = {}
        if nexttime not in self._srv[srvname]:
            self._srv[srvname][nexttime] = []
            self._srv[srvname][nexttime].extend([srvlist, False])
        else:
            self._srv[srvname][nexttime][0] = srvlist
            self._srv[srvname][nexttime][1] = False

    def releasedata(self, srvname, nexttime):
        if srvname in self._srv and nexttime in self._srv[srvname]:
            self._srv[srvname][nexttime][1] = False

    def getdata(self, srvname):
        if srvname not in self._srv:
            return None, None
        now = time.time()
        for k, v in self._srv[srvname].iteritems():
            if k < now and not v[1]:
                v[1] = True
                return k, v[0]
        return None, None

class slpschedmanager(object):
    def __init__(self, pesys):
        self._log = pesys.log
        self._loader = pesys.loader
        self._conf = {}
        self.data = scheddata()

    def register(self, schedtype, scheclass):
        self._conf[schedtype] = scheclass

    def create(self, srvname, schedtype):
        if schedtype in self._conf:
            return self._conf[schedtype](self, srvname)
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

class timesched(slpscheduler):
    def __init__(self, slpsm, srvname):
        slpscheduler.__init__(self, slpsm, srvname)

    def _setdata(self, srvname, nexttime, srvlist):
        self._slpsm.data.setdata(self._srvname, nexttime, srvlist)

    def _query(self):
        self._slpsm.data.getdata(self._srvname)

    def _release(self):
        self._slpsm.data.releasedata(self._srvname, self._nt)

    def callslp(self):
        nexttime, srvlist = self._query()
        if srvlist:
            self._nt = nexttime
            return True, srvlist
        else:
            return False, None

    def endslp(self, ret, nexttime, srvdict):
        if ret == -1:
            self._release()
        if ret == 0:
            nt = time.time() + float(nexttime)/1000
            for k, v in srvdict.iteritems():
                self._setdata(k, nt, v)
