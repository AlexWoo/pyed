import traceback


class pyloader(object):
    def __init__(self, log):
        self.log = log

    def load(self, name, path):
        try:
            tmp = {}
            exec compile(open(path).read(), "", "exec") in tmp
            m = type(name, (object,), tmp)
            m.__class_name__ = name

        except:
            self.log.logError("Pyloader", "Load module %s [path: %s] error: %s!!!"
                % (name, path, traceback.format_exc()))
            return None

        return m
