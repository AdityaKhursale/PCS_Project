import socket

from utils.constants import HOST_ADDRESS_BY_NAME


def getNodes():
    nodes = list(HOST_ADDRESS_BY_NAME.values())
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
