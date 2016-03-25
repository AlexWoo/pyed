from multiprocessing import Process, Pipe
import sys, os, grp, pwd

from pyevent.event import event


class pyproc(object):
    def __init__(self, pesys):
        self._procs = {}
        self.log = pesys.log
        self.conf = pesys.conf
        self.pidpath = pesys.pidpath
        self.pesys = pesys

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
            except Exception, e:
                self.log.logError("Pyproc", "set uid or gid failed: %s" % e)
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
        try:
            pid, _ = os.waitpid(-1, os.P_NOWAIT)
        except Exception, e:
            self.log.logError("Pyproc", "waitpid raise error: %s", e)
        if pid > 0:
            self.log.logInfo("Pyproc", "master process SIGCHLD ...")
            if exiting:
                del self._procs[pid]
            else:
                self.respawn(pid)

    def checkalive(self):
        if len(self._procs) > 0:
            return True
        else:
            return False

    def closechanel(self):
        for p in self._procs.itervalues():
            p.chanel.close()

    def sendcmd(self, cmd):
        for p in self._procs.itervalues():
            p.chanel.send(cmd)

    def sendsig(self, sig):
        for pid in self._procs.iterkeys()():
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
        buf = ev.sock.recv()
        if len(buf) == 0: # child close chanel, do nothing now TODO
            print "child close chanel"
        else:
            print "Master recv from worker", buf
