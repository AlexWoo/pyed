from multiprocessing import Process
import sys, os, grp, pwd


class pyproc(object):
    def __init__(self):
        self.__procs = {}

    def daemon(self, log): # make proc run background
        pid = os.fork()
        if pid == -1:
            log.logError("Pyproc", "fork() failed in daemon")
            return
        elif pid != 0:
            sys.exit(0)
    
        pid = os.getpid()
    
        if os.setsid() == -1:
            log.logError("Pyproc", "setsid() failed in daemon")
            return
    
        os.umask(0)
    
        fd = os.open("/dev/null", os.O_RDWR)
        if fd == -1:
            log.logError("Pyproc", "open /dev/null failed")
            return
    
        if os.dup2(fd, 0) == -1:
            log.logError("Pyproc", "dup2 stdin failed")
            return
    
        if os.dup2(fd, 1) == -1:
            log.logError("Pyproc", "dup2 stdout failed")
            return
    
        if fd > 2:
            if os.close(fd) == -1:
                log.logError("Pyproc", "close fd failed")
                return

    def procowner(self, user, group, log):
        if os.geteuid() == 0: #root
            try:
                gr = grp.getgrnam(group)
                os.setgid(gr.gr_gid)
                os.initgroups(user, gr.gr_gid)
                pw = pwd.getpwnam(user)
                os.setuid(pw.pw_uid)
            except Exception, e:
                log.logError("Pyproc", "set uid or gid failed: %s" % e)
                print("set uid or gid failed: %s" % e)
                sys.exit(1)

    def writepidfile(self, pidfile):
        f = open(pidfile, "w")
        f.write("%d" % os.getpid())
        f.close()

    def spawn(self, target, args):
        p = Process(target=target, args=args)
        p.start()
        return p.pid