import logging
import logging.config

logging.config.fileConfig('logging.conf')

def getLogger(name):
    return logging.getLogger(name)
