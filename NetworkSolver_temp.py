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
        
        # OTTIMIZZAZIONE FRONTIERA: temp inizializzato SOLO col nodo sorgente
        temp = {start_id} 
        
        # d(i) = +infinito per tutti, tranne d(s) = 0
        distances = {node_id: float('inf') for node_id in self.network.nodes}
        distances[start_id] = 0
        
        # pred(i) = None per tutti
        predecessors_edge = {node_id: None for node_id in self.network.nodes}
        
        # 2. CICLO PRINCIPALE: Finché ci sono nodi nella frontiera da esplorare
        while temp:
            
            # SELEZIONE DEL NODO MINIMO NELLA FRONTIERA (temp) 
            current_dist = float('inf')
            u = None
            
            for nodo in temp:
                if distances[nodo] < current_dist:
                    current_dist = distances[nodo]
                    u = nodo
                    
            # Se 'u' è None, la coda è vuota o rotta
            if u is None:
                break
                
            # Early Exit: ottimizzazione pratica per fermarsi all'arrivo
            if u == end_id:
                break
                
            # Il nodo è stato selezionato: lo togliamo dalla frontiera e lo mettiamo nei permanenti
            temp.remove(u)
            perm.add(u)
            
            # RILASSAMENTO E AGGIORNAMENTO FRONTIERA
            # Per ogni arco (i,j) uscente da u
            for edge in self.network.adj_list[u]:
                v = edge.tail.get_id()
                
                # Aggiorniamo solo se il nodo NON è già stato chiuso (non è permanente)
                if v not in perm:
                    new_cost = distances[u] + edge.weight
                    
                    # se d(j) > d(i) + c_ij
                    if distances[v] > new_cost:
                        distances[v] = new_cost          # d(j) = d(i) + c_ij
                        predecessors_edge[v] = edge      # pred(j) = i
                        
                        # Aggiungiamo il vicino alla frontiera temporanea
                        temp.add(v)

        # 3. RICOSTRUZIONE DEL PERCORSO
        return self.reconstruct_path(start_id, end_id, distances, predecessors_edge)

    def dial_dijkstra_cir(self, start_id, end_id):
        
        # 1. RECUPERO COSTO MASSIMO
        max_c = self.network.max_edge_weight
        bucket_size = max_c + 1 
        
        # 2. INIZIALIZZAZIONE VARIABILI
        perm = set() 
        # NOTA: Rimosso 'temp'. In Dial, i bucket stessi fungono nativamente da frontiera.
        
        distances = {node_id: float('inf') for node_id in self.network.nodes}
        distances[start_id] = 0 
        
        predecessors_edge = {node_id: None for node_id in self.network.nodes}
        
        # Inizializzazione Array Circolare
        buckets = [set() for _ in range(bucket_size)]
        buckets[0].add(start_id)
        
        current_dist = 0
        nodes_in_buckets = 1 
        
        # 3. CICLO PRINCIPALE
        while nodes_in_buckets > 0:
            
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
                
            # Se è già permanente lo ignoriamo
            if u in perm:
                continue
                
            # Lo rendiamo permanente
            perm.add(u)
            
            # RILASSAMENTO E AGGIORNAMENTO BUCKET (La nostra frontiera)
            for edge in self.network.adj_list[u]:
                v = edge.tail.get_id() 
                edge_cost = edge.weight
                
                # Se non è permanente, calcoliamo i costi
                if v not in perm:
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

        # 4. RICOSTRUZIONE DEL PERCORSO
        return self.reconstruct_path(start_id, end_id, distances, predecessors_edge)

    def dial_dijkstra(self, start_id, end_id):
        
        # 1. CALCOLO DELLA DISTANZA MASSIMA DEGLI EDGE DEL GRAFO
        max_c = 0
        for node_id in self.network.nodes:
            for edge in self.network.adj_list[node_id]:
                cost = edge.weight 
                if cost > max_c:
                    max_c = cost
        
        num_nodes = len(self.network.nodes)
        max_possible_dist = (num_nodes - 1) * max_c 

        # 2. INIZIALIZZAZIONE VARIABILI PRINCIPALI
        perm = set() 
        # NOTA: Come per il circolare, rimosso 'temp'. I bucket sono la frontiera.
        
        distances = {node_id: float('inf') for node_id in self.network.nodes} 
        distances[start_id] = 0 
        
        predecessors_edge = {node_id: None for node_id in self.network.nodes}
        
        # INIZIALIZZAZIONE SET DI BUCKETS 
        buckets = [set() for _ in range(max_possible_dist + 1)] 
        buckets[0].add(start_id) 
        
        current_bucket_idx = 0 
        
        # 3. CICLO PRINCIPALE 
        while current_bucket_idx <= max_possible_dist:
            
            # Itera i buckets dal basso verso l'alto finché non trova il primo non vuoto
            while current_bucket_idx <= max_possible_dist and not buckets[current_bucket_idx]:
                current_bucket_idx += 1
                
            # Se la distanza massima viene superata, esce
            if current_bucket_idx > max_possible_dist:
                break
                
            # Si estrae un nodo dal bucket minimo corrente
            u = buckets[current_bucket_idx].pop()
            
            if u == end_id:
                break
                
            if u in perm:
                continue
                
            # Si rende il nodo permanente 
            perm.add(u)
            
            # RILASSAMENTO E AGGIORNAMENTO BUCKETS
            for edge in self.network.adj_list[u]:
                v = edge.tail.get_id() 
                edge_cost = edge.weight 
                
                # Verifichiamo la distanza solo per i nodi non permanenti
                if v not in perm:
                    new_cost = distances[u] + edge_cost
                    
                    if distances[v] > new_cost:
                        old_dist = distances[v]
                        
                        # Se il nodo aveva già una distanza finita, si rimuove dal vecchio bucket
                        if old_dist != float('inf'):
                            buckets[int(old_dist)].remove(v)
                            
                        distances[v] = new_cost
                        predecessors_edge[v] = edge
                        
                        # Inseriamo il nodo nel nuovo bucket
                        buckets[int(new_cost)].add(v)

        # 4. RICOSTRUZIONE DEL PERCORSO
        return self.reconstruct_path(start_id, end_id, distances, predecessors_edge)
             

    def heuristic_euclidean(self, node_id, end_id):
        current_node = self.network.nodes[node_id]
        end_node = self.network.nodes[end_id]
        return math.hypot(current_node.x - end_node.x, current_node.y - end_node.y)

    def heuristic_chebyshev(self, node_id, end_id):
        current_node = self.network.nodes[node_id]
        end_node = self.network.nodes[end_id]
        dx = abs(current_node.x - end_node.x)
        dy = abs(current_node.y - end_node.y)
        return max(dx, dy)

    def heuristic_manhattan(self, node_id, end_id):
        current_node = self.network.nodes[node_id]
        end_node = self.network.nodes[end_id]
        dx = abs(current_node.x - end_node.x)
        dy = abs(current_node.y - end_node.y)
        return dx + dy
    def a_star(self, start_id, end_id, heuristic_func):
            nodes = self.network.nodes
            end_node = nodes[end_id]
            


            # 1. INIZIALIZZAZIONE
            perm = set() 
            
            # OTTIMIZZAZIONE FRONTIERA: temp parte solo col nodo iniziale
            temp = {start_id} 
            
            distances = {node_id: float('inf') for node_id in self.network.nodes}
            distances[start_id] = 0
            
            predecessors_edge = {node_id: None for node_id in self.network.nodes}
            
            # 2. CICLO PRINCIPALE: Finché c'è frontiera da esplorare
            while temp:
                
                # SELEZIONE DEL NODO MINIMO NELLA FRONTIERA (temp)
                current_f = float('inf')
                u = None
                
                for nodo in temp:
                    f_score = distances[nodo] + heuristic_func(nodo, end_id) 
                    if f_score < current_f:
                        current_f = f_score
                        u = nodo
                        
                if u is None:
                    break
                    
                if u == end_id:
                    break
                    
                # Rimuoviamo dalla frontiera e spostiamo nei permanenti
                temp.remove(u)
                perm.add(u)
                
                # RILASSAMENTO E AGGIORNAMENTO FRONTIERA
                for edge in self.network.adj_list[u]:
                    v = edge.tail.get_id()
                    
                    # Ignoriamo i nodi già consolidati nei permanenti
                    if v not in perm:
                        new_cost = distances[u] + edge.weight 
                        
                        if distances[v] > new_cost:
                            distances[v] = new_cost          
                            predecessors_edge[v] = edge      
                            
                            # Aggiungiamo alla frontiera se non c'era già
                            temp.add(v)

            # 3. RICOSTRUZIONE DEL PERCORSO
            return self.reconstruct_path(start_id, end_id, distances, predecessors_edge)
    def a_star_opt(self, start_id, end_id,heuristic_func):
            nodes = self.network.nodes
            end_node = nodes[end_id]
        


            # 1. INIZIALIZZAZIONE
            perm = set() 
            temp = {start_id} 
            
            distances = {node_id: float('inf') for node_id in self.network.nodes}
            distances[start_id] = 0
            
            # NUOVO: DIZIONARIO PER CACHARE GLI F-SCORE 
            f_scores = {node_id: float('inf') for node_id in self.network.nodes}
            f_scores[start_id] = heuristic_func(start_id, end_id) 
            
            predecessors_edge = {node_id: None for node_id in self.network.nodes}
            
            # 2. CICLO PRINCIPALE
            while temp:
                
                current_f = float('inf')
                u = None
                
                # RICERCA DEL MINIMO 
                for nodo in temp:
                    if f_scores[nodo] < current_f:
                        current_f = f_scores[nodo]
                        u = nodo
                        
                if u is None:
                    break
                    
                if u == end_id:
                    break
                    
                temp.remove(u)
                perm.add(u)
                
                # RILASSAMENTO 
                for edge in self.network.adj_list[u]:
                    v = edge.tail.get_id()
                    
                    if v not in perm:
                        new_cost = distances[u] + edge.weight 
                        
                        if distances[v] > new_cost:
                            distances[v] = new_cost          
                            predecessors_edge[v] = edge      
                            
                            # NUOVO: Calcoliamo l'euristica SOLO quando troviamo un percorso migliore
                            f_scores[v] = new_cost + heuristic_func(v, end_id) 
                            
                            temp.add(v)

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