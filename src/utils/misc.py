import ast
import logging
import logging.config
import logging.handlers
import os
import yaml

from utils import constants, file


class DirectoryEnsuredFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=False, errors=None):
        file.createDir(os.path.dirname(filename))
        super().__init__(filename, mode, maxBytes,
                         backupCount, encoding, delay, errors)


def getLogger(loggerName, substituteValueByKeys=dict()):
    with open(constants.LOGGING_CFG) as f:
        loggingCfg = yaml.safe_load(f.read())
    for k, v in substituteValueByKeys.items():
        loggingCfg = ast.literal_eval(
            repr(loggingCfg).replace(k, v))
    logging.config.dictConfig(loggingCfg)
    return logging.getLogger(loggerName)
