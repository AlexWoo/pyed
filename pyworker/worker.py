import sys, traceback

from pyslpm import pyslpm
from workercmd import workercmd
from slpscheduler import slpschedmanager


class worker(object):
    def __init__(self, pesys, i, chanel):
        self._evs = pesys.evs
        self._tms = pesys.tms
        self._log = pesys.log
        self._schedman = slpschedmanager(pesys)
        self._idx = i

        cmd = {
            "quit": self.quit,
            "reopen": self.reopen,
            "reload": self.reload
        }
        self._cmd = workercmd(self._log, self._evs, self._tms, chanel)
        self._cmd.registercmd(cmd)

        self._exiting = False
        self._slpm = pyslpm(self._log, self._evs, self._tms, self._schedman, self._cmd)

    def mainloop(self):
        while 1:
            try:
                self._slpm.runslp()
                t = self._tms.processtimer()
                self._evs.processevent(t)
            except SystemExit:
                return
            except:
                self._log.logInfo("Worker", "error occured when event process: %s",
                                  traceback.format_exc())

    def quit(self):
        if not self._exiting:
            self._log.logNotice("Worker", "worker process(%d) quit", self._idx)
            self._exiting = True
            sys.exit(0)

    def reopen(self):
        self._log.logNotice("Worker", "worker process(%d) reopen log", self._idx)
        self._log.reopen()

    def reload(self):
        self._log.logNotice("Worker", "worker process(%d) reload conf", self._idx)
        # Do nothing now
