from pyed.tcpclient import tcpclient
from pyed.event import event
from pyed.timers import timers
try:
    from pyed.events_epoll import events_epoll as events
except:
    from pyed.events_select import events_select as events
from pyed.tcpconnection import tcpconnection
import sys

pytclientconf = {
    "host": "127.0.0.1",
    "port": 8000,
    "blocking": 0,
    "recvbuf": 8092,
    "sendbuf": 8092,
    "linger": (0,0),
}

def recvmsg(c):
    buf = c.read()
    print "################################"
    print "Recv Package(%d):" % len(buf)
    print buf
    print "################################"

def broken(c):
    print "################################"
    print "Link Broken"
    print "################################"
    sys.exit(-1)

if __name__ == '__main__':
    evs = events()
    tms = timers()
    cli = tcpclient(pytclientconf)
    c = cli.connect()
    c.set_recvmsg(recvmsg)
    c.set_broken(broken)

    while 1:
        buf = sys.stdin.readline()
        buf = buf[:-1]
        print "################################"
        print "Read from stdin", buf
        print "################################"
        if buf == "quit":
            c.close()
            sys.exit(-1)
        c.write(buf)

        t = tms.processtimer()
        evs.processevent(t)
