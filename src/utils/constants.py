import os

from database.dfs_db import DfsDB

# Configs

CONFIG_PATH = os.path.join("src", "configs")
NETWORK_CFG_FILE = "network.cfg"
LOGGING_CFG_FILE = "logging_config.yml"
NETWORK_CFG = os.path.join(CONFIG_PATH, NETWORK_CFG_FILE)
LOGGING_CFG = os.path.join(CONFIG_PATH, LOGGING_CFG_FILE)

# Logs

LOG_DIR = os.path.join("logs")

# Assets

ASSETS = os.path.join("assets")

# global constants

HOST_NAME = ""
ADDRESS = ""
DB_INSTANCE = None

# pylint: disable=global-statement


def setupGlobalConstants(address, host):
    global HOST_NAME, ADDRESS, DB_INSTANCE

    HOST_NAME = host
    ADDRESS = address
    DB_INSTANCE = DfsDB(HOST_NAME)
