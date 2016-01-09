from pyed.tcpserver import tcpserver
from pyed.timers import timers
try:
    from pyed.events_epoll import events_epoll as events
except:
    from pyed.events_select import events_select as events
from pyed.tcpconnection import tcpconnection

pytserverconf = {
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

def sendresp(c, buf):
    print "################################"
    print "Send Package(%d):" % len(buf)
    print buf
    print "################################"
    c.write(buf)

def recvmsg(c):
    buf = c.read()
    print "################################"
    print "Recv Package(%d):" % len(buf)
    print buf
    print "################################"
    sendresp(c, buf)

def broken(c):
    print "################################"
    print "Link Broken"
    print "################################"

def accepthandler(ev):
    csock, caddr = ev.sock.accept()
    print "################################"
    print "Recv Connection From %s:%d:" % caddr
    print "################################"
    c = tcpconnection(csock, pytserverconf)
    c.set_recvmsg(recvmsg)
    c.set_broken(broken)

if __name__ == '__main__':
    srv = tcpserver(accepthandler, pytserverconf)
    evs = events()
    tms = timers()

    while 1:
        t = tms.processtimer()
        evs.processevent(t)
