# http://lightthewoods.me/2013/11/18/Python%E5%A4%9A%E8%BF%9B%E7%A8%8Blog%E6%97%A5%E5%BF%97%E5%88%87%E5%88%86%E9%94%99%E8%AF%AF%E7%9A%84%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88/
# http://www.jianshu.com/p/d615bf01e37b

import time
import os
import fcntl
import struct

from logging.handlers import TimedRotatingFileHandler

class MultiProcessTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, delay, utc)

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        #if self.stream:
        #    self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        #if os.path.exists(dfn):
        #    os.remove(dfn)
        lockdata = struct.pack('hhllhh', fcntl.F_WRLCK, 0, 0, 0, 0, 0)
        fcntl.fcntl(self.stream, fcntl.F_SETLKW, lockdata)
        if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
            with open(self.baseFilename, 'a'):
                pass
        if self.backupCount > 0:
            # find the oldest log file and delete it
            #s = glob.glob(self.baseFilename + ".20*")
            #if len(s) > self.backupCount:
            #    s.sort()
            #    os.remove(s[0])
            for s in self.getFilesToDelete():
                os.remove(s)
        #print "%s -> %s" % (self.baseFilename, dfn)
        if self.stream:
            self.stream.close()
        self.mode = 'a'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    newRolloverAt = newRolloverAt - 3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    newRolloverAt = newRolloverAt + 3600
        self.rolloverAt = newRolloverAt

