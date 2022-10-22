import logging
import os
from filepaths import paths
from datetime import date
from functools import wraps

def makedir(func):
    # @wraps
    def wrapper(*args, **kwargs):
        os.makedirs(paths["database"] + str(date.today()) + paths["log"], exist_ok=True)
        os.makedirs(paths["database"] + str(date.today()) + paths["records"], exist_ok=True)
        os.makedirs(paths["database"] + str(date.today()) + paths["timelapse"], exist_ok=True)
        func(*args, **kwargs)
    return wrapper

class DirTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, **kwargs):
        logging.handlers.TimedRotatingFileHandler.__init__(self, **kwargs)
    
    @makedir
    def emit(self,record):
        """
        Emit a record.

        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        filename = paths["database"] + str(date.today()) + paths["log"] + str(date.today()) + "_log.csv"
        self.baseFilename = os.path.abspath(filename)
        try:
            if self.shouldRollover(record):
                self.doRollover()
            logging.FileHandler.emit(self, record)
        except Exception:
            self.handleError(record)

def setup_logger(level, path):
    logger = logging.getLogger(__name__)
    
    logging.basicConfig(level = level)
    
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s',
                                  "%Y-%m-%d %H:%M:%S")
    
    handler = DirTimedRotatingFileHandler(
        filename = paths["database"] + str(date.today()) + paths["log"] + str(date.today()) + "_log.csv",
        when='midnight',
        interval=0,
        backupCount=0,
        encoding=None,
        delay=True,
        utc=False,
        atTime=None,
        errors=None)
    
    handler.suffix = "%Y-%m-%d_%H-%M-%S" + ".csv"
    handler.setFormatter(formatter)
    
    logging.getLogger('').addHandler(handler)
    
    logger.debug("Logger is set up.")
