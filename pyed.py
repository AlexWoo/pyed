import argparse, sys, os, signal, traceback

# sys macro 
import pyedsys

# pysys
from pysys.pysys import pysys
from pyevent.event import event
from pyworker.worker import worker

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

def manager_process(pesys, args):
    if args.s:
        sendsig(pesys, args.s)
        sys.exit(0)

def worker_process(pesys, i, pchanel, cchanel):
    pesys.initsys()

    log = pesys.log
    evs = pesys.evs
    tms = pesys.tms

    pchanel.close()
    ev = event(evs, tms, cchanel)
    w = worker(pesys, i, cchanel)
    ev.add_read(w.mastercmd)

    while 1:
        try:
            t = tms.processtimer()
            evs.processevent(t)
        except:
            log.logInfo("Worker", "error occured when event process: %s", traceback.format_exc())
        
        if w.exiting:
            pass
            #pesys.chanel.close()
            #sys.exit(0)

def quittimeout(ev):
    print "quittimeout"
    ev.proc.sendsig(signal.SIGKILL)

def master_mainloop(pesys):
    pesys.initsys()

    log = pesys.log
    proc = pesys.proc
    evs = pesys.evs
    tms = pesys.tms
    exiting = False
    t_quit = event(evs, tms)

    proc.addevent()

    while 1:
        if exiting and not proc.checkalive():
            log.logNotice("Master", "All worker process exited, master exit")
            sys.exit(0)

        try:
            t = tms.processtimer()
            evs.processevent(t)
        except:
            log.logInfo("Master", "error occured when event process: %s", traceback.format_exc())

        if pesys.stop and not exiting: # stop right now
            log.logInfo("Master", "master process stop ...")
            proc.sendcmd("stop")
            exiting = True

        if pesys.quit and not exiting: # stop process new task and wait for old task process over
            log.logInfo("Master", "master process quit ...")
            proc.sendcmd("quit")
            exiting = True
            proc.closechanel()
            t_quit.add_timer(10000, quittimeout)
            t_quit.proc = proc

        if pesys.reopen: # reopen log
            log.logInfo("Master", "master process reopen ...")
            pesys.reopen = False
            proc.sendcmd("reopen")
            log.reopen()

        if pesys.reload: # reload config
            pesys.reload = False
            log.logInfo("Master", "master process reload ...")
            proc.sendcmd("reload")

        if pesys.reap: # deal sig with SIGCHLD
            pesys.reap = False

        proc.wait(exiting) # deal sig with SIGCHLD lost

def master_process(pesys):
    pesys.log.logError("Master", "in master_process")

    pesys.proc.procowner()
    pesys.proc.pidfile()
    for i in range(pesys.conf.processes):
        pid = pesys.proc.spawn(worker_process, (pesys, i))
        pesys.log.logInfo("Master", "Pyed master process start sub process %d" % pid)
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
