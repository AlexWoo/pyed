# PYED

---
## Instruction

Pyed is the abbreviation of Python Event Driver. It offers user a rapid development for a event system using tcpserver, timer etcd  

## How to use

import the package into your program, set hookpoint and run. Here is a simple example:

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

Run this program, you will get a server listen on port 8000, it will recv msg from client and print it on screen

## APIs

### timers

timers is a timer manager class storing and processing timer

**import:**

	from pyed.timers import timers

**API:**

	__init__(self)
		retrun value: timers object

	processtimer(self)
		retrun value: the latest timer arrival time interval measured millisecond

### events

events is a socket event manager class storing and processing event over socket

**import:**

use events_select as events

	from pyed.events_select import events_select as events

use events_epoll as events

	from pyed.events_epoll import events_select as events

**API:**

	__init__(self)
		retrun value: events object

	addevent(self, fd, ev, etype)
		return value: void
		fd: socket fd
		ev: event class instance create by event(sock)
		etype: set to events.EVENT_READ for adding a read event such as accepting connction or receiving msg; set to events.EVENT_WRITE for adding a write event

	delevent(self, fd, etype)
		return value: void
		fd: socket fd
		etype: exactly same as addevent, it delete event from events

	processevent(self, ms)
		return value: void
		ms: waiting time

### event

event offers user timer and socket event apis

**import:**

	from pyed.event import event

**API:**

	__init__(self, sock)
		retrun value: event object
		sock: socket object correlated with event

	add_read(self, readhandler)
		return value: void
		readhandler: read event handler

	del_read(self)
		return value: void

	add_write(self, writehandler)
		return value: void
		writehandler: write event handler

	del_write(self)
		return value: void

	add_timer(self, timeout, timeouthandler)
		return value: void
		timeout: time elaspe from now to the timer trigger time 
		timeouthandler: timer event handler

	del_timer(self)
		return value: void

	timerset(self)
		return value: whether timer is set

	timeout(self)
		return value: timer trigger time

### tcpclient

**import:**

	from pyed.tcpclient import tcpclient

**API:**

	__init__(self, cliconf)
		retrun value: tcpclient object
		srvconf: client config

	connect(self)
		retrun value: tcpconnection object

**srvconf:**

	tcpclientconf = {
	    "host": "127.0.0.1",
	    "port": 8000,
	    "blocking": 0,
	    "recvbuf": 8092,
	    "sendbuf": 8092,
	    "linger": (0,0),
	}

	host: the host of server to connect, could be hostname
	port: the port of server to connect, could be number between 1-65535 or service name such as http
	blocking: set 0 for blocking, set 1 for non-blocking
	recvbuf: see tcp opt
	sendbuf: see tcp opt
	linger: see tcp opt


### tcpserver

**import:**

	from pyed.tcpserver import tcpserver

**API:**

	__init__(self, accepthandler, srvconf)
		retrun value: tcpserver object
		accepthandler: handler when accept link from client
		srvconf: server config

**srvconf:**

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

	host: the host server bind, "" bind all interface
	port: the port server bind, could be number between 1-65535 or service name such as http
	blocking: set 0 for blocking, set 1 for non-blocking
	reuseaddr: see tcp opt
	recvbuf: see tcp opt
	sendbuf: see tcp opt
	backlog: see tcp opt
	linger: see tcp opt
	reuseport: see tcp opt

### tcpconnection

**import:**

	from pyed.tcpconnection import tcpconnection

**API:**

	__init__(self, sock, srvconf)
		retrun value: tcpconnection object
		sock: connect socket return by accept for server and socket for client
		srvconf: exactly same as srvconf, in tcpconnection we use blocking, recvbuf, sendbuf and linger only

	set_config(self, conf)
		return value: void
		conf: rate limit config for read and write

	set_recvmsg(self, recvmsghandler)
		return value: void
		recvmsghandler: handler when receive msg from peer

	set_broken(self, brokenhandler)
		return value: void
		brokenhandler: handler when link broken

	read(self, size=-1)
		return value: data receive from socket
		size: set to -1 receive all data in socket buffer; set to positive number, read size

	write(self, buf)
		return value: void
		buf: data send to sokcet buffer

	close(self)
		return value: void

## TODO LIST

- HTTP Server support
- HTTP Client support

## Author

AlexWoo(Wu Jie): wj19840501@gmail.com

