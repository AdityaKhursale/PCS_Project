import os

from database.dfs_db import DfsDB

NETWORK_CFG_FILE = "network.cfg"
CONFIG_PATH = "configs"
NETWORK_CFG = os.path.join(CONFIG_PATH, NETWORK_CFG_FILE)

# @TODO Set the hard-coded values correctly.
def init_env():
    global dir_path
    global host_name
    global db_instance

    dir_path = "/home/gaurav/Documents/"
    host_name = "host1"
    db_instance = DfsDB(host_name)
