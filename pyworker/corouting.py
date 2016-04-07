import traceback


class coroutine(object):
    def __init__(self, log, func, *args):
        self.log = log
        self._state = "init"
        try:
            self._gen = func(*args)
            print self._gen
        except:
            self._state = "stop"
            raise

    def wait(self):
        if self._state == "stop":
            return None
        self._state = "running"
        try:
            res = self._gen.next()
        except StopIteration:
            self._state = "stop"
        except:
            self.log.logError("Corouting", "%s", traceback.format_exc())
        return res

    def kill(self):
        self._state = "stop"
        try:
            self._gen.close()
        except:
            raise
