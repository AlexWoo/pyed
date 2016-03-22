import time

def worker_process(pesys, i):
    log = pesys.log
    while 1:
        log.logError("Worker", "worker mainloop in worker_process")
        time.sleep(1)