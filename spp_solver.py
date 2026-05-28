import osmnx as ox
import math
import heapq
import time
class NetworkSolver:
    def __init__(self, instance_name, network,):
        self.instance_name = instance_name
        self.network = network
    def dijkstra(self, start_id, end_id):
        # 1. INIZIALIZZAZIONE
        perm = set() # Equivalente a S (nodi permanenti), inizializzato vuoto
        temp = set(self.network.nodes.keys()) # Equivalente a S_bar (nodi temporanei), inizializzato con tutti i nodi
        
        # d(i) = +infinito per tutti, tranne d(s) = 0
        distances = {node_id: float('inf') for node_id in self.network.nodes}
        distances[start_id] = 0
        
        # pred(i) = None per tutti
        predecessors_edge = {node_id: None for node_id in self.network.nodes}
        
        print(f"\n[Dijkstra Teorico] Calcolo percorso da {start_id} a {end_id}...")

        # 2. CICLO PRINCIPALE: Finché |S| < |N|
        while len(perm) < len(self.network.nodes):
            
            # SELEZIONE DEL NODO MINIMO IN S_bar (temp) 
            # Selezionare il nodo i in temp con d(i) = min { d(j) : j in temp }
            current_dist = float('inf')
            u = None
            
            for nodo in temp:
                if distances[nodo] < current_dist:
                    current_dist = distances[nodo]
                    u = nodo
                    
            # Se 'u' è None, tutti i nodi rimasti sono irraggiungibili
            if u is None:
                break
                
            # Early Exit: ottimizzazione pratica per fermarsi all'arrivo
            if u == end_id:
                break
                
            # Il nodo è stato selezionato: lo togliamo dai temporanei e lo mettiamo nei permanenti
            temp.remove(u)
            perm.add(u)
            
            #  RILASSAMENTO 
            # Per ogni arco (i,j) in A
            for edge in self.network.adj_list[u]:
                v = edge.tail.get_id()
                
                # Ottimizzazione logica: aggiorniamo solo i nodi che sono ancora Temporanei
                if v in temp:
                    new_cost = distances[u] + edge.len
                    
                    # se d(j) > d(i) + c_ij
                    if distances[v] > new_cost:
                        distances[v] = new_cost          # d(j) = d(i) + c_ij
                        predecessors_edge[v] = edge      # pred(j) = i (salviamo l'arco per comodità)

        # 3. RICOSTRUZIONE DEL PERCORSO
        if distances[end_id] == float('inf'):
            return None, float('inf')

        path_edges = []
        current = end_id
        
        while current != start_id:
            arco_usato = predecessors_edge[current]
            path_edges.append(arco_usato)
            current = arco_usato.head.get_id() 
            
        path_edges.reverse()
        
        return path_edges, distances[end_id]
    
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

def nearest_node(network, target_x, target_y):
    """
    Trova l'ID del nodo della rete più vicino a una data coppia di coordinate.
    x = Longitudine, y = Latitudine.
    """
    nearest_node = None
    distanza_minima = float('inf')

    # Iteriamo su tutti i nodi della tua rete
    for node_id, node in network.nodes.items():
        # Calcoliamo la distanza in linea d'aria tra le coordinate inserite e il nodo
        distanza = math.hypot(node.x - target_x, node.y - target_y)

        # Se troviamo un nodo più vicino di quello precedente, aggiorniamo il node id
        if distanza < distanza_minima:
            distanza_minima = distanza
            nearest_node = node_id

    return nearest_node



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


    




    y_partenza, x_partenza = 39.214241, 9.107818
    

    y_arrivo, x_arrivo = 39.225522, 9.113819
    
    print("\nRicerca dei punti di accesso stradali più vicini...")
    
    partenza = nearest_node(cagliari_net, target_x=x_partenza, target_y=y_partenza)
    arrivo = nearest_node(cagliari_net, target_x=x_arrivo, target_y=y_arrivo)
    
    print(f"Nodo di partenza: {partenza}")
    print(f"Nodo di arrivo: {arrivo}")
    print(f"\nAvvio test da {partenza} a {arrivo}")
    
    # Avvia il cronometro ad alta precisione
    start_time = time.perf_counter()
    
    # Esegue l'algoritmo puro
    percorso, costo = solver.dijkstra(start_id=partenza, end_id=arrivo)
    
    # Ferma il cronometro
    end_time = time.perf_counter()
    
    # Calcola il tempo trascorso (in millisecondi e secondi)
    tempo_esecuzione_ms = (end_time - start_time) * 1000
    tempo_esecuzione_s = end_time - start_time
    

    print("\n     RISULTATO DIJKSTRA    \n")
    if percorso:
        print(f"Costo Totale: {costo:.2f} metri")
        print(f"Incroci: {len(percorso) + 1}") # +1 per contare i nodi, non gli archi
        print(f"Tempo di calcolo CPU: {tempo_esecuzione_ms:.4f} millisecondi ({tempo_esecuzione_s:.6f} secondi)")
        
        # Estrai i nomi delle strade dagli oggetti Edge
        strade_percorse = []
        for arco in percorso:
            if not strade_percorse or arco.name != strade_percorse[-1]:
                strade_percorse.append(arco.name)
        
        print("\nITINERARIO STRADALE:")
        #for i, via in enumerate(strade_percorse, 1):
        #    print(f"  {i}. {via}")

        #  Converti gli oggetti Edge in una lista di ID Nodi
        percorso_nodi = [partenza]
        for arco in percorso:
            percorso_nodi.append(arco.tail.get_id())

        print("\nGenerazione mappa in corso...")
        fig, ax = ox.plot_graph_route(
            G,                     
            percorso_nodi,         
            route_color='red',     
            route_linewidth=4,     
            node_size=0,           
            bgcolor='black'        
        )
    else:
        print("Percorso non trovato.")