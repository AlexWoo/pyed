import traceback, time


class pyslp(object):
    """
    scheduler.callslp()
    return value:
        para1: need to process slp
        para2: paralist(tuple)

    m.process(paralist)
        return value:
            para1: 0 process over, -1 process incomplete
            para2: next process interval (measured with millisecond)
            para3: service dict
            {
                servicename1: paralist(tuple),
                servicename2: paralist(tuple),
                ...
            }
 
    scheduler.endslp(ret, nexttime, srvdict)
        ret:
            m.process return para1
        nexttime:
            m.process calculate with return para2 from m.prorcess time.time()+float(para2)/1000
        srvdict:
            m.process return para3
        return value:
            None
    """
    def __init__(self, log, loader, m, scheduler):
        self.stop = False
        self.log = log

        self._scheduler = scheduler
        self._m = m
        self._enter = m.process

    def run(self):
        if self.stop: return

        trigger, args = self._scheduler.callslp()
        if not trigger: return
        else:
            try:
                if not args:
                    ret, wait, srvlist = self._enter(self)
                else:
                    ret, wait, srvlist = self._enter(self, *args)
                if not wait:
                    wait = 50
                nexttime = time.time() + float(wait)/1000
                self._scheduler.endslp(ret, nexttime, srvlist)
            except:
                self.log.logError("Pyslp", "Run SLP Error: %s" % traceback.format_exc())
                self._scheduler.endslp(-1, time.time(), None)
