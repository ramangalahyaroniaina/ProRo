import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import networkx as nx
import heapq
import json
import time
import string
from collections import deque

# -------- INTERFACE --------
root = tk.Tk()
root.title("Dijkstra Ultimate 🔥")

# Frame principal pour organiser l'interface
main_frame = tk.Frame(root)
main_frame.pack()

canvas = tk.Canvas(main_frame, width=600, height=400, bg="white")
canvas.pack(side=tk.LEFT, padx=5, pady=5)

# Frame pour les contrôles
control_frame = tk.Frame(main_frame)
control_frame.pack(side=tk.RIGHT, padx=5, pady=5)

G = nx.Graph()
positions = {}
node_count = 0


# -------- GENERER LETTRES --------
def generer_nom_sommet(index):
    letters = string.ascii_uppercase
    return letters[index % 26]


# -------- AJOUT SOMMET --------
def ajouter_sommet(event):
    global node_count

    x, y = event.x, event.y

    node = generer_nom_sommet(node_count)

    G.add_node(node)
    positions[node] = (x, y)

    node_count += 1
    dessiner()
    mettre_a_jour_info()


# -------- AJOUT ARETE --------
selected = []


def selectionner_sommet(event):
    global selected

    for node, (x, y) in positions.items():
        if abs(x - event.x) < 20 and abs(y - event.y) < 20:

            if node not in selected:
                selected.append(node)

            if len(selected) == 2:
                poids = simpledialog.askinteger("Poids", "Entrer le poids", minvalue=1)

                if poids is not None:
                    G.add_edge(selected[0], selected[1], weight=poids)

                selected.clear()
                dessiner()
                mettre_a_jour_info()
            break


# -------- DESSIN --------
def dessiner(couleurs=None, chemin=None):
    canvas.delete("all")

    # Dessiner les arêtes
    for u, v in G.edges():
        x1, y1 = positions[u]
        x2, y2 = positions[v]

        color = "black"
        if chemin is not None and ((u, v) in chemin or (v, u) in chemin):
            color = "green"

        canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

        poids = G[u][v]['weight']
        canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(poids),
                           fill="blue", font=("Arial", 10, "bold"))

    # Dessiner les sommets
    for node, (x, y) in positions.items():
        color = "lightblue"
        if couleurs:
            color = couleurs.get(node, "lightblue")

        canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill=color, outline="black", width=2)
        canvas.create_text(x, y, text=node, font=("Arial", 12, "bold"))


# -------- TABLEAU --------
def afficher_tableau_matrice(historiques):
    table.delete("1.0", tk.END)

    nodes = sorted(list(G.nodes()))

    header = "Etape\t" + "\t".join(nodes) + "\n"
    table.insert(tk.END, header)
    table.insert(tk.END, "-" * 80 + "\n")

    for i, etat in enumerate(historiques):
        ligne = f"{i}\t"

        for node in nodes:
            dist, pred = etat[node]

            if dist == float('inf'):
                ligne += "∞\t"
            elif dist == float('-inf'):
                ligne += "-∞\t"
            else:
                pred_str = "-" if pred is None else str(pred)
                ligne += f"{dist}({pred_str})\t"

        ligne += "\n"
        table.insert(tk.END, ligne)
        table.see(tk.END)

    table.update()


# -------- ALGORITHME POUR CHEMIN MINIMUM (DIJKSTRA) --------
def chemin_minimum(source, dest):
    """Algorithme de Dijkstra pour le chemin minimum"""
    distances = {n: float('inf') for n in G.nodes()}
    parents = {n: None for n in G.nodes()}
    distances[source] = 0

    pq = [(0, source)]
    historiques = []

    while pq:
        dist, node = heapq.heappop(pq)

        if dist > distances[node]:
            continue

        # Enregistrer l'état
        etat = {n: (distances[n], parents[n]) for n in G.nodes()}
        historiques.append(etat)

        # Animation
        couleurs = {node: "red"}
        dessiner(couleurs)
        root.update()
        time.sleep(0.3)

        for voisin in G.neighbors(node):
            poids = G[node][voisin]['weight']
            new_dist = dist + poids

            if new_dist < distances[voisin]:
                distances[voisin] = new_dist
                parents[voisin] = node
                heapq.heappush(pq, (new_dist, voisin))

        couleurs[node] = "gray"
        dessiner(couleurs)
        root.update()

    return distances, parents, historiques


