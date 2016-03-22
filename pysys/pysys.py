import os, sys, argparse, signal
from pylog import pylog
from pysig import pysig
from pyloader import pyloader
from pyproc import pyproc


class pysys(object):
    def __init__(self, vertag, version, prefix):
        self.vertag = vertag
        self.version = version
        self.ver = 'pyed/' + self.version

        self.prefix = prefix
        if self.prefix == None or self.prefix == "":
            self.prefix = "/usr/local/pyed/"
        if not self.prefix.endswith("/"):
            self.prefix = self.prefix + "/"

    def parseargs(self):
        # opt
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-h", "-?", action='help',
               help=": show this help message and exit")
        parser.add_argument("-v", action='version', version=self.ver,
               help=": show version and exit")
        parser.add_argument("-t", action='store_true', default=False,
               help=": test configuration and exit")
        parser.add_argument("-s", metavar="signal",
               choices=['stop', 'quit', 'reopen', 'reload'],
               help=": send signal to a master process: stop, quit, reopen, reload")
        parser.add_argument("-p", metavar="prefix", default=self.prefix, type=str,
               help=": set prefix path (default: " + self.prefix + ")")
        parser.add_argument("-c", metavar="filename", type=str,
               help=": set configuration file (default: " + self.prefix + "conf/pyed.conf)")
        args = parser.parse_args()

        # test configuration
        self.testc = args.t

        # send signal
        self.stop = False
        self.quit = False
        self.reopen = False
        self.reload = False
        self.reap = False

        if args.s == "stop": # signal stop
            self.stop = True
        elif args.s == "quit": # signal quit
            self.quit = True
        elif args.s == "reopen": # signal reopen
            self.reopen = True
        elif args.s == "reload": # signal reload
            self.reload = True

        # path
        self.prefix = args.p
        if not self.prefix.endswith("/"):
            self.prefix = self.prefix + "/"
        self.logpath = self.prefix + "log/pyed.log"
        if args.c:
            self.confpath = args.c
        else:
            self.confpath = self.prefix + "conf/pyed.conf"
        self.binpath = self.prefix + "bin/pyed"
        self.pidpath = self.prefix + "pyed.pid"

    def initsys(self):
        self.log = pylog(self.logpath) # init log
        self.loader = pyloader(self) #init pyloader
        self.sig = pysig(self) # init signal
        self.proc = pyproc() # init proc
        self.loadconf() # init conf

    def loadconf(self):
        self.conf = self.loader.load('conf', self.confpath) # init conf

    def testconf(self):
        self.loadconf()
        sys.exit(1)

    def sendsig(self):
        if self.quit:
            sig = signal.SIGQUIT
        elif self.stop:
            sig = signal.SIGTERM
        elif self.reopen:
            sig = signal.SIGUSR1
        elif self.reload:
            sig = signal.SIGUSR2

        try:
            f = open(self.pidpath, "r")
            line = f.readline()
            pid = int(line)
            os.kill(pid, sig)
            f.close()
        except Exception, e:
            print("Error occur when send signal(%d) to pyed master:%s" % (sig, e))
        finally:
            sys.exit(1)

    def status(self):
        print "vertag:\t\t", self.vertag
        print "version:\t", self.version
        print "ver:\t\t", self.ver
    
        print "prefix:\t\t", self.prefix
        print "logpath:\t", self.logpath
        print "confpath:\t", self.confpath
        print "binpath:\t", self.binpath
        print "pidpath:\t", self.pidpath
    
        print "testc:\t\t", self.testc
    
        print "quit:\t\t", self.quit
        print "stop:\t\t", self.stop
        print "reopen:\t\t", self.reopen
        print "reload:\t\t", self.reload
        print "reap:\t\t", self.reap

if __name__ == '__main__':
    sys = pysys(1000000, "1.0.0", "/Users/wujie/Work/Github/pyed/")
    sys.parseargs()
    sys.status()