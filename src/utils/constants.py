import os

from database.dfs_db import DfsDB

NETWORK_CFG_FILE = "network.cfg"
CONFIG_PATH = "configs"
NETWORK_CFG = os.path.join(CONFIG_PATH, NETWORK_CFG_FILE)


def init_env(ip_address, host):
    global dir_path
    global host_name
    global db_instance
    global ip_addr

    host_name = host
    ip_addr = ip_address
    dir_path = "assets/" + host_name
    db_instance = DfsDB(host_name)
