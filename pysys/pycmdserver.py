from pyevent.tcpserver import tcpserver
from pyevent.tcpconnection import tcpconnection


class cmdserver(tcpserver):
    def __init__(self, pesys):
        self.evs = pesys.evs
        self.tms = pesys.tms
        self.log = pesys.log
        self.srvconf = pesys.conf.cmdserver
        tcpserver.__init__(self, self.accepthandler, self.srvconf,
                           self.evs, self.tms)

    def accepthandler(self, ev):
        csock, _ = ev.sock.accept()
        c = tcpconnection(csock, self.srvconf, self.evs, self.tms)
        c.set_recvmsg(self.recvmsg)
        c.set_broken(self.brokenhandler)

    def recvmsg(self, c):
        buf = c.read()
        print "recvmsg", buf
        c.write(buf)
        c.close()
    
    def brokenhandler(self, c):
        self.log.logInfo("CmdServer", "connection broken")