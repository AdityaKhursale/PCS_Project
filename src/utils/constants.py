import os

from database.dfs_db import DfsDB

NETWORK_CFG_FILE = "network.cfg"
CONFIG_PATH = "configs"
NETWORK_CFG = os.path.join(CONFIG_PATH, NETWORK_CFG_FILE)


def init_env():
    # @TODO Set the hard-coded values correctly.
    global dir_path
    global host_name
    global db_instance
    global ip_addr

    dir_path = "/home/gaurav/Documents/"
    host_name = "host1"
    db_instance = DfsDB(host_name)
    ip_addr = "0.0.0.0"
