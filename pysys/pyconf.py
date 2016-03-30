import sys
from pylog import pylog


class pyconf(object):
    def __init__(self, pesys):
        self.user = "pyed"
        self.group = "pyed"
        self.daemon = True
        self.processes = 1
        self.loglevel = pesys.log._LOG_ERROR

        self.cmdserver={
            "host":"127.0.0.1",
            "port":2539,
            "blocking":0,
            "reuseaddr":1,
            "backlog":511,
            "reuseport":0
        }

        self.log = pesys.log
        self.loader = pesys.loader
        self.confpath = pesys.confpath

        conf = self.loader.load('conf', self.confpath)
        if conf == None:
            self.log.logInfo("Pyconf", "load conf[%s] failed" % self.confpath)
            sys.exit(1)
        if hasattr(conf, 'user'):
            self.user = conf.user
        if hasattr(conf, 'group'):
            self.group = conf.group
        if hasattr(conf, 'daemon'):
            self.daemon = conf.daemon
        if hasattr(conf, 'processes'):
            self.processes = conf.processes
        if hasattr(conf, 'loglevel'):
            self._loglevel(conf.loglevel)

        if hasattr(conf, "cmdserver"):
            for k, v in conf.cmdserver.iteritems():
                self.cmdserver[k] = v

    def loadconf(self):
        conf = self.loader.load('conf', self.confpath)
        if hasattr(conf, 'loglevel'):
            self._loglevel(conf.loglevel)

    def _loglevel(self, lvstr):
        if lvstr == "debug":
            self.loglevel = pylog._LOG_DEBUG
        elif lvstr == "info":
            self.loglevel = pylog._LOG_INFO
        elif lvstr == "warn":
            self.loglevel = pylog._LOG_WARN
        elif lvstr == "error":
            self.loglevel = pylog._LOG_ERROR
        elif lvstr == "fatal":
            self.loglevel = pylog._LOG_FATAL
        else:
            self.log.logError("Conf", "Unknown loglevel in conf:%s", lvstr)
