import socket

from utils.constants import NETWORK_CFG


def getNodes():
    nodes = []
    with open(NETWORK_CFG, "r", encoding="utf-8") as f:
        for node in f.readlines():
            nodes.append(node.rstrip('\n'))
    return nodes


def getNodesExcept(node):
    nodes = getNodes()
    if node in nodes:
        nodes.remove(node)
    return nodes


def isValidIpAddress(ipAddress):
    try:
        socket.inet_aton(ipAddress)
        return True
    except socket.error:
        return False
