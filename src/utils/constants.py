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

ASSETS = "assets"


def setupGlobalConstants(address, host):
    global dir_path
    global host_name
    global db_instance
    global ip_addr
    global private_key_path
    global public_key_path

    host_name = host
    ip_addr = address
    dir_path = os.path.join(ASSETS, host_name)
    private_key_path = os.path.join(dir_path, "private_key")
    public_key_path = os.path.join(dir_path, "public_key")
    db_instance = DfsDB(host_name)
