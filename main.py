import heapq
import string
import time
import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from tkinter import simpledialog, messagebox
from typing import Dict, Tuple, List, Optional, Set

import networkx as nx


# -------- CONSTANTES ET TYPES --------
class AlgorithmMode(Enum):
    MIN = "min"
    MAX = "max"


class DrawState:
    """État du dessin pour l'animation"""

    def __init__(self):
        self.node_colors: Dict[str, str] = {}
        self.edge_colors: Dict[Tuple[str, str], str] = {}
        self.highlighted_path: List[Tuple[str, str]] = []
        self.current_node: Optional[str] = None


@dataclass
class AlgorithmStep:
    """Représente une étape de l'algorithme"""
    distances: Dict[str, float]
    parents: Dict[str, Optional[str]]
    current_node: Optional[str] = None
    visited_nodes: Set[str] = None

    def __post_init__(self):
        if self.visited_nodes is None:
            self.visited_nodes = set()


# -------- CLASSE PRINCIPALE --------
class DijkstraApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Dijkstra Ultimate 🔥 - Visualisation d'algorithmes")
        self.root.configure(bg="#f0f2f5")
        self.root.geometry("1200x700")

        # Données du graphe
        self.G = nx.Graph()
        self.positions: Dict[str, Tuple[int, int]] = {}
        self.node_count = 0
        self.selected_nodes: List[str] = []

        # Animation
        self.animation_speed = 0.5
        self.animation_cancelled = False

        # Interface
        self.setup_ui()

        # Événements
        self.setup_events()

        # Variables temporaires
        self.temp_edge: Optional[Tuple[int, int, int, int]] = None

    # -------- CONFIGURATION UI --------
    def setup_ui(self):
        """Configure toute l'interface utilisateur"""
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg="#f0f2f5")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas pour le dessin
        self.canvas_frame = tk.Frame(self.main_frame, bg="white", relief=tk.RAISED, bd=2)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Scrollbars pour le canvas
        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Panel de contrôle
        self.control_frame = tk.Frame(self.main_frame, bg="#f0f2f5", width=250)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)
        self.control_frame.pack_propagate(False)

        # Titre
        tk.Label(self.control_frame, text="Contrôles", font=("Arial", 16, "bold"),
                 bg="#f0f2f5", fg="#333").pack(pady=10)

        # Vitesse d'animation
        self.setup_speed_control()

        tk.Frame(self.control_frame, height=10, bg="#f0f2f5").pack()

        # Boutons d'action
        self.setup_action_buttons()

        tk.Frame(self.control_frame, height=10, bg="#f0f2f5").pack()

        # Informations
        self.setup_info_panel()

        # Tableau des résultats
        self.setup_table()

    def setup_speed_control(self):
        """Configure le contrôle de vitesse"""
        speed_frame = tk.LabelFrame(self.control_frame, text="Animation", bg="#f0f2f5", padx=5, pady=5)
        speed_frame.pack(fill=tk.X, pady=5)

        tk.Label(speed_frame, text="Vitesse:", bg="#f0f2f5").pack()
        self.speed_scale = tk.Scale(speed_frame, from_=0.1, to=2.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, command=self.change_speed)
        self.speed_scale.set(0.5)
        self.speed_scale.pack(fill=tk.X)

        self.speed_label = tk.Label(speed_frame, text="0.5x", bg="#f0f2f5")
        self.speed_label.pack()

    def setup_action_buttons(self):
        """Configure les boutons d'action"""
        actions_frame = tk.LabelFrame(self.control_frame, text="Actions", bg="#f0f2f5", padx=5, pady=5)
        actions_frame.pack(fill=tk.X, pady=5)

        buttons = [
            ("🚀 CHEMIN MIN", "#4CAF50", lambda: self.run_algorithm(AlgorithmMode.MIN)),
            ("⚡ CHEMIN MAX", "#F44336", lambda: self.run_algorithm(AlgorithmMode.MAX)),
            ("🗑️ Supprimer sommet", "#FF9800", self.delete_node),
            ("🧹 Tout effacer", "#9E9E9E", self.clear_all),
            ("❌ Annuler animation", "#607D8B", self.cancel_animation)
        ]

        for text, color, command in buttons:
            btn = tk.Button(actions_frame, text=text, bg=color, fg="white",
                            font=("Arial", 10, "bold"), command=command)
            btn.pack(fill=tk.X, pady=2)

    def setup_info_panel(self):
        """Configure le panneau d'information"""
        info_frame = tk.LabelFrame(self.control_frame, text="Informations", bg="#f0f2f5", padx=5, pady=5)
        info_frame.pack(fill=tk.X, pady=5)

        self.info_label = tk.Label(info_frame, text="Sommets: 0\nArêtes: 0\nSélection: -",
                                   bg="#f0f2f5", font=("Arial", 10))
        self.info_label.pack()

        self.status_label = tk.Label(self.control_frame, text="✅ Prêt",
                                     bg="#f0f2f5", fg="green", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=5)

    def setup_table(self):
        """Configure le tableau des résultats"""
        table_frame = tk.LabelFrame(self.root, text="Historique des étapes", bg="#f0f2f5", padx=5, pady=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame pour le tableau avec scrollbar
        table_container = tk.Frame(table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)

        self.table = tk.Text(table_container, height=12, font=("Courier", 9))
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        table_scrollbar = tk.Scrollbar(table_container, command=self.table.yview)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscrollcommand=table_scrollbar.set)

    def setup_events(self):
        """Configure les événements"""
        self.canvas.bind("<Button-1>", self.add_node)
        self.canvas.bind("<Button-3>", self.select_node)
        self.canvas.bind("<B1-Motion>", self.drag_node)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Control-Button-1>", self.edit_edge_weight)

        # Raccourcis clavier
        self.root.bind("<Delete>", lambda e: self.delete_node())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Escape>", lambda e: self.cancel_selection())

    # -------- GESTION DU CANVAS --------
    def draw(self, state: Optional[DrawState] = None):
        """Dessine le graphe avec l'état actuel"""
        self.canvas.delete("all")

        # Ajuster la zone de dessin
        if self.positions:
            all_x = [p[0] for p in self.positions.values()]
            all_y = [p[1] for p in self.positions.values()]
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)

            margin = 50
            self.canvas.configure(scrollregion=(min_x - margin, min_y - margin,
                                                max_x + margin, max_y + margin))

        # Dessiner les arêtes
        for u, v in self.G.edges():
            if u in self.positions and v in self.positions:
                x1, y1 = self.positions[u]
                x2, y2 = self.positions[v]

                # Couleur de l'arête
                color = "black"
                if state and state.highlighted_path:
                    if (u, v) in state.highlighted_path or (v, u) in state.highlighted_path:
                        color = "#FFD700"  # Or pour le chemin final
                    elif state.edge_colors.get((u, v)) == "red":
                        color = "red"

                width = 3 if color == "#FFD700" else 2
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

                # Poids de l'arête
                poids = self.G[u][v].get("weight", "?")
                mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
                self.canvas.create_oval(mid_x - 10, mid_y - 10, mid_x + 10, mid_y + 10,
                                        fill="white", outline="blue")
                self.canvas.create_text(mid_x, mid_y, text=str(poids), fill="blue", font=("Arial", 9, "bold"))

        # Dessiner les sommets
        for node, (x, y) in self.positions.items():
            # Couleur du sommet
            color = "lightblue"
            if state and state.node_colors:
                color = state.node_colors.get(node, "lightblue")

            # Bordure pour la sélection
            outline = "red" if node in self.selected_nodes else "black"
            width = 3 if node in self.selected_nodes else 1

            self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18,
                                    fill=color, outline=outline, width=width)
            self.canvas.create_text(x, y, text=node, font=("Arial", 12, "bold"))

        # Dessiner l'arête temporaire
        if self.temp_edge:
            self.canvas.create_line(self.temp_edge[0], self.temp_edge[1],
                                    self.temp_edge[2], self.temp_edge[3],
                                    fill="gray", width=2, dash=(5, 5))

        self.root.update()

    def update_info(self):
        """Met à jour les informations affichées"""
        selection_text = ", ".join(self.selected_nodes) if self.selected_nodes else "-"
        self.info_label.config(text=f"Sommets: {self.G.number_of_nodes()}\n"
                                    f"Arêtes: {self.G.number_of_edges()}\n"
                                    f"Sélection: {selection_text}")

    # -------- GESTION DES SOMMETS --------
    def get_node_name(self, index: int) -> str:
        """Génère un nom pour un nouveau sommet"""
        if index < 26:
            return string.ascii_uppercase[index]
        else:
            return f"{string.ascii_uppercase[index // 26 - 1]}{string.ascii_uppercase[index % 26]}"

    def add_node(self, event: tk.Event):
        """Ajoute un sommet au clic"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        node_name = self.get_node_name(self.node_count)

        self.G.add_node(node_name)
        self.positions[node_name] = (x, y)
        self.node_count += 1

        self.draw()
        self.update_info()
        self.set_status(f"✅ Sommet {node_name} ajouté", "green")

    def delete_node(self):
        """Supprime un sommet"""
        if not self.G.nodes():
            messagebox.showwarning("Attention", "Aucun sommet à supprimer")
            return

        nodes_list = sorted(self.G.nodes())
        node = simpledialog.askstring("Supprimer sommet",
                                      f"Nom du sommet à supprimer\nSommets existants: {', '.join(nodes_list)}")

        if not node:
            return

        node = node.strip().upper()

        if node not in self.G.nodes():
            messagebox.showerror("Erreur", f"Le sommet {node} n'existe pas")
            return

        # Confirmation
        if messagebox.askyesno("Confirmation", f"Supprimer le sommet {node} et toutes ses arêtes ?"):
            self.G.remove_node(node)
            if node in self.positions:
                del self.positions[node]
            if node in self.selected_nodes:
                self.selected_nodes.remove(node)

            self.draw()
            self.update_info()
            self.set_status(f"✅ Sommet {node} supprimé", "green")

    def clear_all(self):
        """Efface tout le graphe"""
        if messagebox.askyesno("Confirmation", "Effacer tout le graphe ?\nToutes les données seront perdues."):
            self.G.clear()
            self.positions.clear()
            self.selected_nodes.clear()
            self.node_count = 0
            self.draw()
            self.update_info()
            self.set_status("✅ Tout a été effacé", "green")

    # -------- GESTION DES ARÊTES --------
    def select_node(self, event: tk.Event):
        """Sélectionne un sommet pour créer une arête"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        for node, (nx, ny) in self.positions.items():
            if abs(nx - x) < 20 and abs(ny - y) < 20:
                if node not in self.selected_nodes:
                    self.selected_nodes.append(node)
                    self.set_status(f"📍 Sommet {node} sélectionné", "blue")

                if len(self.selected_nodes) == 2:
                    self.create_edge()
                else:
                    self.draw()
                    self.update_info()
                break

    def create_edge(self):
        """Crée une arête entre deux sommets sélectionnés"""
        u, v = self.selected_nodes[0], self.selected_nodes[1]

        if u == v:
            messagebox.showerror("Erreur", "Impossible de créer une boucle")
            self.selected_nodes.clear()
            self.draw()
            self.update_info()
            return

        # Vérifier si l'arête existe déjà
        if self.G.has_edge(u, v):
            reponse = messagebox.askyesno("Arête existante",
                                          f"Une arête existe déjà entre {u} et {v}.\nVoulez-vous modifier son poids ?")
            if reponse:
                self.modify_edge_weight(u, v)
            self.selected_nodes.clear()
            self.draw()
            self.update_info()
            return

        # Demander le poids
        poids = simpledialog.askinteger("Poids de l'arête",
                                        f"Entrez le poids pour l'arête {u}-{v}",
                                        minvalue=1, maxvalue=999)

        if poids:
            self.G.add_edge(u, v, weight=poids)
            self.set_status(f"✅ Arête {u}-{v} créée (poids={poids})", "green")

        self.selected_nodes.clear()
        self.draw()
        self.update_info()

    def modify_edge_weight(self, u: str, v: str):
        """Modifie le poids d'une arête existante"""
        current_weight = self.G[u][v]["weight"]
        new_weight = simpledialog.askinteger("Modifier le poids",
                                             f"Poids actuel: {current_weight}\nNouveau poids:",
                                             minvalue=1, maxvalue=999)

        if new_weight:
            self.G[u][v]["weight"] = new_weight
            self.set_status(f"✅ Poids modifié: {u}-{v} = {new_weight}", "green")
            self.draw()

    def edit_edge_weight(self, event: tk.Event):
        """Édite le poids d'une arête par double-clic"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        # Trouver l'arête la plus proche
        min_dist = 20
        closest_edge = None

        for u, v in self.G.edges():
            if u in self.positions and v in self.positions:
                x1, y1 = self.positions[u]
                x2, y2 = self.positions[v]

                # Distance du point à la ligne
                import math
                d = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / math.hypot(y2 - y1, x2 - x1)

                if d < min_dist:
                    min_dist = d
                    closest_edge = (u, v)

        if closest_edge:
            self.modify_edge_weight(closest_edge[0], closest_edge[1])

    # -------- DRAG & DROP --------
    def drag_node(self, event: tk.Event):
        """Déplace un sommet"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        for node, (nx, ny) in self.positions.items():
            if abs(nx - x) < 20 and abs(ny - y) < 20:
                self.dragged_node = node
                self.drag_start_x = nx
                self.drag_start_y = ny
                break

        if hasattr(self, 'dragged_node'):
            self.positions[self.dragged_node] = (x, y)
            self.draw()

    def stop_drag(self, event: tk.Event):
        """Arrête le déplacement"""
        if hasattr(self, 'dragged_node'):
            delattr(self, 'dragged_node')

    def zoom(self, event: tk.Event):
        """Zoom sur le canvas"""
        scale = 1.1 if event.delta > 0 else 0.9
        self.canvas.scale("all", self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), scale, scale)

    # -------- ALGORITHMES --------
    def run_algorithm(self, mode: AlgorithmMode):
        """Lance un algorithme"""
        if self.G.number_of_nodes() < 2:
            messagebox.showwarning("Attention", "Ajoutez au moins 2 sommets d'abord")
            return

        source, dest = self.get_nodes_from_user()
        if not source or not dest:
            return

        if source not in self.G.nodes():
            messagebox.showerror("Erreur", f"Le sommet {source} n'existe pas")
            return

        if dest not in self.G.nodes():
            messagebox.showerror("Erreur", f"Le sommet {dest} n'existe pas")
            return

        self.animation_cancelled = False

        if mode == AlgorithmMode.MIN:
            self.dijkstra(source, dest)
        else:
            self.max_path_dfs(source, dest)

    def get_nodes_from_user(self) -> Tuple[Optional[str], Optional[str]]:
        """Demande à l'utilisateur de choisir deux sommets"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Choisir les sommets")
        dialog.geometry("300x200")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Sélectionnez les sommets", font=("Arial", 12, "bold")).pack(pady=10)

        nodes = sorted(self.G.nodes())
        node_list_str = ", ".join(nodes)
        tk.Label(dialog, text=f"Sommets disponibles:\n{node_list_str}", font=("Arial", 9)).pack(pady=5)

        tk.Label(dialog, text="Sommet de départ:").pack()
        source_entry = tk.Entry(dialog)
        source_entry.pack()

        tk.Label(dialog, text="Sommet d'arrivée:").pack()
        dest_entry = tk.Entry(dialog)
        dest_entry.pack()

        result = {"source": None, "dest": None}

        def validate():
            source = source_entry.get().strip().upper()
            dest = dest_entry.get().strip().upper()

            if source and dest:
                result["source"] = source
                result["dest"] = dest
                dialog.destroy()
            else:
                messagebox.showwarning("Attention", "Veuillez remplir les deux champs")

        tk.Button(dialog, text="Valider", command=validate, bg="#4CAF50", fg="white").pack(pady=10)

        self.root.wait_window(dialog)
        return result["source"], result["dest"]

    def dijkstra(self, source: str, dest: str):
        """Algorithme de Dijkstra pour le chemin minimum"""
        self.set_status(f"🚀 Lancement de Dijkstra de {source} à {dest}...", "blue")

        distances = {n: float('inf') for n in self.G.nodes()}
        parents = {n: None for n in self.G.nodes()}
        distances[source] = 0

        pq = [(0, source)]
        steps = []
        visited = set()

        while pq and not self.animation_cancelled:
            dist, node = heapq.heappop(pq)

            if node in visited:
                continue

            if dist > distances[node]:
                continue

            visited.add(node)

            # Enregistrer l'étape
            step = AlgorithmStep(
                distances=distances.copy(),
                parents=parents.copy(),
                current_node=node,
                visited_nodes=visited.copy()
            )
            steps.append(step)

            # Animation
            self.animate_step(step, node)

            if node == dest:
                break

            for voisin in self.G.neighbors(node):
                if voisin not in visited:
                    poids = self.G[node][voisin]["weight"]
                    new_dist = dist + poids

                    if new_dist < distances[voisin]:
                        distances[voisin] = new_dist
                        parents[voisin] = node
                        heapq.heappush(pq, (new_dist, voisin))

        if self.animation_cancelled:
            self.set_status("❌ Animation annulée", "red")
            return

        # Afficher les résultats
        self.display_results(steps, distances, parents, dest)

    def max_path_dfs(self, source: str, dest: str):
        """Recherche du chemin de poids maximum par DFS"""
        self.set_status(f"⚡ Recherche du chemin maximum de {source} à {dest}...", "blue")

        best_path = []
        best_weight = float('-inf')

        def dfs(current: str, visited: Set[str], current_weight: float, path: List[str]):
            nonlocal best_weight, best_path

            if self.animation_cancelled:
                return

            if current == dest:
                if current_weight > best_weight:
                    best_weight = current_weight
                    best_path = path.copy()
                return

            for voisin in self.G.neighbors(current):
                if voisin not in visited:
                    weight = self.G[current][voisin]["weight"]
                    dfs(voisin, visited | {voisin}, current_weight + weight, path + [voisin])

        dfs(source, {source}, 0, [source])

        if self.animation_cancelled:
            self.set_status("❌ Animation annulée", "red")
            return

        if not best_path:
            messagebox.showinfo("Résultat", "Aucun chemin trouvé")
            return

        # Construire les distances et parents
        distances = {n: float('-inf') for n in self.G.nodes()}
        parents = {n: None for n in self.G.nodes()}
        distances[source] = 0

        steps = []
        for i in range(len(best_path) - 1):
            current, nxt = best_path[i], best_path[i + 1]
            weight = self.G[current][nxt]["weight"]
            distances[nxt] = distances[current] + weight
            parents[nxt] = current

            step = AlgorithmStep(
                distances=distances.copy(),
                parents=parents.copy(),
                current_node=nxt,
                visited_nodes=set(best_path[:i + 2])
            )
            steps.append(step)

            # Animation
            state = DrawState()
            state.node_colors = {n: "lightgray" for n in self.G.nodes()}
            for j in range(i + 2):
                state.node_colors[best_path[j]] = "#90EE90"
            state.current_node = nxt
            self.draw(state)
            time.sleep(self.animation_speed)

        self.display_results(steps, distances, parents, dest, best_path)

    def animate_step(self, step: AlgorithmStep, current_node: str):
        """Anime une étape de l'algorithme"""
        state = DrawState()

        # Colorer les sommets
        for node in self.G.nodes():
            if node == current_node:
                state.node_colors[node] = "#FF6B6B"  # Rouge pour le courant
            elif node in step.visited_nodes:
                state.node_colors[node] = "#90EE90"  # Vert pour visité
            else:
                state.node_colors[node] = "#E0E0E0"  # Gris pour non visité

        self.draw(state)
        time.sleep(self.animation_speed)

    def display_results(self, steps: List[AlgorithmStep], distances: Dict[str, float],
                        parents: Dict[str, Optional[str]], dest: str, optimal_path: List[str] = None):
        """Affiche les résultats dans le tableau"""
        # Afficher le tableau
        self.display_table(steps)

        # Reconstruire le chemin
        if not optimal_path:
            path = []
            current = dest
            while current is not None:
                path.append(current)
                current = parents.get(current)
            path.reverse()
        else:
            path = optimal_path

        if len(path) < 2:
            messagebox.showinfo("Résultat", "Aucun chemin trouvé")
            return

        # Mettre en évidence le chemin final
        state = DrawState()
        edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        state.highlighted_path = edges

        # Colorer le chemin
        for i, node in enumerate(path):
            if i == 0:
                state.node_colors[node] = "#4CAF50"  # Vert pour départ
            elif i == len(path) - 1:
                state.node_colors[node] = "#F44336"  # Rouge pour arrivée
            else:
                state.node_colors[node] = "#FFD700"  # Or pour le chemin

        self.draw(state)

        # Afficher le résultat
        distance_value = distances[dest]
        distance_text = f"{distance_value}" if distance_value != float('inf') else "∞"
        if distance_value == float('-inf'):
            distance_text = "-∞"

        messagebox.showinfo("Résultat",
                            f"{'Distance' if distance_value != float('-inf') else 'Poids'} totale: {distance_text}\n"
                            f"Chemin: {' → '.join(path)}")

        self.set_status("✅ Algorithme terminé", "green")

    def display_table(self, steps: List[AlgorithmStep]):
        """Affiche l'historique dans le tableau"""
        self.table.delete("1.0", tk.END)

        if not steps:
            return

        nodes = sorted(self.G.nodes())

        # En-tête
        header = "Étape".ljust(8) + "".join([f"{n:^10}" for n in nodes])
        self.table.insert(tk.END, header + "\n")
        self.table.insert(tk.END, "-" * (8 + 10 * len(nodes)) + "\n")

        # Données
        for i, step in enumerate(steps):
            line = f"{i + 1:<8}"
            for node in nodes:
                dist = step.distances[node]
                parent = step.parents[node]

                if dist == float('inf'):
                    dist_str = "∞"
                elif dist == float('-inf'):
                    dist_str = "-∞"
                else:
                    dist_str = f"{int(dist)}"

                parent_str = f"({parent})" if parent else "(-)"
                line += f"{dist_str}{parent_str:^6}"

            self.table.insert(tk.END, line + "\n")
            self.table.see(tk.END)
            self.root.update()
            time.sleep(self.animation_speed * 0.5)

    # -------- UTILITAIRES --------
    def change_speed(self, val: str):
        """Change la vitesse d'animation"""
        self.animation_speed = float(val)
        self.speed_label.config(text=f"{val}x")

    def cancel_animation(self):
        """Annule l'animation en cours"""
        self.animation_cancelled = True
        self.set_status("⏹️ Animation annulée", "orange")

    def cancel_selection(self):
        """Annule la sélection en cours"""
        self.selected_nodes.clear()
        self.draw()
        self.update_info()
        self.set_status("✅ Sélection annulée", "green")

    def undo(self):
        """Annule la dernière action (non implémenté complètement)"""
        messagebox.showinfo("Info", "Fonctionnalité à venir")

    def set_status(self, message: str, color: str = "black"):
        """Définit le message de statut"""
        self.status_label.config(text=message, fg=color)
        self.root.update()

    def save_graph(self):
        """Sauvegarde le graphe dans un fichier"""
        # À implémenter
        pass

    def load_graph(self):
        """Charge un graphe depuis un fichier"""
        # À implémenter
        pass


# -------- LANCEMENT --------
if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraApp(root)
    root.mainloop()