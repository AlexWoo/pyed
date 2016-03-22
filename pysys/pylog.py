from datetime import datetime
import os


class pylog(object):
    LOG_ALL   = 0
    LOG_DEBUG = 0
    LOG_INFO  = 1
    LOG_WARN  = 2
    LOG_ERROR = 3
    LOG_FATAL = 4
    LOG_NONE  = 5
    __logstr = {
        LOG_DEBUG: "Debug",
        LOG_INFO:  "Info ",
        LOG_WARN:  "Warn ",
        LOG_ERROR: "Error",
        LOG_FATAL: "Fatal"
        }

    def __init__(self, logpath, loglevel=LOG_ERROR):
        self.__level = loglevel
        self.__logpath = logpath
        self.__logfile = self.__open(self.__logpath)

    def __open(self, logpath):
        logfile = file(logpath, "a+")
        return logfile

    def __time(self):
        timenow = datetime.now()
        return timenow.strftime("%Y-%m-%d %H:%M:%S.")+str(timenow.microsecond/1000)
    
    def __log(self, level, module, fmtstr):
        if level < self.__level:
            return
        log = self.__time() + " [" + pylog.__logstr[level] + "] " + str(os.getpid()) + " " + module + ": " + fmtstr + "\r\n"
        self.__logfile.write(log)
        self.__logfile.flush()
    
    def reopen(self):
        self.__logfile.flush()
        self.__logfile.close()
        self.__logfile = self.__open(self.__logpath)
    
    def logDebug(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self.__log(pylog.LOG_DEBUG, module, fmtstr)
    
    def logInfo(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self.__log(pylog.LOG_INFO, module, fmtstr)
    
    def logWarn(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self.__log(pylog.LOG_WARN, module, fmtstr)
    
    def logError(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self.__log(pylog.LOG_ERROR, module, fmtstr)
    
    def logFatal(self, module, fmtinfo, *args):
        fmtstr = fmtinfo % args
        self.__log(pylog.LOG_FATAL, module, fmtstr)
