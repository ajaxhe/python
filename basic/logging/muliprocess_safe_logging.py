#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
ref links:
http://www.jianshu.com/p/d615bf01e37b
http://www.cnblogs.com/restran/p/4743840.html
'''

import logging
import logging.config
import multiprocessing
import time

import SafeFileHandler

logging.config.fileConfig('./conf/logging.conf')
logger = logging.getLogger()

def run(idx):
    while True:
        logger.debug('[%d] logging', idx)
        time.sleep(1)

def main():
    p_num = 16
    for i in range(p_num):
        p = multiprocessing.Process(target=run, args=(i+1,))
        p.daemon = True
        p.start()

    while True:
        var = raw_input('Enter s for stop:\n')
        if var == 's':
            break

    for p in multiprocessing.active_children():
        logger.info('shutting down processing %r', p)
        p.terminate()
        p.join()
    
    logger.info('all done')

if __name__ == '__main__':
    main()
