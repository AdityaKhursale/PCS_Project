import ast
import logging
import logging.config
import logging.handlers
import os
import yaml

from utils import constants
from utils import file_io as fileIO


class DirectoryEnsuredFileHandler(logging.handlers.RotatingFileHandler):
    # pylint: disable=too-many-arguments
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=False, errors=None):
        fileIO.createDir(os.path.dirname(filename))
        super().__init__(filename, mode, maxBytes,
                         backupCount, encoding, delay, errors)


def getLogger(loggerName, substituteValueByKeys=None):
    with open(constants.LOGGING_CFG, encoding="utf8") as f:
        loggingCfg = yaml.safe_load(f.read())
    if substituteValueByKeys:
        for k, v in substituteValueByKeys.items():
            loggingCfg = ast.literal_eval(
                repr(loggingCfg).replace(k, v))
    logging.config.dictConfig(loggingCfg)
    return logging.getLogger(loggerName)
