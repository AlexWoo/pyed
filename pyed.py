import argparse, sys, os, signal, traceback


# sys macro 
import pyedsys

# pysys
from pysys.pysys import pysys
from pysys.pycmdserver import cmdserver
from pysys.pycmdclient import cmdclient
from pyworker.worker import worker
from pyevent.event import event

def parseargs(version, prefix):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "-?", action='help',
        help=": show this help message and exit")
    parser.add_argument("-v", action='version', version=version,
        help=": show version and exit")
    parser.add_argument("-s", metavar="signal",
        choices=['stop', 'quit', 'reopen', 'reload'],
        help=": send signal to a master process: stop, quit, reopen, reload")
    parser.add_argument("-p", metavar="prefix", default=prefix, type=str,
        help=": set prefix path (default: " + prefix + ")")
    parser.add_argument("-c", metavar="filename", type=str,
        help=": set configuration file (default: " + prefix + "conf/pyed.conf)")
    parser.add_argument("-e", nargs="+", metavar=('cmd', 'option'),
        help=": execute command of pyed")
    args = parser.parse_args()
    return args

def sendsig(pesys, sigstr):
    try:
        f = open(pesys.pidpath, "r")
        line = f.readline()
        pid = int(line)
        if sigstr == "stop":
            os.kill(pid, signal.SIGTERM)
        elif sigstr == "quit":
            os.kill(pid, signal.SIGQUIT)
        elif sigstr == "reopen":
            os.kill(pid, signal.SIGUSR1)
        elif sigstr == "reload":
            os.kill(pid, signal.SIGUSR2)
        f.close()
    except:
        pesys.log.logError("Manager", "Error occur when send %s to pyed master:%s"
            % (sigstr, traceback.format_exc()))

def quittimeout(ev):
    ev.proc.sendsig(signal.SIGKILL)

def cmdresphandler(c):
    resp = c.read()
    print resp
    c.close()

def managersendcmd(pesys, args):
    cmdcli = cmdclient(pesys)
    cmdcli.sendcmd(args[0], args[1:])
    cmdcli.mainloop()

def manager_process(pesys, args):
    if args.s:
        sendsig(pesys, args.s)
        sys.exit(0)
    elif args.e:
        managersendcmd(pesys, args.e)
        sys.exit(0)

def worker_process(pesys, i, pchanel, cchanel):
    pesys.log.logNotice("Worker", "Pyed worker process(%d) starting ...", i)
    pesys.initsys("worker")

    pchanel.close()
    w = worker(pesys, i, cchanel)
    w.mainloop()

def master_mainloop(pesys):
    pesys.initsys("master")

    log = pesys.log
    proc = pesys.proc
    evs = pesys.evs
    tms = pesys.tms
    cmdserver(pesys)
    exiting = False
    t_quit = event(evs, tms)

    proc.addevent()

    while 1:
        try:
            t = tms.processtimer()
            evs.processevent(t)
        except:
            log.logInfo("Master", "tms or evs runtime error: %s", traceback.format_exc())

        if pesys.stop and not exiting: # stop right now
            log.logNotice("Master", "master process stop ...")
            proc.sendsig(signal.SIGKILL)
            exiting = True

        if pesys.quit and not exiting: # stop process new task and wait for old task process over
            log.logNotice("Master", "master process quit ...")
            proc.sendcmd("quit")
            exiting = True
            t_quit.add_timer(10000, quittimeout)
            t_quit.proc = proc

        if pesys.reopen: # reopen log
            log.logNotice("Master", "master process reopen ...")
            pesys.reopen = False
            proc.sendcmd("reopen")
            log.reopen()

        if pesys.reload: # reload config
            pesys.reload = False
            log.logNotice("Master", "master process reload ...")
            proc.sendcmd("reload")

        if pesys.reap: # deal sig with SIGCHLD
            pesys.reap = False

        proc.wait(exiting) # process SIGCHLD

        if exiting:
            if pesys.quit and not proc.checkalive():
                log.logNotice("Master", "All worker process exited, master quit")
                proc.closechanel()
                os.remove(pesys.pidpath)
                sys.exit(0)
            if pesys.stop:
                log.logNotice("Master", "All worker process stoped, master stop")
                os.remove(pesys.pidpath)
                sys.exit(0)

def master_process(pesys):
    pesys.proc.procowner()
    pesys.proc.pidfile()
    for i in range(pesys.conf.processes):
        pid = pesys.proc.spawn(worker_process, (pesys, i))
        pesys.log.logNotice("Master", "Pyed master process start sub process %d" % pid)
    master_mainloop(pesys)

def main():
    version = 'pyed/' + pyedsys.version
    prefix = pyedsys.prefix
    if prefix == None or prefix == "":
        prefix = "/usr/local/pyed/"
    if not prefix.endswith("/"):
        prefix = prefix + "/"
    
    # parse args
    args = parseargs(version, prefix)
    prefix = args.p
    if not prefix.endswith("/"):
        prefix = prefix + "/"

    pesys = pysys(version, prefix, args.c)

    manager_process(pesys, args)

    pesys.log.logNotice("Master", "Pyed master process starting ...")
    if pesys.conf.daemon:
        pesys.log.logInfo("Master", "Pyed master process is set background running")
        pesys.proc.daemon()
    master_process(pesys)

if __name__ == '__main__':
    main()
