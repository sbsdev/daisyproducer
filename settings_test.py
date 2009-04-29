from settings import *

DEBUG = TEMPLATE_DEBUG = True

DATABASE_ENGINE = 'mysql'
DATABASE_OPTIONS = {
    "default-character-set": "utf8",
    "init_command": "SET storage_engine=INNODB",
}
DATABASE_NAME = 'daisyproducer_test'
DATABASE_USER = 'daisyproducer'
DATABASE_PASSWORD = ''