# -------- ALGORITHME POUR CHEMIN MAXIMUM (DFS AVEC MÉMOISATION) --------
def chemin_maximum_dfs(source, dest):
    """Recherche du plus long chemin par DFS avec mémoisation"""

    # Vérifier si dest est accessible depuis source
    if not peut_atteindre(source, dest):
        return None, None, None

    # Mémoisation des résultats
    memo = {}

    def dfs(u, visited):
        """Parcourt le graphe pour trouver le plus long chemin vers dest"""
        if u == dest:
            return (0, [dest])

        # Créer une clé de mémoisation
        visited_key = frozenset(visited)
        if (u, visited_key) in memo:
            return memo[(u, visited_key)]

        max_dist = float('-inf')
        max_path = []

        for voisin in G.neighbors(u):
            if voisin not in visited:
                poids = G[u][voisin]['weight']
                dist, path = dfs(voisin, visited | {voisin})

                if dist != float('-inf'):
                    total_dist = poids + dist
                    if total_dist > max_dist:
                        max_dist = total_dist
                        max_path = [u] + path

        memo[(u, visited_key)] = (max_dist, max_path)
        return max_dist, max_path

    # Lancer la recherche
    max_dist, max_path = dfs(source, {source})

    if max_dist == float('-inf') or not max_path:
        return None, None, None

    # Construire les structures de données pour l'affichage
    distances = {n: float('-inf') for n in G.nodes()}
    parents = {n: None for n in G.nodes()}

    # Reconstruire les distances et parents
    cumulative_dist = 0
    for i in range(len(max_path) - 1):
        current = max_path[i]
        next_node = max_path[i + 1]
        cumulative_dist += G[current][next_node]['weight']
        distances[next_node] = cumulative_dist
        parents[next_node] = current

    distances[source] = 0

    # Créer un historique pour l'affichage
    historiques = []
    for i in range(len(max_path)):
        etat = {n: (distances[n], parents[n]) for n in G.nodes()}
        historiques.append(etat)

        # Animation
        couleurs = {node: "lightgray" for node in G.nodes()}
        for j in range(i + 1):
            couleurs[max_path[j]] = "lightgreen"

        if i < len(max_path) - 1:
            edges = [(max_path[i], max_path[i + 1])]
            dessiner(couleurs, edges)
        else:
            dessiner(couleurs)

        root.update()
        time.sleep(0.5)

    return distances, parents, historiques


def peut_atteindre(source, dest):
    """Vérifie s'il existe un chemin de source vers dest"""
    if source == dest:
        return True

    visite = set()
    queue = deque([source])

    while queue:
        node = queue.popleft()
        if node == dest:
            return True

        if node not in visite:
            visite.add(node)
            for voisin in G.neighbors(node):
                if voisin not in visite:
                    queue.append(voisin)

    return False


# -------- RECONSTRUCTION DU CHEMIN --------
def reconstruire(parents, dest):
    if parents is None:
        return []

    chemin = []
    current = dest
    iterations = 0
    max_iterations = len(G.nodes()) + 1

    while current is not None and iterations < max_iterations:
        chemin.append(current)
        current = parents.get(current)
        iterations += 1

    if iterations >= max_iterations:
        return [dest]

    return chemin[::-1]


# -------- LANCEMENT AVEC MODE SÉLECTIONNÉ --------
def lancer_min():
    lancer_avec_mode("min")


def lancer_max():
    lancer_avec_mode("max")


def lancer_avec_mode(mode):
    try:
        if len(G.nodes()) == 0:
            messagebox.showerror("Erreur", "Aucun sommet dans le graphe")
            return

        # Demander les sommets source et destination
        source = simpledialog.askstring("Source", "Sommet de départ (ex: A)")
        if not source:
            return

        dest = simpledialog.askstring("Destination", "Sommet d'arrivée (ex: C)")
        if not dest:
            return

        if source not in G.nodes():
            messagebox.showerror("Erreur", f"Le sommet {source} n'existe pas")
            return

        if dest not in G.nodes():
            messagebox.showerror("Erreur", f"Le sommet {dest} n'existe pas")
            return

        # Exécuter l'algorithme approprié
        if mode == "min":
            distances, parents, historiques = chemin_minimum(source, dest)
        else:
            # Utiliser DFS avec mémoisation pour le chemin maximum
            result = chemin_maximum_dfs(source, dest)
            if result[0] is None:
                messagebox.showinfo("Résultat", "Aucun chemin trouvé entre les sommets")
                return
            distances, parents, historiques = result

        if distances is None:
            return

        # Afficher le tableau des étapes
        if historiques:
            afficher_tableau_matrice(historiques)

        # Vérifier si un chemin a été trouvé
        if distances.get(dest, float('-inf')) in [float('inf'), float('-inf')]:
            messagebox.showinfo("Résultat", "Aucun chemin trouvé")
            return

        # Reconstruire et afficher le chemin
        chemin = reconstruire(parents, dest)

        if len(chemin) > 1:
            edges_path = [(chemin[i], chemin[i + 1]) for i in range(len(chemin) - 1)]
            dessiner(chemin=edges_path)
        else:
            dessiner()

        # Afficher le résultat
        message_text = f"Mode: {'Minimum' if mode == 'min' else 'Maximum'}\n"
        message_text += f"Distance totale: {distances[dest]}\n"
        message_text += f"Chemin: {' -> '.join(chemin)}"

        messagebox.showinfo("Résultat", message_text)

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")


