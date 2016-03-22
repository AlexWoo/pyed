import pyedsys

## pysys
from pysys.pysys import pysys
from master import master_mainloop
from worker import worker_process

def sysinit():
    pesys = pysys(pyedsys.vertag, pyedsys.version, pyedsys.prefix)
    pesys.parseargs()

    # manager process from here
    if pesys.testc:
        pesys.testconf()
    if pesys.quit or pesys.stop or pesys.reopen or pesys.reload:
        pesys.sendsig()

    # master process from here
    pesys.initsys()

    return pesys

def main():
    pesys = sysinit()
    # can not modify when system running
    log = pesys.log
    conf = pesys.conf
    proc = pesys.proc
    log.logNotice("Master", "Pyed master process starting ...")
    if conf.daemon:
        proc.daemon(log)
        log.logInfo("Master", "Pyed master process is set background running")
    proc.procowner(conf.user, conf.group, log)
    proc.writepidfile(pesys.pidpath)
    for i in range(conf.processes):
        pid = proc.spawn(worker_process, (pesys, i))
        log.logInfo("Master", "Pyed master process start sub process %d" % pid)
    master_mainloop(pesys)

if __name__ == '__main__':
    main()
