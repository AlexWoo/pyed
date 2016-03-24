from multiprocessing import Process, Pipe
import sys, os, grp, pwd
from pyevent import event


class pyproc(object):
    def __init__(self, pesys):
        self._procs = {}
        self.log = pesys.log
        self.conf = pesys.conf
        self.pidpath = pesys.pidpath

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
        pesys = args[0]
        pesys.chanel = child_conn
        p = Process(target=target, args=args)
        p.start()
        p.chanel = parent_conn
        p.event = event.event(p.chanel)
        p.event.add_read(self.recvfromworker)
        self._procs[p.pid] = p
        for key in self._procs.iterkeys():
            print key
        return p.pid

    def respawn(self, pid):
        p = self._procs[pid]
        target = p._target
        args = p._args
        del self._procs[pid]
        return self.spawn(target, args)

    def wait(self):
        pid, _ = os.waitpid(-1, os.P_NOWAIT)
        if pid > 0:
            self.respawn(pid)

    def recvfromworker(self, ev):
        pass

    def sendtoworker(self, buf):
        pass