# -------- SAUVEGARDE --------
def sauvegarder():
    if len(G.nodes()) == 0:
        messagebox.showwarning("Attention", "Rien à sauvegarder")
        return

    data = {
        "nodes": list(G.nodes()),
        "edges": [(u, v, G[u][v]['weight']) for u, v in G.edges()],
        "positions": positions
    }

    file = filedialog.asksaveasfilename(defaultextension=".json")
    if file:
        try:
            with open(file, "w") as f:
                json.dump(data, f)
            messagebox.showinfo("Succès", "Graphe sauvegardé avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")


# -------- CHARGER --------
def charger():
    global G, positions, node_count

    file = filedialog.askopenfilename()
    if file:
        try:
            with open(file, "r") as f:
                data = json.load(f)

            G = nx.Graph()
            positions = {k: tuple(v) for k, v in data["positions"].items()}

            for n in data["nodes"]:
                G.add_node(n)

            for u, v, w in data["edges"]:
                G.add_edge(u, v, weight=w)

            node_count = len(G.nodes())
            dessiner()
            mettre_a_jour_info()
            messagebox.showinfo("Succès", "Graphe chargé avec succès")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement : {e}")


# -------- EFFACER TOUT --------
def effacer_tout():
    global G, positions, node_count, selected

    if messagebox.askyesno("Confirmation", "Voulez-vous vraiment effacer tout le graphe ?"):
        G = nx.Graph()
        positions = {}
        node_count = 0
        selected = []
        dessiner()
        table.delete("1.0", tk.END)
        mettre_a_jour_info()


# -------- METTRE À JOUR LES INFOS --------
def mettre_a_jour_info():
    info_label.config(text=f"Sommets: {G.number_of_nodes()}\nArêtes: {G.number_of_edges()}")


# -------- INTERFACE DES BOUTONS --------
# Titre
title_label = tk.Label(control_frame, text="Contrôles", font=("Arial", 14, "bold"))
title_label.pack(pady=5)

# Boutons pour choisir le mode
mode_frame = tk.LabelFrame(control_frame, text="Mode de calcul", padx=10, pady=5)
mode_frame.pack(pady=5, fill="x")

tk.Button(mode_frame, text="Chemin MINIMUM", command=lancer_min,
          bg="lightgreen", font=("Arial", 10, "bold"), width=15).pack(pady=2)
tk.Button(mode_frame, text="Chemin MAXIMUM", command=lancer_max,
          bg="lightcoral", font=("Arial", 10, "bold"), width=15).pack(pady=2)

# Boutons d'action
action_frame = tk.LabelFrame(control_frame, text="Actions", padx=10, pady=5)
action_frame.pack(pady=5, fill="x")

tk.Button(action_frame, text="💾 Sauvegarder", command=sauvegarder,
          bg="lightblue", width=15).pack(pady=2)
tk.Button(action_frame, text="📂 Charger", command=charger,
          bg="lightyellow", width=15).pack(pady=2)
tk.Button(action_frame, text="🗑️ Effacer tout", command=effacer_tout,
          bg="orange", width=15).pack(pady=2)
tk.Button(action_frame, text="❌ Quitter", command=root.quit,
          bg="lightcoral", width=15).pack(pady=2)

# Informations
info_frame = tk.LabelFrame(control_frame, text="Informations", padx=10, pady=5)
info_frame.pack(pady=5, fill="x")

info_label = tk.Label(info_frame, text="Sommets: 0\nArêtes: 0",
                      font=("Arial", 9), justify=tk.LEFT)
info_label.pack()

# Table des résultats
table_frame = tk.Frame(root)
table_frame.pack(pady=5)

table_label = tk.Label(table_frame, text="Tableau des distances", font=("Arial", 10, "bold"))
table_label.pack()

table = tk.Text(table_frame, height=12, width=80, font=("Courier", 9))
table.pack()

scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=table.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
table.configure(yscrollcommand=scrollbar.set)

# Message d'aide
aide_label = tk.Label(root,
                      text="Clic gauche : Ajouter sommet | Clic droit : Sélectionner sommet pour créer une arête\n"
                           "Pour le mode MAXIMUM : recherche exhaustive du plus long chemin ",
                      fg="gray", font=("Arial", 8), justify=tk.LEFT)
aide_label.pack(pady=5)

# -------- BIND --------
canvas.bind("<Button-1>", ajouter_sommet)
canvas.bind("<Button-3>", selectionner_sommet)

root.mainloop()