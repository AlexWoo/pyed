from pyed.tcpserver import tcpserver
from pyed.timers import timers
from pyed.events_select import events_select as events
from pyed.tcpconnection import tcpconnection

tcpserverconf = {
    "host": "",
    "port": 8000,
    "blocking": 0,
    "reuseaddr": 1,
    "recvbuf": 8092,
    "sendbuf": 8092,
    "backlog": 1024,
    "linger": (0,0),
    "reuseport": 0
}

def recvmsg(c):
    buf = c.read()
    print "################################", len(buf)
    print buf
    print "################################"

def broken(c):
    print "link broken"

def accepthandler(ev):
    csock, _ = ev.sock.accept()
    c = tcpconnection(csock, tcpserverconf)
    c.set_recvmsg(recvmsg)
    c.set_broken(broken)

if __name__ == '__main__':
    srv = tcpserver(accepthandler, tcpserverconf)
    evs = events()
    tms = timers()

    while 1:
        t = tms.processtimer()
        evs.processevent(t)
