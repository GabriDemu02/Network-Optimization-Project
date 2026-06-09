import osmnx as ox
import math
import time
import matplotlib.pyplot as plt
from NetworkSolver_temp import Network, Node, Edge, NetworkSolver

def nearest_node(network, target_x, target_y):
    """
    Trova l'ID del nodo della rete più vicino a una data coppia di coordinate.
    x = Longitudine, y = Latitudine.
    """
    nearest_node = None
    distanza_minima = float('inf')

    for node_id, node in network.nodes.items():
        distanza = math.hypot(node.x - target_x, node.y - target_y)
        if distanza < distanza_minima:
            distanza_minima = distanza
            nearest_node = node_id

    return nearest_node

if __name__ == '__main__':

    # 1. CARICAMENTO DATI
    print("Caricamento del grafo in corso...")
    G = ox.load_graphml(filepath="cagliari.graphml") 

    stats = ox.basic_stats(G)
    print(f"Nodi (n): {stats['n']} | Archi (m): {stats['m']}")
    # STAMPA DEL GRAFO SENZA PERCORSI
    print("\nVisualizzazione del grafo completo (senza percorsi)...")
    

    
    # Mostra il grafico
    plt.show()
    # 2. CREAZIONE ISTANZA DI RETE
    cagliari_net = Network()

    for node_id, data in G.nodes(data=True):
        nuovo_nodo = Node(id=node_id, x=data['x'], y=data['y'])
        cagliari_net.add_node(nuovo_nodo)
        
    edge_counter = 0
    for u, v, data in G.edges(data=True):
        edge_counter += 1
        nodo_partenza = cagliari_net.nodes[u]
        nodo_arrivo = cagliari_net.nodes[v]
        
        lunghezza_grezza = data.get('length', 1.0)
        nome_via = data.get('name', 'Sconosciuta')
        if isinstance(nome_via, list):
            nome_via = nome_via[0]
            
        nuovo_arco = Edge(
            edge_id=f"E{edge_counter}", 
            head=nodo_partenza, 
            tail=nodo_arrivo, 
            length=lunghezza_grezza, 
            name=nome_via
        )
        cagliari_net.add_edge(nuovo_arco)

    print("\nVisualizzazione della mappa base (senza percorsi)")
    
    fig, ax = ox.plot_graph(
        G,                     
        node_size=3,
        node_color='green',           # Nasconde i nodi, esattamente come nei percorsi
        bgcolor='white',       # Sfondo nero coerente
        edge_color='black',        # Archi bianchi (il default di OSMnx su sfondo nero)
        edge_linewidth=0.5,    # Spessore leggero per non impastare la visuale
        show=False,
        close=False
    )
    
    # Aggiungiamo il titolo con lo stesso stile (usiamo il bianco perché lo sfondo è nero)
    ax.set_title("Rete Stradale di Cagliari", fontsize=16, color='black', fontweight='bold', pad=15)

    # Titolo della finestra di sistema
    fig.canvas.manager.set_window_title("Mappa - Base (Nessun Percorso)")

    plt.show()

    # 3. SETUP DEL SOLVER
    solver = NetworkSolver(instance_name="Routing_Cagliari", network=cagliari_net)
    y_partenza, x_partenza = 39.229680, 9.112611



    y_arrivo, x_arrivo = 39.214811, 9.109814



    print("=== COORDINATE INPOSTATE ===")
    print(f"Partenza : Latitudine (y) = {y_partenza} | Longitudine (x) = {x_partenza}")
    print(f"Arrivo   : Latitudine (y) = {y_arrivo} | Longitudine (x) = {x_arrivo}")
 


    
    print("\nRicerca dei punti di accesso stradali più vicini")
    partenza = nearest_node(cagliari_net, target_x=x_partenza, target_y=y_partenza)
    arrivo = nearest_node(cagliari_net, target_x=x_arrivo, target_y=y_arrivo)
    print()
    print(f"Nodo di partenza: {partenza}")
    print(f"Nodo di arrivo: {arrivo}")
  
    
   # 4. BENCHMARK DEGLI ALGORITMI
    algoritmi = {
        "Dijkstra": solver.dijkstra,
        "Dial's Algorithm": solver.dial_dijkstra,
        "A* (Euclidea)": lambda start_id, end_id: solver.a_star(start_id, end_id, solver.heuristic_euclidean),
        "A* (Manhattan)": lambda start_id, end_id: solver.a_star(start_id, end_id, solver.heuristic_manhattan),
        "A* (Chebyshev)": lambda start_id, end_id: solver.a_star(start_id, end_id, solver.heuristic_chebyshev),
        "A* (Euclidea) con caching": lambda start_id, end_id: solver.a_star_opt(start_id, end_id, solver.heuristic_euclidean),
        "A* (Manhattan) con caching": lambda start_id, end_id: solver.a_star_opt(start_id, end_id, solver.heuristic_manhattan),
        "A* (Chebyshev) con caching": lambda start_id, end_id: solver.a_star_opt(start_id, end_id, solver.heuristic_chebyshev),
    }
 

    
    risultati = {}

    # Esegue ogni algoritmo uno dopo l'altro
    for nome, funzione in algoritmi.items():
        start_time = time.perf_counter()
        percorso, costo = funzione(start_id=partenza, end_id=arrivo)
        end_time = time.perf_counter()
        
        tempo_ms = (end_time - start_time) * 1000
        
        if percorso:
            incroci = len(percorso) + 1
            
            # Ricaviamo i nodi specifici per QUESTO algoritmo
            percorso_nodi = [partenza]
            for arco in percorso:
                percorso_nodi.append(arco.tail.get_id())
                
            # Salviamo tutto nel dizionario
            risultati[nome] = {
                "costo": costo, 
                "incroci": incroci, 
                "tempo_ms": tempo_ms,
                "nodi_mappa": percorso_nodi
            }
        else:
            risultati[nome] = {
                "costo": float('inf'), 
                "incroci": 0, 
                "tempo_ms": tempo_ms,
                "nodi_mappa": None
            }

    # 5. STAMPA DELLA TABELLA DI CONFRONTO
    print("\n" + "="*80)
    print(" " * 20 + "RISULTATI BENCHMARK")
    print("="*0)
    for nome, dati in risultati.items():
        if dati['costo'] != float('inf'):
            print(f"{nome.ljust(30)} | Tempo: {dati['tempo_ms']:>8.2f} ms | Costo: {dati['costo']:.2f} m")
        else:
            print(f"{nome.ljust(30)} | PERCORSO NON TROVATO")
    print("="*100)

# 6. PLOT DEI GRAFICI PER OGNI ALGORITMO
    print("\nVisualizzazione delle mappe in sequenza...")
    
    for nome, dati in risultati.items():
        if dati['nodi_mappa']:
            print(f"Mappa per: {nome}")
       
            fig, ax = ox.plot_graph_route(
                G,                     
                dati['nodi_mappa'],         
                route_color='blue',     
                route_linewidth=4,     
                node_size=3,
                node_color='green', 
                edge_color='black',       
                bgcolor='white',
                show=False,
                close=False
            )
            
            # Aggiungiamo il titolo in alto dentro l'immagine
            ax.set_title(nome, fontsize=16, color='black', fontweight='bold', pad=15)

            fig.canvas.manager.set_window_title(f"Mappa - {nome}")

            plt.show()
            
            break
        else:
            print(f" -> Nessun percorso da mostrare per {nome}.")