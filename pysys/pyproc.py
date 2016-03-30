from multiprocessing import Process, Pipe
import sys, os, grp, pwd, traceback, errno

from pyevent.event import event


class pyproc(object):
    def __init__(self, pesys):
        self._procs = {}
        self.log = pesys.log
        self.conf = pesys.conf
        self.pidpath = pesys.pidpath
        self.pesys = pesys
        self.cmdcount = 0

    def daemon(self): # make proc run background
        pid = os.fork()
        if pid == -1:
            self.log.logError("Pyproc", "fork() failed in daemon")
            return
        elif pid != 0:
            sys.exit(0)

        pid = os.getpid()
        os.setsid()
        os.umask(0)

        fd = os.open("/dev/null", os.O_RDWR)
        if fd == -1:
            self.log.logError("Pyproc", "open /dev/null failed")
            return
        
        os.dup2(fd, sys.stdin.fileno())
        os.dup2(fd, sys.stdout.fileno())
        os.dup2(fd, sys.stderr.fileno())
        if fd > sys.stderr.fileno():
            os.close(fd)

    def procowner(self):
        user = self.conf.user
        group = self.conf.group
        if os.geteuid() == 0: #root
            try:
                gr = grp.getgrnam(group)
                os.setgid(gr.gr_gid)
                os.initgroups(user, gr.gr_gid)
                pw = pwd.getpwnam(user)
                os.setuid(pw.pw_uid)
            except:
                self.log.logError("Pyproc", "set uid or gid failed: %s",
                    traceback.format_exc())
                sys.exit(1)

    def pidfile(self):
        try:
            f = open(self.pidpath, "w")
            f.write("%d" % os.getpid())
            f.close()
        except Exception, e:
            self.log.logError("Pyproc", "write pidfile(%s) failed: %s" % (self.pidpath, e))
            sys.exit(1)

    def spawn(self, target, args):
        parent_conn, child_conn = Pipe()
        newargs = list(args)
        newargs.append(parent_conn)
        newargs.append(child_conn)
        p = Process(target=target, args=newargs)
        p.start()

        # close child_conn in master process
        child_conn.close()

        p.chanel = parent_conn
        p.hbcount = 0
        self._procs[p.pid] = p
        for key in self._procs.iterkeys():
            print key
        return p.pid

    def respawn(self, pid):
        p = self._procs[pid]
        target = p._target
        args = (p._args[0], p._args[1])
        p.chanel.close() # close parent_conn when respawn
        del self._procs[pid]
        return self.spawn(target, args)

    def wait(self, exiting):
        while 1:
            try:
                pid, _ = os.waitpid(-1, os.P_NOWAIT)
                if pid == 0:
                    return
                if pid > 0:
                    self.log.logInfo("Pyproc", "work(%d) exiting, master process SIGCHLD ...", pid)
                    if exiting:
                        del self._procs[pid]
                        if len(self._procs) == 0:
                            return
                    else:
                        self.respawn(pid)
            except OSError, e:
                if e.errno == errno.EINTR:
                    self.log.logInfo("Pyproc", "master process waitpid interrupt")
                    continue
                if e.errno == errno.ECHILD:
                    self.log.logInfo("Pyproc", "master process has no sub process to wait")
                    return
            except:
                self.log.logError("Pyproc", "waitpid raise error: %s", traceback.format_exc())
                continue

    def checkalive(self):
        return len(self._procs) > 0

    def closechanel(self):
        for p in self._procs.itervalues():
            p.chanel.close()
            p.event.del_read()

    def sendcmd(self, cmd):
        for p in self._procs.itervalues():
            p.chanel.send(cmd)
            self.cmdcount += 1

    def setcmdserver(self, cmdserver):
        self.cmdserver = cmdserver

    def sendsig(self, sig):
        for pid in self._procs.iterkeys():
            os.kill(pid, sig)

    def addevent(self, pid=-1):
        if pid == -1:
            for p in self._procs.itervalues():
                p.event = event(self.pesys.evs, self.pesys.tms, p.chanel)
                p.event.add_read(self.recvfromworker)
        else:
            if self._procs.has_key(pid):
                p = self._procs[pid]
                p.event = event(self.pesys.evs, self.pesys.tms, p.chanel)
                p.event.add_read(self.recvfromworker)
            else:
                self.log.logError("Pyproc", "pid(%d) not in pyproc" % pid)

    def recvfromworker(self, ev):
        try: #Pipe in multiprocessing, if peerside close, localside read will raise an EOFError
            buf = ev.sock.recv()
        except:
            ev.del_read()
            self.log.logError("Pyproc", "error occur when recv from worker: %s",
                traceback.format_exc())
            return

        if len(buf) == 0: # child close chanel, do nothing now TODO
            print "child close chanel"
            ev.del_read()
        elif buf == None:
            self.cmdcount -= 1
        else:
            self.cmdcount -= 1
            if self.cmdcount:
                self.cmdserver.sendresp(buf, False)
            else:
                self.cmdserver.sendresp(buf, True)
