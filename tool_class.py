#editor ref
#encoding=utf-8

import sys, os,re,csv,time
import cPickle as p



class Stack(object):
    def __init__(self):
        self.stack = []
    def push(self,object):
        self.stack.append(object)
    def pop(self):
        return self.stack.pop()
    def length(self):
        return len(self.stack)

class Count:
    def __init__(self):
        self.setdir=os.path.abspath('.')
        self.tabLen=0
        self.erroLogger=self.setdir+'\\date\\'+'errolog.log'
        self.runLogger=self.setdir+'\\date\\'+'runlog.log'
    def setTabLen(self,num):
        self.tabLen=num
    def getTabLen(self):
        return self.tabLen
    def getErroLogger(self):
        return self.erroLogger
    def getRunLogger(self):
        return self.runLogger
    def printMember(self):
        print 'dir is: ',self.setdir
        print 'tablen is: ',self.tabLen
        print 'erroLogger: ',self.erroLogger
        print 'runLogger: ',self.runLogger

def initlog(logfile):
    import logging
    logger = logging.getLogger()
    if os.path.isfile(logfile)!=True:
        if os.path.exists(os.path.dirname(logfile))!=True:
            os.mkdir(os.path.dirname(logfile))
        open('logfile','w').close()
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.WARN)
    return logger


def write_cPickle(list,outfile):
    f = file(outfile, 'w')
    p.dump(list, f) # dump the object to a file
    f.close()
    
def read_cPickle(infile):
    list=[]
    f=open(infile,'r')
    list=p.load(f)
    return list    
        
        
if __name__=='__main__':
    c1=Count()
    print c1.getErroLogger()

    c1.setTabLen(3)
    initlog(c1.getErroLogger().decode('gbk'))
    print c1.getTabLen()
    print c1.getErroLogger()
    print c1.getRunLogger()

    