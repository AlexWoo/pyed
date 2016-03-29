import traceback, time


class pyslp(object):
    def __init__(self, log, loader, m):
        self._slps = {}
        self._enter = []
        self._steps = []
        self._loader = loader
        self.loadmodule(m)

    def loadmodule(self, m):
        for name, item in m.modulelist.iteritems():
            path = item[0]
            func = item[1]
            isEnter = item[2]
            script = self._loader.load(name, path)
            self._slps[name] = getattr(script, func)
            if isEnter:
                self._enter.append(name)

        m.init(self)
        self._steps = self._enter

    def runslp(self):
        while 1:
            try:
                func = self._slps[self._steps[0]]
                code, param = func(self)
                if code == -1:
                    self._steps = self._enter
                    return -1, time.time() + param / 1000
                elif code == 0:
                    self._steps = self._enter
                    return 0, 0
                elif code > 0:
                    for p in param:
                        self._steps.append(p)
            except:
                self.log.logError("Pyslp", "Run SLP Error: %s" % traceback.format_exc())
                return 0, 0

    def lsslp(self):
        retstr = ""
        for m in self._steps:
            retstr = retstr + m + "\r\n"
        return retstr