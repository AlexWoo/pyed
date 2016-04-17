import time


class scheddata(object):
    """
    _srv = {
        "srvname1": {
            "begintime": 1460689440,
            "interval": 1, # measured by minutes
            "maxcount": 4,
            "processing": {
                nexttime1: [srvlist, occupied],
                nexttime2: [srvlist, occupied],
                nexttime3: [srvlist, occupied],
                ...
            }
        },
        "srvname2": {
            "begintime": 0,
            "interval": 1, # measured by minutes
            "maxcount": 4,
            "processing": {
                nexttime1: [srvlist, occupied],
                nexttime2: [srvlist, occupied],
                nexttime3: [srvlist, occupied],
                ...
            }
        },
        ...
    }
    if begintime is 0, interval is nonsense
    if begintime is time, interval is used to calculate next begintime
    maxcount limit elements number of processing
    processing is list of data to process now
    if processing number is less than maxcount, getdata will new new a nexttime if begintime is not 0
    """
    def __init__(self):
        self._srv = {}

    def initdata(self, srvname, begintime=0, interval=1, maxcount=1):
        if srvname in self._srv:
            if begintime < 0 or interval <=0:
                return ("add data " + srvname + ", begintime: " + str(begintime)
                        + ", interval: " + str(interval) + ", maxcount: " + str(maxcount)
                        + " failed!!")
        else:
            self._srv[srvname] = {}
            
        if begintime == 0:
            self._srv[srvname]["begintime"] = begintime
            self._srv[srvname]["interval"] = 0
        else:
            interval *= 60
            begintime = int(begintime) - int(begintime) % interval
            self._srv[srvname]["begintime"] = begintime
            self._srv[srvname]["interval"] = interval
        self._srv[srvname]["maxcount"] = maxcount
        self._srv[srvname]["processing"] = {}
        return ("add data " + srvname + ", begintime: " + str(begintime)
                + ", interval: " + str(interval) + ", maxcount: " + str(maxcount)
                + " ok!!")

    def _displaydata(self, srvname):
        retstr = ""
        if srvname in self._srv:
            retstr += (srvname + ":\n")
            retstr += ("\t" + "begintime: " + str(self._srv[srvname]["begintime"]) + "\n")
            retstr += ("\t" + "interval: " + str(self._srv[srvname]["interval"]) + "\n")
            retstr += ("\t" + "maxcount: " + str(self._srv[srvname]["maxcount"]) + "\n")
            retstr += ("\t" + "processing:\n")
            for k, v in self._srv[srvname]["processing"].iteritems():
                retstr += ("\t\t" + str(k) + "\t" + str(v[0]) + "\t" + str(v[1]) + "\n")
        return retstr 

    def displaydata(self, srvname=None):
        retstr = ""
        if not srvname:
            for k in self._srv.iterkeys():
                retstr += self._displaydata(k)
            return retstr
        else:
            return self._displaydata(srvname)

    def setdata(self, srvname, nexttime, srvlist):
        if srvname not in self._srv:
            self._srv[srvname] = {}
        if nexttime not in self._srv[srvname]["processing"]:
            self._srv[srvname]["processing"][nexttime] = []
            self._srv[srvname]["processing"][nexttime].extend([srvlist, False])
        else:
            self._srv[srvname]["processing"][nexttime][0] = srvlist
            self._srv[srvname]["processing"][nexttime][1] = False

    def releasedata(self, srvname, nexttime):
        if srvname in self._srv and nexttime in self._srv[srvname]["processing"]:
            self._srv[srvname]["processing"][nexttime][1] = False

    def getdata(self, srvname):
        if srvname not in self._srv:
            return None, None
        if self._srv[srvname]["begintime"] != 0 and len(self._srv[srvname]["processing"]) < self._srv[srvname]["maxcount"]:
            nexttime = self._srv[srvname]["begintime"]
            interval = self._srv[srvname]["interval"]
            begintime = nexttime + interval
            begintime = int(begintime) - int(begintime) % interval
            self._srv[srvname]["begintime"] = begintime
            self._srv[srvname]["processing"][nexttime] = []
            self._srv[srvname]["processing"][nexttime].extend([(nexttime,), False])
        now = time.time()
        for k, v in self._srv[srvname]["processing"].iteritems():
            if k < now and not v[1]:
                v[1] = True
                return k, v[0]
        return None, None

if __name__ == "__main__":
    sd = scheddata()
    sd.initdata("slp1", time.time()-600, 5, 4)
    sd.initdata("slp2")
    sd.initdata("slp3", maxcount=10)
    print sd.displaydata()

    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    nt, srvlist = sd.getdata("slp10")
    print nt, srvlist

    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    nt, srvlist = sd.getdata("slp1")
    print nt, srvlist
    print "release", nt
    sd.releasedata("slp1", nt)
    nt, srvlist = sd.getdata("slp1")
    print nt, srvlist
    nt, srvlist = sd.getdata("slp1")
    print nt, srvlist
    nt, srvlist = sd.getdata("slp1")
    print nt, srvlist
    print sd.displaydata("slp1")
    nt, srvlist = sd.getdata("slp1")
    print nt, srvlist

    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    sd.setdata("slp2", time.time()+5, ())
    print sd.displaydata("slp2")
    nt, srvlist = sd.getdata("slp2")
    print nt, srvlist
    time.sleep(10)
    nt, srvlist = sd.getdata("slp2")
    print nt, srvlist
