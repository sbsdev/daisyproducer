import logging
import logging.config
import os.path

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.conf'))

def getLogger(name):
    return logging.getLogger(name)
