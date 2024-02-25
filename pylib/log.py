import logging
from .logger_formatting import* 
import sys

global default_log_level
default_log_level = logging.INFO

#Set up logging
def init_logging(log_level = logging.INFO):
    formatstr = '%(asctime)s.%(msecs)d  %(name)s  %(levelname)s  %(message)s'
    datefmt = '%H:%M:%S'
    global default_logging_level
    default_logging_level = log_level
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(default_logging_level)
    console.setFormatter(ColoredFormatter(formatstr, datefmt))
    logging.getLogger('').addHandler(console)

#Decorator for linking up a class with a named logger
def with_logging(obj):
    obj.logger = logging.getLogger(obj.__name__)
    obj.log = obj.logger
    obj.log.setLevel(default_log_level)
    return obj

