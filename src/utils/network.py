from utils.constants import NETWORK_CFG


def get_nodes():
    nodes = []
    with open(NETWORK_CFG, "r") as f:
        for node in f.readlines():
            nodes.append(node.rstrip('\n'))
    return nodes


def get_nodes_except(node):
    nodes = get_nodes()
    if node in nodes:
        nodes.remove(node)
    return nodes
