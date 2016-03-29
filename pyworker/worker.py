import sys, traceback
from pyslpm import pyslpm


class worker(object):
    def __init__(self, pesys, i, chanel):
        self.evs = pesys.evs
        self.tms = pesys.tms
        self.log = pesys.log
        self.idx = i
        self.chanel = chanel
        self.exiting = False
        self._cmds = {
            "stop": self.stop,
            "quit": self.quit,
            "reopen": self.reopen,
            "reload": self.reload,
            "heartbeat": self.heartbeat
        }
        self.slpm = pyslpm(self.evs, self.tms, self.log)

    def mastercmd(self, ev):
        try: #Pipe in multiprocessing, if peerside close, localside read will raise an EOFError
            cmd = ev.sock.recv()
        except:
            ev.del_read()
            self.log.logError("Worker", "error occur when recv from master: %s",
                traceback.format_exc())
            return
        args = cmd.split()
        if self._cmds.has_key(args[0]):
            tuple_args = tuple(args[1:])
            self._cmds[args[0]](*tuple_args)
    
    def stop(self):
        self.log.logNotice("Worker", "worker process(%d) stop" % self.idx)
        sys.exit(0)
    
    def quit(self):
        self.log.logNotice("Worker", "worker process(%d) quit" % self.idx)
        self.exiting = True
    
    def reopen(self):
        self.log.reopen()
    
    def reload(self):
        self.log.logNotice("Worker", "worker process(%d) reload" % self.idx)
        # Do nothing now
        
    def heartbeat(self):
        pass