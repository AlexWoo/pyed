class pyloader(object):
    def __init__(self, pysys):
        self.__modules = {}
        self.pesys = pysys

    def load(self, name, path):
        try:
            code = open(path).read()
        
            if self.__modules.has_key(name):
                del self.__modules[name]
    
            tmp = {}
            exec compile(code, '', 'exec') in tmp
            m = type(name, (object,), tmp)
            m.__class_name__ = name

        except Exception, e:
            log = self.pesys.log
            log.logError("Pyloader", "Load module %s [path: %s] error: %s!!!" % (name, path, e))

        return m

    def unload(self, module):
        name = module.__class_name__
        if self.__modules.has_key(name):
            del self.__modules[name]