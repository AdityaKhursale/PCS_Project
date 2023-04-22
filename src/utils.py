
# Fetch all IPs of the nodes in the netwok.
def get_nodes_in_network():
    network_file = open('network.cfg', 'r')
    node_ips = []
    for ip in network_file.readlines():
        node_ips.append(ip.rstrip('\n'))
    
    return node_ips

# Get IPs of other nodes in the network.
def get_other_nodes_in_network(current_node_ip):
    nodes = get_nodes_in_network()
    nodes.remove(current_node_ip)

    return nodes