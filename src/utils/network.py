from utils.constants import NETWORK_CFG


def getNodes():
    nodes = []
    with open(NETWORK_CFG, "r") as f:
        for node in f.readlines():
            nodes.append(node.rstrip('\n'))
    return nodes


def getNodesExcept(node):
    nodes = getNodes()
    if node in nodes:
        nodes.remove(node)
    return nodes
