from pylog import pylog
from pyconf import pyconf
from pyloader import pyloader

from pysig import pysig
from pyproc import pyproc
from pyevent.timers import timers
try:
    from pyevent.events_epoll import events_epoll as events
except:
    from pyevent.events_select import events_select as events


class pysys(object):
    def __init__(self, version, prefix, confpath):
        self.version = version
        self.prefix = prefix

        self.stop = False
        self.quit = False
        self.reopen = False
        self.reload = False
        self.reap = False

        if confpath:
            self.confpath = confpath
        else:
            self.confpath = prefix + "conf/pyed.conf"
        self.logpath = prefix + "log/pyed.log"
        self.binpath = prefix + "bin/pyed"
        self.pidpath = prefix + "pyed.pid"

        self.log = pylog(self.logpath) # init log
        self.loader = pyloader(self) # init pyloader
        self.conf = pyconf(self) # init pyconf
        self.proc = pyproc(self) # init proc

        self.conf.loadconf()
        self.log.setloglevel(self.conf.loglevel)

    def initsys(self):
        self.sig = pysig(self) # init signal
        self.evs = events() # init events
        self.tms = timers() # init timers

    def testconf(self):
        self.conf.loadconf()

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
