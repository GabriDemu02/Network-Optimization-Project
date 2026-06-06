import osmnx as ox
import math
import heapq

class NetworkSolver:
    """
    Classe degli algoritmi per la risoluzione dello Shortest Path Problem
    """

    def __init__(self, instance_name, network):
        self.instance_name = instance_name
        self.network = network

    def reconstruct_path(self, start_id, end_id, distances, predecessors_edge):
            """
            Ricostruisce il percorso a ritroso partendo dal nodo di destinazione.
            """
            # Se la destinazione non è stata raggiunta
            if distances[end_id] == float('inf'):
                return None, float('inf')
                
            path_edges = []
            current = end_id
            cost = 0.0 
            
            # Si ripercorrono gli archi a partire dal nodo destinazione all'indietro
            while current != start_id:
                arco_usato = predecessors_edge[current]
                
                # Controllo di sicurezza: se manca il predecessore prima di arrivare alla sorgente
                if arco_usato is None:
                    return None, float('inf')
                    
                path_edges.append(arco_usato)
                
                # Sommiamo la lunghezza originale con la precisione float
                cost += arco_usato.len 
                
                # Torna indietro verso la sorgente dell'arco
                current = arco_usato.head.get_id()
                
            # Invertiamo la lista per avere il percorso dalla sorgente alla destinazione
            path_edges.reverse()
            
            return path_edges, cost

    def dijkstra(self, start_id, end_id):
        # 1. INIZIALIZZAZIONE
        perm = set() # Equivalente a S (nodi permanenti), inizializzato vuoto
        temp = set(self.network.nodes.keys()) # Equivalente a S_bar (nodi temporanei), inizializzato con tutti i nodi
        
        # d(i) = +infinito per tutti, tranne d(s) = 0
        distances = {node_id: float('inf') for node_id in self.network.nodes}
        distances[start_id] = 0
        
        # pred(i) = None per tutti
        predecessors_edge = {node_id: None for node_id in self.network.nodes}
        
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
                    new_cost = distances[u] + edge.weight
                    
                    # se d(j) > d(i) + c_ij
                    if distances[v] > new_cost:
                        distances[v] = new_cost          # d(j) = d(i) + c_ij
                        predecessors_edge[v] = edge      # pred(j) = i (salviamo l'arco per comodità)

        # 3. RICOSTRUZIONE DEL PERCORSO
        return self.reconstruct_path(start_id, end_id, distances, predecessors_edge)

    def dial_dijkstra_cir(self, start_id, end_id):
        
        # 1. RECUPERO COSTO MASSIMO (Usiamo la proprietà della rete per fare prima)
        max_c = self.network.max_edge_weight
        bucket_size = max_c + 1 
        
        # 2. INIZIALIZZAZIONE VARIABILI (Stessa base logica di Dijkstra)
        perm = set() 
        temp = set(self.network.nodes.keys()) # Aggiunto per mantenere la logica base di Dijkstra
        
        distances = {node_id: float('inf') for node_id in self.network.nodes}
        distances[start_id] = 0 
        
        predecessors_edge = {node_id: None for node_id in self.network.nodes}
        
        # Inizializzazione Array Circolare
        buckets = [set() for _ in range(bucket_size)]
        buckets[0].add(start_id)
        
        current_dist = 0
        nodes_in_buckets = 1 
        
        # 3. CICLO PRINCIPALE
        while nodes_in_buckets > 0 and len(perm) < len(self.network.nodes):
            
            # Gira sull'array circolare finché non trova un bucket pieno
            while not buckets[current_dist % bucket_size]:
                current_dist += 1
                if current_dist > len(self.network.nodes) * max_c:
                    break
            
            if current_dist > len(self.network.nodes) * max_c:
                break
                
            u = buckets[current_dist % bucket_size].pop()
            nodes_in_buckets -= 1 
            
            if u == end_id:
                break
                
            if u in perm:
                continue
                
            # Il nodo è stato selezionato: lo togliamo dai temporanei e lo mettiamo nei permanenti
            if u in temp:
                temp.remove(u)
            perm.add(u)
            
            # RILASSAMENTO
            # Esplorazione dei vicini
            for edge in self.network.adj_list[u]:
                v = edge.tail.get_id() # Il nodo destinazione dell'arco
                edge_cost = edge.weight
                
                # Ottimizzazione logica: aggiorniamo solo i nodi che sono ancora Temporanei
                if v in temp:
                    new_cost = distances[u] + edge_cost
                    
                    if distances[v] > new_cost:
                        old_dist = distances[v]
                        
                        # Se era in un altro bucket, lo togliamo
                        if old_dist != float('inf'):
                            buckets[int(old_dist) % bucket_size].remove(v)
                            nodes_in_buckets -= 1
                            
                        distances[v] = new_cost
                        predecessors_edge[v] = edge
                        
                        # Lo inseriamo nel nuovo bucket posizionato col modulo
                        buckets[int(new_cost) % bucket_size].add(v)
                        nodes_in_buckets += 1

        # 4. RICOSTRUZIONE DEL PERCORSO (con calcolo basato su .len float)
        return self.reconstruct_path(start_id, end_id, distances, predecessors_edge)

    def dial_dijkstra(self, start_id, end_id):
        
        # 1. CALCOLO DELLA DISTANZA MASSIMA DEGLI EDGE DEL GRAFO
        max_c = 0
        for node_id in self.network.nodes:
            for edge in self.network.adj_list[node_id]:
                cost = edge.weight # intero per l'indice del bucket
                if cost > max_c:
                    max_c = cost
        
        num_nodes = len(self.network.nodes)
        max_possible_dist = (num_nodes - 1) * max_c # (n-1)*C al massimo

        # 2. INIZIALIZZAZIONE VARIABILI PRINCIPALI (Stessa base logica di Dijkstra)
        perm = set() # nodi permanenti
        temp = set(self.network.nodes.keys()) # nodi temporanei
        
        distances = {node_id: float('inf') for node_id in self.network.nodes} # dict delle distanze dalla sorgente per ogni nodo
        distances[start_id] = 0 # nodo sorgente ha distanza nulla
        
        predecessors_edge = {node_id: None for node_id in self.network.nodes}
        
        # INIZIALIZZAZIONE SET DI BUCKETS (Implementazione di Dial)
        buckets = [set() for _ in range(max_possible_dist + 1)] # set dei bucket per l'accesso rapido ai nodi
        buckets[0].add(start_id) # inserisco nodo sorgente nel primo bucket 0 (distanza nulla)
        
        current_bucket_idx = 0 # indice di tracciamento del bucket corrente

        # 3. CICLO PRINCIPALE (Finchè la cardinalità del set di nodi permanenti non eguaglia quella del set di nodi del grafo)
        while len(perm) < len(self.network.nodes):
            
            # Itera i buckets dal basso verso l'alto finché non trova il primo non vuoto (distanza minima)
            while current_bucket_idx <= max_possible_dist and not buckets[current_bucket_idx]:
                current_bucket_idx += 1
                
            # Se la distanza massima viene superata, allora i restanti nodi sono irraggiungibili, quindi esce dal ciclo
            if current_bucket_idx > max_possible_dist:
                break
                
            # Si estrae un nodo dal bucket minimo corrente
            u = buckets[current_bucket_idx].pop()
            
            # Se il nodo corrisponde alla destinazione, esce dal ciclo
            if u == end_id:
                break
                
            # Se il nodo pescato è permanente, allora prosegue con la prossima iterazione
            if u in perm:
                continue
                
            # Si rende il nodo permanente e lo si toglie dai temporanei (logica base Dijkstra)
            temp.remove(u)
            perm.add(u)
            
            # RILASSAMENTO
            # Iterazione per ogni edge uscente al nodo u
            for edge in self.network.adj_list[u]:
                v = edge.tail.get_id() # prendo il nodo coda v
                edge_cost = edge.weight # si assicura che il costo sia intero
                
                # Se il nodo coda è temporaneo, allora si verifica la sua distanza dalla sorgente passando per u
                if v in temp:
                    new_cost = distances[u] + edge_cost
                    
                    # Se maggiore, allora si può aggiornare con la nuova distanza
                    if distances[v] > new_cost:
                        old_dist = distances[v]
                        
                        # Se il nodo aveva già una distanza finita, si rimuove dal suo vecchio bucket
                        if old_dist != float('inf'):
                            buckets[int(old_dist)].remove(v)
                            
                        # Si aggiorna la distanza e l'edge predecessore
                        distances[v] = new_cost
                        predecessors_edge[v] = edge
                        
                        # Inseriamo il nodo nel nuovo bucket
                        buckets[int(new_cost)].add(v)

        # 4. RICOSTRUZIONE DEL PERCORSO
        return self.reconstruct_path(start_id, end_id, distances, predecessors_edge)

    def a_star(self, start_id, end_id):
            nodes = self.network.nodes
            end_node = nodes[end_id]
            
            # FUNZIONE EURISTICA (DISTANZA EUCLIDEA)
            def heuristic(node_id):
                current_node = nodes[node_id]
                return math.hypot(current_node.x - end_node.x, current_node.y - end_node.y)

            def heuristic_chebyshev(node_id):
                current_node = nodes[node_id]
                dx = abs(current_node.x - end_node.x)
                dy = abs(current_node.y - end_node.y)
                # Distanza di Chebyshev: Ammissibile e molto veloce
                return max(dx, dy)

            # 1. INIZIALIZZAZIONE (Stessa base logica di Dijkstra)
            perm = set() # Equivalente a S (nodi permanenti), inizializzato vuoto
            temp = set(self.network.nodes.keys()) # Equivalente a S_bar (nodi temporanei), inizializzato con TUTTI i nodi
            
            # g(i) = +infinito per tutti, tranne g(s) = 0
            distances = {node_id: float('inf') for node_id in self.network.nodes}
            distances[start_id] = 0
            
            # pred(i) = None per tutti
            predecessors_edge = {node_id: None for node_id in self.network.nodes}
            
            # 2. CICLO PRINCIPALE: Finché |S| < |N|
            while len(perm) < len(self.network.nodes):
                
                # SELEZIONE DEL NODO MINIMO IN S_bar (temp)
                # Selezionare il nodo i in temp con f(i) = min { g(j) + h(j) : j in temp }
                current_f = float('inf')
                u = None
                
                for nodo in temp:
                    # A* valuta il nodo in base alla somma del costo reale accumulato (g) e dell'euristica (h)
                    f_score = distances[nodo] + heuristic(nodo)
                    if f_score < current_f:
                        current_f = f_score
                        u = nodo
                        
                # Se 'u' è None, tutti i nodi rimasti sono irraggiungibili (grafo non connesso)
                if u is None:
                    break
                    
                # Early Exit: ottimizzazione per fermarsi appena la destinazione diventa permanente
                if u == end_id:
                    break
                    
                # Il nodo è stato selezionato: lo togliamo dai temporanei e lo mettiamo nei permanenti
                temp.remove(u)
                perm.add(u)
                
                # RILASSAMENTO 
                # Per ogni arco (i,j) in A
                for edge in self.network.adj_list[u]:
                    v = edge.tail.get_id()
                    
                    # Aggiorniamo solo i nodi che sono ancora Temporanei
                    if v in temp:
                        new_cost = distances[u] + edge.weight # g(i) + c_ij
                        
                        # Se g(j) > g(i) + c_ij
                        if distances[v] > new_cost:
                            distances[v] = new_cost          # Aggiorniamo g(j)
                            predecessors_edge[v] = edge      # pred(j) = i

            # 3. RICOSTRUZIONE DEL PERCORSO
            return self.reconstruct_path(start_id, end_id, distances, predecessors_edge)

class Node:
    """
    Classe della struttura del nodo
    """
    def __init__(self, id, x, y):
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
    """
    Classe della struttura dell'edge
    """

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
    """
    Classe della struttura della rete
    """

    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.adj_list = {}
        self.max_edge_weight = 0
        
    def add_node(self, newNode):
        if newNode.get_id() not in self.nodes.keys():
            self.nodes[newNode.get_id()] = newNode
            self.adj_list[newNode.get_id()] = []
        else: 
            print("The node already exists in network.")
    
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