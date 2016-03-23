import time

def master_mainloop(pesys):
    log = pesys.log
    proc = pesys.proc
    while 1:
        log.logError("Master", "Master mainloop in master_mainloop")
        
        if pesys.reap: # deal sig with SIGCHLD
            proc.wait()

        proc.wait() # deal sig with SIGCHLD lost

        time.sleep(1)
