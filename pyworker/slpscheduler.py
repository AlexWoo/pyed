class slpschedmanager(object):
    def __init__(self, pesys):
        self._log = pesys.log
        self._loader = pesys.loader

    def create(self, schedtype):
        pass

class slpscheduler(object):
    def query(self, *args):
        pass

    def callslp(self, *args):
        pass

    def endslp(self, *args):
        pass
