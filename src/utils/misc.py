import logging
import logging.config
import yaml

from utils import constants, file


def getLogger(loggerName):
    file.createDir(constants.LOG_DIR)
    with open(constants.LOGGING_CFG) as f:
        loggingCfg = yaml.safe_load(f.read())
    logging.config.dictConfig(loggingCfg)
    return logging.getLogger(loggerName)
