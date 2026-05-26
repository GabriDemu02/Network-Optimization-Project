import math
import osmnx as ox

class NetworkSolver:
    def __init__(self, instance_name, network,):
        self.instance_name = instance_name,
        self.network = network,
    
    def dijkstra(self):
        print()
    
    def dial_dijkstra(self):
        print()

    def A_star(self):
        print()

class Node:
    def __init__(self, id, x, y,):
        self.id = id,
        self.x = x,
        self.y = y,

    def get_id(self):
        return self.id
    
    def get_coordinates(self):
        return (self.x, self.y)
    
    def __repr__(self) -> str:
        return f"Node({self.id, self.get_coordinates})"

class Edge:
    def __init__(self, id, head, tail, len, name = "UNK",):
        self.id = id,
        self.name = name,
        self.head = head,
        self.tail = tail,
        self.len = len,
        self.weight = int(round(len)),

    def get_id(self):
        return self.id

    def get_edge(self):
        return (self.head, self.tail, self.weight)
    
    def __repr__(self) -> str:
        return f"Edge({self.id, self.name, self.get_edge})"

class Network:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.adj_list = {}
        self.max_edge_weight = 0
        
    def add_node(self, newNode):
        if newNode.get_id() not in self.nodes.keys():
            self.nodes[newNode.get_id()] = newNode
            self.adj_list[newNode.get_id()] = []
        else: print("The node already exists in network.")
    
    def add_edge(self, newEdge):
        if newEdge.len() 


    def get_node_list(self):
        return self.nodes
    
    def get_edge_list(self):
        return self.edges

if __name__ == '__main__':

    

    G = ox.load_graphml(filepath="cagliari.graphml")

    stats = ox.basic_stats(G)
    print(f"Nodi (n): {stats['n']} | Archi (m): {stats['m']}")