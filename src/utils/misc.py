import ast
import json
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


class HostAddressMapper:
    @property
    def _store(self):
        return os.path.join(os.getcwd(), "host_address_map.json")

    @property
    def _hostNameByAddress(self):
        hostNameByAddress = {}
        storeContents = fileIO.readFile(self._store)
        if storeContents:
            hostNameByAddress = json.loads(storeContents)
        return hostNameByAddress

    def __getitem__(self, key):
        return self._hostNameByAddress.get(key, "")

    def __setitem__(self, key, value):
        hostNameByAddress = self._hostNameByAddress
        hostNameByAddress[key] = value
        fileIO.writeFile(self._store, json.dumps(hostNameByAddress))

    def __delitem__(self, key):
        hostNameByAddress = self._hostNameByAddress
        del hostNameByAddress[key]
        fileIO.writeFile(self._store, json.dumps(hostNameByAddress))

    def __len__(self):
        return len(self._hostNameByAddress)

    def __iter__(self):
        return iter(self._hostNameByAddress)

    def __contains__(self, key):
        return key in self._hostNameByAddress

    def __repr__(self):
        return repr(self._hostNameByAddress)

    def keys(self):
        return self._hostNameByAddress.keys()

    def values(self):
        return self._hostNameByAddress.values()
