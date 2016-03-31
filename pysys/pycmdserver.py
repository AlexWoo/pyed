from pyevent.event import event
from pyevent.tcpserver import tcpserver
from pyevent.tcpconnection import tcpconnection


class cmdserver(tcpserver):
    def __init__(self, pesys):
        self.evs = pesys.evs
        self.tms = pesys.tms
        self.log = pesys.log
        self.proc = pesys.proc
        self.proc.setcmdserver(self)
        self.srvconf = pesys.conf.cmdserver
        self.c = None
        tcpserver.__init__(self, self.accepthandler, self.srvconf,
                           self.evs, self.tms)

    def accepthandler(self, ev):
        csock, _ = ev.sock.accept()
        if self.c:
            csock.close()
            self.log.logInfo("CmdServer", "Cmdserver has cmd to process, close new cmdclient")
            return
        self.c = tcpconnection(csock, self.srvconf, self.evs, self.tms)
        self.c.set_recvmsg(self.recvmsg)
        self.c.set_broken(self.brokenhandler)

    def recvmsg(self, c):
        buf = self.c.read()
        self.log.logInfo("CmdServer", "Send cmd[%s] to worker", buf.strip())
        self.proc.sendcmd(buf)
        self.ev = event(self.evs, self.tms)
        self.ev.add_timer(5000, self.timeouthandler) # set cmd response timeout to 5s

    def sendresp(self, buf, islast):
        self.c.write(buf)
        if islast:
            self.c.close()
            self.c = None
            self.ev.del_timer()

    def brokenhandler(self, c):
        self.c = None
        self.ev.del_timer()
        self.log.logInfo("CmdServer", "Cmdclient link broken")

    def timeouthandler(self, ev):
        self.log.logInfo("CmdServer", "Wait for Worker response timeout")
        self.c.close()
        self.c = None
        self.ev.del_timer()
