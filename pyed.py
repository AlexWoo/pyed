import argparse, sys, os, signal, traceback

# sys macro 
import pyedsys

# pysys
from pysys.pysys import pysys
from pysys.pycmdserver import cmdserver
from pyworker.worker import worker
from pyevent.event import event
from pyevent.tcpclient import tcpclient
from pyevent.tcpserver import tcpserver
from pyevent.timers import timers
try:
    from pyevent.events_epoll import events_epoll as events
except:
    from pyevent.events_select import events_select as events

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
    parser.add_argument("--load", nargs=2, metavar=('modulename', 'filename'), type=str,
        help=": load module")
    parser.add_argument("--unload", metavar='modulename', type=str,
        help=": unload module")
    parser.add_argument("--update", nargs=2, metavar=('modulename', 'filename'),
        type=str, default=None,
        help=": update module")
    parser.add_argument("--display", metavar='modulename', default=None,
        help=": display module")
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
    try:
        evs = events()
        tms = timers()
        cliconf={
            "host":pesys.conf.cmdserver["host"],
            "port":pesys.conf.cmdserver["port"]
        }
        cmd = "test"
        cmdclient = tcpclient(cliconf, evs, tms)
        c = cmdclient.connect()
        c.set_recvmsg(cmdresphandler)
        c.write(cmd)
        while 1:
            try:
                evs.processevent(60000)
            except:
                pesys.log.logError("Manager", "recv cmd response from server[%s:%d] failed: %s"
                    % (cliconf["host"], cliconf["port"], traceback.format_exc()))
                sys.exit(0)
    except:
        pesys.log.logError("Manager", "send cmd[%s] to server[%s:%d] failed: %s"
            % (cmd, cliconf["host"], cliconf["port"], traceback.format_exc()))
        sys.exit(0)

def manager_process(pesys, args):
    if args.s:
        sendsig(pesys, args.s)
        sys.exit(0)
    elif args.load or args.unload or args.update or args.display:
        managersendcmd(pesys, args)
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

def master_mainloop(pesys):
    pesys.initsys()

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
            proc.closechanel()
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
                os.remove(pesys.pidpath)
                sys.exit(0)
            if pesys.stop:
                log.logNotice("Master", "All worker process stoped, master stop")
                os.remove(pesys.pidpath)
                sys.exit(0)

def master_process(pesys):
    pesys.log.logError("Master", "in master_process")

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
