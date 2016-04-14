import traceback, time
from pysys.pyloader import pyloader
from pyslp import pyslp


class pyslpm(object):
    def __init__(self, log, evs, tms, slpschedman, cmd):
        self._slps = {}
        self._stop = []
        self._log = log
        self._loader = pyloader(log)
        self._schedman = slpschedman
        slpmcmd = {
            "load": self.load,
            "unload": self.unload,
            "update": self.update,
            "display": self.display,
            "delete": self.delete
        }
        cmd.registercmd(slpmcmd)

    def _stopslp(self, modulename):
        slp = self._slps[modulename]
        slp.stop = True
        del self._slps[modulename]
        self._stop.append(slp)

    def _checkstop(self):
        self._stop = [slp for slp in self._stop if not slp.exited]

    def load(self, modulename, filepath, schedtype):
        sched = self._schedman.create(modulename, schedtype)
        if sched == None:
            return "Unknown schedtype: " + schedtype
        m = self._loader.load(modulename, filepath)
        if m == None:
            self._log.logError("Pyslpm", "Compile module[%s:%s] failed: %s"
                % (modulename, filepath, traceback.format_exc()))
            return "Compile module[" + modulename + ", " + filepath + "] failed"
        try: # load module in slp
            slp = pyslp(self._log, self._loader, m, sched)
        except:
            self._log.logError("Pyslpm", "load module[%s:%s] failed: %s"
                % (modulename, filepath, traceback.format_exc()))
            return "Load module[" + modulename + ":" + filepath + "] failed"
        slp.name = modulename
        slp.filepath = filepath
        slp.schedtype = schedtype
        self._slps[modulename] = slp
        return "Load module [" + modulename + ":" + filepath + "] ok"

    def unload(self, modulename):
        if modulename in self._slps:
            self._stopslp(modulename)
            return "Unload module[" + modulename + "] ok"
        else:
            return "Unknown module[" + modulename + "] for unloading"

    def update(self, modulename, filepath=None, schedtype=None):
        if modulename not in self._slps:
            return "Unknown module[" + modulename + "] for updating"
        if filepath == None:
            filepath = self._slps[modulename].filepath
        if schedtype == None:
            schedtype = self._slps[modulename].schedtype

        sched = self._schedman.create(modulename, schedtype)
        if sched == None:
            return "Unknown schedtype: " + schedtype

        m = self._loader.load(modulename, filepath, sched)
        if m == None:
            self._log.logError("Pyslpm", "Compile module[%s:%s] failed: %s"
                % (modulename, filepath, traceback.format_exc()))
            return "Compile module[" + modulename + ", " + filepath + "] failed"
        try: # load module in slp
            slp = pyslp(self._log, self._loader, m)
        except:
            self._log.logError("Pyslpm", "update module[%s:%s] failed: %s"
                % (modulename, filepath, traceback.format_exc()))
            return "update module[" + modulename + ":" + filepath + "] failed"
        slp.name = modulename
        slp.filepath = filepath
        self._stopslp(modulename)
        self._slps[modulename] = slp

        return "update module[" + modulename + ":" + filepath + "] ok"

    def display(self, modulename=None):
        if modulename and modulename in self._slps:
            return (modulename + "\t" + self._slps[modulename].filepath
                                      + "\t" + self._slps[modulename].schedtype)
        elif not modulename:
            ret = ""
            for k, v in self._slps.iteritems():
                ret += (k + "\t" + v.filepath + "\t" + v.schedtype + "\n")
            return ret
        return "Unknown module[" + modulename + "]"

    def delete(self, modulename):
        if modulename not in self._slps:
            return "Unknown module[" + modulename + "] for deleting"
        self._stopslp(modulename)
        return "delete module[" + modulename + "] ok"

    def runslp(self):
        self._checkstop()

        for slp in self._slps.itervalues():
            slp.run()

        return
