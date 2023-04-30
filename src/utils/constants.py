import os

from database.dfs_db import DfsDB
from utils.misc import HostAddressMapper

# Configs

CONFIG_PATH = os.path.join("src", "configs")
LOGGING_CFG_FILE = "logging_config.yml"
LOGGING_CFG = os.path.join(CONFIG_PATH, LOGGING_CFG_FILE)

# Logs

LOG_DIR = os.path.join("logs")

# Assets

ASSETS = os.path.join("assets")

# global constants

HOST_NAME = ""
ADDRESS = ""
DB_INSTANCE = None
HOST_ADDRESS_BY_NAME = HostAddressMapper()

# pylint: disable=global-statement


def setupGlobalConstants(address, host):
    global HOST_NAME, ADDRESS, DB_INSTANCE

    HOST_NAME = host
    ADDRESS = address
    HOST_ADDRESS_BY_NAME[HOST_NAME] = ADDRESS
    DB_INSTANCE = DfsDB(HOST_NAME)


def cleanup():
    del HOST_ADDRESS_BY_NAME[HOST_NAME]
