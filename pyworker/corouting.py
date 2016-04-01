import traceback


class coroutine(object):
    def __init__(self, log, func, *args):
        self._log = log
        self._state = "init"
        try:
            self._gen = func(*args)
        except:
            self._log.logError("Corouting", "Spawn func failed: %s",
                      traceback.format_exc())
            self._state = "stop"

    def wait(self):
        if self._state == "stop":
            return None
        self._state = "running"
        try:
            res = self._gen.next()
        except:
            self._log.logError("Corouting", "Wait func failed: %s",
                      traceback.format_exc())
            return None
        return res

    def kill(self):
        self._state = "stop"
        try:
            self._gen.close()
        except:
            self._log.logError("Corouting", "Close func failed: %s",
                      traceback.format_exc())

if __name__ == '__main__':
    def test(idx):
        while 1:
            print "In test", idx
            yield "Hello", idx
            idx += 1
    
    from pysys.pylog import pylog
    log = pylog("test.log")
    
    a = coroutine(log, test, 10)
    res = a.wait()
    print res
    res = a.wait()
    print res
    a.kill()
    res = a.wait()
    print res
    

