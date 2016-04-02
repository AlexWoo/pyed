class coroutine(object):
    def __init__(self, log, func, *args):
        self.log = log
        self._state = "init"
        try:
            self._gen = func(*args)
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
            raise
        return res

    def kill(self):
        self._state = "stop"
        try:
            self._gen.close()
        except:
            raise
