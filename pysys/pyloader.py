import traceback, types


class pyloader(object):
    def __init__(self, log):
        self.log = log

    def load(self, name, path):
        try:
            m = types.ModuleType(name)
            exec open(path).read() in m.__dict__
            m.__file__ = path
            return m

        except:
            self.log.logError("Pyloader", "Load module %s [path: %s] error: %s!!!",
                              name, path, traceback.format_exc())
            return None
