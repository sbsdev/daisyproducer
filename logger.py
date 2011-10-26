import logging

logging.config.fileConfig('logging.conf')

def getLogger(name):
    return logging.getLogger(name)
