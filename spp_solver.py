import osmnx as ox

class NetworkSolver:
    def __init__(self, instance_name, network,):
        self.instance_name = instance_name
        self.network = network
    
    def dijkstra(self):
        print()
    
    def dial_dijkstra(self):
        print()

    def A_star(self):
        print()

class Node:
    def __init__(self, id, x, y,):
        self.id = id
        self.x = x
        self.y = y

    def get_id(self):
        return self.id
    
    def get_coordinates(self):
        return (self.x, self.y)
    
    def __repr__(self) -> str:
        return f"Node({self.id, self.get_coordinates})"

class Edge:
    def __init__(self, edge_id, head, tail, length, name = "UNK"):
        try:

            if length < 0:
                raise ValueError(f"Trovata lunghezza negativa ({length})")
            self.id = edge_id
            self.name = name
            self.head = head
            self.tail = tail
            self.len = length
            self.weight = int(round(length))
        except ValueError as e:
            print(f"Avviso: Valore non valido in via '{self.name}' ({e}).")
    

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
        self.edges.append(newEdge)
        id_partenza = newEdge.head.get_id()
        #liste di adiacenza
        self.adj_list[id_partenza].append(newEdge)
        #max edge weight
        if newEdge.weight > self.max_edge_weight:
            self.max_edge_weight = newEdge.weight

    def get_node_list(self):
        return self.nodes
    
    def get_edge_list(self):
        return self.edges







if __name__ == '__main__':

    

    G = ox.load_graphml(filepath="cagliari.graphml")

    stats = ox.basic_stats(G)
    print(f"Nodi (n): {stats['n']} | Archi (m): {stats['m']}")
    cagliari_net = Network()

    for node_id, data in G.nodes(data=True):
        # Crea il tuo oggetto Node
        nuovo_nodo = Node(id=node_id, x=data['x'], y=data['y'])
        cagliari_net.add_node(nuovo_nodo)
    edge_counter = 0

    for u, v, data in G.edges(data=True):
        edge_counter += 1
        
        # Recupera gli oggetti Nodo già creati
        nodo_partenza = cagliari_net.nodes[u]
        nodo_arrivo = cagliari_net.nodes[v]
        
        # Estrae i dati gestendo eventuali liste
        lunghezza_grezza = data.get('length', 1.0)
        nome_via = data.get('name', 'Sconosciuta')
        if isinstance(nome_via, list):
            nome_via = nome_via[0]
            
        # Crea il tuo oggetto Edge
        nuovo_arco = Edge(
            edge_id=f"E{edge_counter}", 
            head=nodo_partenza, 
            tail=nodo_arrivo, 
            length=lunghezza_grezza, 
            name=nome_via
        )
        
        # Inserisce l'arco nella rete (e calcola max_edge_weight)
        cagliari_net.add_edge(nuovo_arco)

    print(f"Nodi Rete: {len(cagliari_net.nodes)} | Archi Rete: {len(cagliari_net.edges)}")
    print(f"Max Edge Weight per Dial: {cagliari_net.max_edge_weight}")
    
    
    solver = NetworkSolver(instance_name="Routing_Cagliari", network=cagliari_net)

    