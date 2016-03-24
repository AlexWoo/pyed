from pylog import pylog


class pyconf(object):
    def __init__(self, pesys):
        self.user = "pyed"
        self.group = "pyed"
        self.daemon = True
        self.processes = 1
        self.loglevel = pesys.log._LOG_ERROR

        self.log = pesys.log
        self.loader = pesys.loader
        self.confpath = pesys.confpath

        conf = self.loader.load('conf', self.confpath)
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
