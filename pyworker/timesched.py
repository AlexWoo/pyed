import time
from slpscheduler import slpscheduler


def register_timesched(slpsm):
    slpsm.register("timesched", timesched)


class timesched(slpscheduler):
    def __init__(self, slpsm, srvname, begintime=0, interval=1, maxcount=1):
        slpscheduler.__init__(self, slpsm, srvname)
        self._slpsm.data.initdata(srvname, begintime, interval, maxcount)

    def _setdata(self, srvname, nexttime, srvlist):
        self._slpsm.data.setdata(srvname, nexttime, srvlist)

    def _query(self):
        return self._slpsm.data.getdata(self._srvname)

    def _release(self):
        self._slpsm.data.releasedata(self._srvname, self._nt)

    def _del(self):
        self._slpsm.data.deletedata(self._srvname, self._nt)

    def callslp(self):
        nexttime, srvlist = self._query()
        if not nexttime:
            return False, None
        else:
            self._nt = nexttime
            return True, srvlist

    def endslp(self, ret, nexttime, srvdict):
        if ret == -1:
            self._release()
            return
        if ret == 0:
            self._del()
            nt = time.time() + float(nexttime)/1000
            for k, v in srvdict.iteritems():
                self._setdata(k, nt, v)

if __name__ == "__main__":
    from pysys.pylog import pylog
    from slpscheduler import slpschedmanager
    log = pylog("timesched.log")
    slpsm = slpschedmanager(log, {}) # for this test, slpschedmanager and scheddata must not register cmd

    print slpsm._conf
    register_timesched(slpsm)
    print slpsm._conf

    slp1 = slpsm.create("slp1", "timesched", time.time()-600, 5, 4)
    slp21 = slpsm.create("slp21", "timesched", time.time()-600, 5, 4)
    slp22 = slpsm.create("slp22", "timesched", 0, 0, 4)
    print slpsm.data.displaydata()

    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    tr1, sl1 = slp1.callslp()
    print tr1, sl1
    tr2, sl2 = slp1.callslp()
    print tr2, sl2
    tr3, sl3 = slp1.callslp()
    print tr3, sl3
    tr4, sl4 = slp1.callslp()
    print tr4, sl4
    print slpsm.data.displaydata()

    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    srvdict={
        "slp22": (10, "Hello", "World"),
        "slp23": (5, "test"),
    }
    tr1, sl1 = slp21.callslp()
    print tr1, sl1
    slp21.endslp(-1, 0, srvdict)
    print slpsm.data.displaydata()

    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    tr2, sl2 = slp21.callslp()
    print tr2, sl2
    slp21.endslp(0, 0, srvdict)
    print slpsm.data.displaydata()

    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    tr3, sl3 = slp22.callslp()
    print tr3, sl3
    print slpsm.data.displaydata()
    
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    slp22.endslp(0, 0, {})
    print slpsm.data.displaydata()
