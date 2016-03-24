import argparse, sys, os, signal

# sys macro 
import pyedsys

# pysys
from pysys.pysys import pysys
from worker import worker_process

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
    except Exception, e:
        pesys.log.logError("Manager", "Error occur when send %s to pyed master:%s" % (sigstr, e))

def manager_process(pesys, args):
    if args.s:
        sendsig(pesys, args.s)
        sys.exit(0)

def master_mainloop(pesys):
    log = pesys.log
    proc = pesys.proc
    evs = pesys.evs
    tms = pesys.tms
    while 1:
        log.logError("Master", "Master mainloop in master_mainloop")
        
        t = tms.processtimer()
        evs.processevent(t)

        if pesys.stop: # stop right now
            pass

        if pesys.quit: # stop process new task and wait for old task process over
            pass

        if pesys.reopen: # reopen log
            pass

        if pesys.reload: # reload config
            pass

        if pesys.reap: # deal sig with SIGCHLD
            proc.wait()
            pesys.reap = False

        proc.wait() # deal sig with SIGCHLD lost

def master_process(pesys):
    pesys.log.logError("Master", "in master_process")
    pesys.initsys()

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
