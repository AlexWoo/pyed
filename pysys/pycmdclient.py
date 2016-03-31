import sys

from pyevent.event import event
from pyevent.tcpclient import tcpclient
from pyevent.timers import timers
try:
    from pyevent.events_epoll import events_epoll as events
except:
    from pyevent.events_select import events_select as events


class cmdclient(tcpclient):
    def __init__(self, pesys):
        self.log = pesys.log
        self.cliconf = {}
        self.evs = events()
        self.tms = timers()
        self.cliconf["host"] = pesys.conf.cmdserver["host"]
        self.cliconf["port"] = pesys.conf.cmdserver["port"]
        tcpclient.__init__(self, self.cliconf, self.evs, self.tms)
        self.c = self.connect()
        self.c.set_recvmsg(self.displayresp)
        self.c.set_broken(self.brokenhandler)

    def mainloop(self):
        while 1:
            t = self.tms.processtimer()
            self.evs.processevent(t)

    def sendcmd(self, cmd, args):
        buf = cmd + " "
        for arg in args:
            buf += (arg + " ")
        self.c.write(buf)
        self.ev = event(self.evs, self.tms)
        self.ev.add_timer(10000, self.timeouthandler) # set cmd response timeout to 5s

    def displayresp(self, c):
        buf = c.read()
        print buf
        self.ev.add_timer(10000, self.timeouthandler) # refresh response timeout

    def brokenhandler(self, c):
        sys.exit(0)

    def timeouthandler(self, ev):
        print("!!!!! Wait cmdserver response timeout")
        sys.exit(0)