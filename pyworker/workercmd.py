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
            print "Master cmd:", cmd
        except:
            ev.del_read()
            self._log.logError("Worker", "error occur when recv cmd from master: %s",
                traceback.format_exc())
            return
    
        args = cmd.split()
        if args[0] in self._cmd:
            ret = self._cmd[args[0]](*args[1:])
            ev.sock.send(ret)
        else:
            ev.sock.send("Unknown command[%s]", args[0])
