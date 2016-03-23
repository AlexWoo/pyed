import signal


class pysig(object):
    def __init__(self, pysys):
        self.__signals={
            signal.SIGQUIT: ["quit",   self.quit],
            #signal.SIGINT:  ["stop",   self.stop],
            signal.SIGTERM: ["stop",   self.stop],
            signal.SIGUSR1: ["reopen", self.reopen],
            signal.SIGHUP:  ["reload", self.reload],
            signal.SIGUSR2: ["reload", self.reload],
            signal.SIGCHLD: ["wait",   self.wait],
            signal.SIGSYS:  ["sys",    self.handler],
            signal.SIGPIPE: ["pipe",   self.handler]
        }

        self.pesys = pysys
        for key, sig in self.__signals.items():
            signal.signal(key, sig[1])

    def quit(self, signo, frame):
        self.pesys.quit = True

    def stop(self, signo, frame):
        print signo
        print dir(frame)
        self.pesys.stop = True

    def reopen(self, signo, frame):
        self.pesys.reopen = True
        
    def reload(self, signo, frame):
        self.pesys.reload = True
    
    def wait(self, signo, frame):
        self.pesys.reap = True
    
    def handler(self, signo, frame):
        log = self.pesys.log
        log.logError("Pysig", "Receive signal %s!!!" % self.__signals[signo][0])