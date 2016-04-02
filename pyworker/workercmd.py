import traceback

from pyevent.event import event


class workercmd(object):
    def __init__(self, log, evs, tms, chanel):
        self._log = log
        self._cmd = {}
        self._ev = event(evs, tms, chanel)
        self._ev.add_read(self.processcmd)
    
    def registercmd(self, cmdtable):
        self._cmd.update(cmdtable)
    
    def processcmd(self, ev):
        try: #Pipe in multiprocessing, if peerside close, localside read will raise an EOFError
            cmd = ev.sock.recv()
        except:
            ev.del_read()
            self._log.logError("Worker", "error occur when recv cmd from master: %s",
                traceback.format_exc())
            return
    
        args = cmd.split()
        if args[0] in self._cmd:
            try:
                ret = self._cmd[args[0]](*args[1:])
            except TypeError:
                ev.sock.send("Number of arguments mismatched")
            except:
                self._log.logInfo("Worker", "error occur when execute cmd[%s], %s",
                                   args[0], traceback.format_exc())
                ev.sock.send("Execute " + args[0] + " failed")
                return
            else:
                ev.sock.send(ret)
        else:
            ev.sock.send("Unknown command: " + args[0])
