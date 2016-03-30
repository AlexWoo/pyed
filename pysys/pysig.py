import signal


class pysig(object):
    def __init__(self, pesys, sigtable):
        self._signals = sigtable
        self.pesys = pesys
        self.log = pesys.log
        for key, sig in self._signals.items():
            signal.signal(key, sig[1])

    def quit(self, signo, frame):
        self.pesys.quit = True

    def stop(self, signo, frame):
        self.pesys.stop = True

    def reopen(self, signo, frame):
        self.pesys.reopen = True
        
    def reload(self, signo, frame):
        self.pesys.reload = True
    
    def wait(self, signo, frame):
        self.pesys.reap = True
    
    def handler(self, signo, frame):
        self.log.logError("Pysig", "Receive signal %s!!!" % self._signals[signo][0])


class mastersig(pysig):
    def __init__(self, pesys):
        sigtable = {
            signal.SIGQUIT: ["quit",   self.quit],
            signal.SIGINT:  ["stop",   self.stop],
            signal.SIGTERM: ["stop",   self.stop],
            signal.SIGUSR1: ["reopen", self.reopen],
            signal.SIGHUP:  ["reload", self.reload],
            signal.SIGUSR2: ["reload", self.reload],
            signal.SIGCHLD: ["wait",   self.wait],
            signal.SIGSYS:  ["sys",    self.handler],
            signal.SIGPIPE: ["pipe",   self.handler],
            signal.SIGALRM: ["alrm",   self.handler]
        }
        pysig.__init__(self, pesys, sigtable)


class workersig(pysig):
    def __init__(self, pesys):
        sigtable = {
            signal.SIGQUIT: ["quit",   self.handler],
            signal.SIGINT:  ["int",    self.handler],
            signal.SIGTERM: ["term",   self.handler],
            signal.SIGUSR1: ["usr1",   self.handler],
            signal.SIGHUP:  ["hup",    self.handler],
            signal.SIGUSR2: ["usr2",   self.handler],
            signal.SIGCHLD: ["chld",   self.handler],
            signal.SIGSYS:  ["sys",    self.handler],
            signal.SIGPIPE: ["pipe",   self.handler],
            signal.SIGALRM: ["alrm",   self.handler]
        }
        pysig.__init__(self, pesys, sigtable)