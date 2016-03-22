from datetime import datetime
import os


class pylog(object):
    _LOG_ALL    = 0
    _LOG_DEBUG  = 0
    _LOG_INFO   = 1
    _LOG_WARN   = 2
    _LOG_ERROR  = 3
    _LOG_FATAL  = 4
    _LOG_NOTICE = 4
    _LOG_NONE   = 5
    _logstr = {
        _LOG_DEBUG:  "Debug ",
        _LOG_INFO:   "Info  ",
        _LOG_WARN:   "Warn  ",
        _LOG_ERROR:  "Error ",
        _LOG_FATAL:  "Fatal ",
        _LOG_NOTICE: "Notice"
        }

    def __init__(self, logpath):
        self._level = pylog._LOG_ERROR
        self._logpath = logpath
        self._logfile = open(logpath, "a+")
    
    def _log(self, level, module, fmtstr):
        if level < self._level:
            return
        timenow = datetime.now()
        self._logfile.write("%s.%03d [%s] %d %s: %s\r\n" %
                            (timenow.strftime("%Y-%m-%d %H:%M:%S"),
                            timenow.microsecond/1000,
                            pylog._logstr[level],
                            os.getpid(), module, fmtstr))
        self._logfile.flush()

    def setloglevel(self, loglevel):
        self._level = loglevel

    def reopen(self):
        self._logfile.close()
        self._logfile = open(self._logpath, "a+")
    
    def logDebug(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self._log(pylog._LOG_DEBUG, module, fmtstr)
    
    def logInfo(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self._log(pylog._LOG_INFO, module, fmtstr)
    
    def logWarn(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self._log(pylog._LOG_WARN, module, fmtstr)
    
    def logError(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self._log(pylog._LOG_ERROR, module, fmtstr)
    
    def logFatal(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self._log(pylog._LOG_FATAL, module, fmtstr)

    def logNotice(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self._log(pylog._LOG_NOTICE, module, fmtstr)