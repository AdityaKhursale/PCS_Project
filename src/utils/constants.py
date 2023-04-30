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


def setupGlobalConstants(address, host):
    global host_name
    global db_instance
    global ip_addr

    host_name = host
    ip_addr = address
    db_instance = DfsDB(host_name)
