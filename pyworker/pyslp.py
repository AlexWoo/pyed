import traceback, time


class pyslp(object):
    def __init__(self, log, loader, m, scheduler):
        self.stop = False
        self.log = log

        self._scheduler = scheduler
        self._enter = m.process

    def run(self):
        if self.stop: return
        if self._count >= self._maxcount: return

        trigger, args = self._scheduler.callslp()
        if not trigger: return
        else:
            try:
                ret, wait, srvlist = self._enter(self, args)
                nexttime = time.time() + float(wait)/1000
                self._scheduler.endslp(ret, nexttime, srvlist)
            except:
                self.log.logError("Pyslp", "Run SLP Error: %s" % traceback.format_exc())
                self._scheduler.endslp(ret, time.time(), None)
