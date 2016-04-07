import traceback


class pyslp(object):
    def __init__(self, log, loader, m, scheduler, parallelcount):
        self.stop = False
        self.log = log

        self._scheduler = scheduler
        self._maxcount = parallelcount
        self._count = 0;
        self._enter = m.process

    def run(self):
        if self.stop: return
        if self._count >= self._maxcount: return

        trigger, args = self._scheduler.callslp()
        if not trigger: return
        else:
            try:
                self._count += 1
                retargs = self._enter(args)
            except:
                self.log.logError("Pyslp", "Run SLP Error: %s" % traceback.format_exc())
                self._count -= 1
