import tkinter as tk
from tkinter import simpledialog, messagebox
import math


class GraphCanvas(tk.Canvas):
    def __init__(self, parent, graph):
        super().__init__(parent, bg="#1a1b26", highlightthickness=0)

        self.graph = graph
        self.nodes_pos = {}
        self.node_items = {}
        self.node_texts = {}
        self.edge_items = {}
        self.weight_items = {}  # Stocke les IDs des textes de poids
        self.node_count = 0

        # interaction state
        self.selected_node = None
        self.temp_line = None
        self.dragging_node = None

        # animation state
        self.current_path = []

        # Couleurs modernes
        self.colors = {
            "bg": "#2a2f68",
            "node": "#2a2b3c",
            "node_outline": "#7aa2f7",
            "node_selected": "#f7768e",
            "node_start": "#7aa2f7",
            "node_end": "#06cd4f",
            "node_current": "#f7768e",
            "edge": "#565f89",
            "edge_highlight": "#e0af68",
            "text": "#c0caf5",
            "weight_bg": "#1a1b26",
            "weight_border": "#7aa2f7"
        }

        # EVENTS
        self.bind("<Button-1>", self.left_click)
        self.bind("<Button-3>", self.right_click)
        self.bind("<B1-Motion>", self.drag_node)
        self.bind("<ButtonRelease-1>", self.release_drag)
        self.bind("<KeyPress-Escape>", self.cancel_action)

        self.focus_set()

    # ===================== NODE CREATION =====================
    def left_click(self, event):
        x, y = event.x, event.y
        node = self.get_node_at(x, y)

        if node:
            self.dragging_node = node
            return

        node_id = self.generate_node_name()
        self.graph.add_node(node_id)
        self.nodes_pos[node_id] = (x, y)

        self.draw()

    # ===================== EDGE CREATION =====================
    def right_click(self, event):
        x, y = event.x, event.y
        node = self.get_node_at(x, y)

        if not node:
            return

        # STEP 1
        if self.selected_node is None:
            self.selected_node = node
            self.draw()
            return

        # STEP 2
        start = self.selected_node
        end = node

        self.selected_node = None

        if start == end:
            messagebox.showerror("Erreur", "Les boucles ne sont pas autorisées")
            return

        weight = simpledialog.askinteger("Poids", f"Poids de l'arête {start} → {end}", 
                                         minvalue=1, maxvalue=999)
        if weight is None:
            return

        self.graph.add_edge(start, end, weight)
        self.draw()

    # ===================== DRAG =====================
    def drag_node(self, event):
        if not self.dragging_node:
            return

        self.nodes_pos[self.dragging_node] = (event.x, event.y)
        self.draw()

    def release_drag(self, event):
        self.dragging_node = None

    # ===================== UTIL =====================
    def get_node_at(self, x, y):
        for n, (nx, ny) in self.nodes_pos.items():
            if abs(nx - x) < 20 and abs(ny - y) < 20:
                return n
        return None

    def generate_node_name(self):
        if self.node_count < 26:
            name = chr(65 + self.node_count)
        else:
            name = f"N{self.node_count}"
        self.node_count += 1
        return name

    # ===================== DRAW =====================
    def draw(self):
        self.delete("all")
        self.node_items.clear()
        self.node_texts.clear()
        self.edge_items.clear()
        self.weight_items.clear()

        # Dessiner les arêtes
        for u, v, w in self.graph.get_edges():
            if u in self.nodes_pos and v in self.nodes_pos:
                self._draw_edge(u, v, w)

        # Dessiner le contour du nœud sélectionné
        if self.selected_node:
            x, y = self.nodes_pos[self.selected_node]
            self.create_oval(x-24, y-24, x+24, y+24, 
                           outline=self.colors["node_selected"], 
                           width=3, dash=(5, 5))

        # Dessiner les nœuds
        for n, (x, y) in self.nodes_pos.items():
            self._draw_node(n, x, y)

    def _draw_node(self, node, x, y):
        """Dessine un nœud avec ombre et dégradé"""
        # Ombre
        self.create_oval(x-20, y-20, x+20, y+20, 
                        fill="#0f0f13", outline="", width=0)
        
        # Cercle principal
        node_id = self.create_oval(
            x-18, y-18, x+18, y+18,
            fill=self.colors["node"],
            outline=self.colors["node_outline"],
            width=2.5
        )
        self.node_items[node] = node_id
        
        # Dégradé intérieur (petit cercle)
        self.create_oval(x-12, y-12, x+12, y+12,
                        fill="#3a3b4c", outline="", width=0)
        
        # Texte du nœud
        text_id = self.create_text(
            x, y, 
            text=node, 
            fill=self.colors["text"],
            font=("Arial", 12, "bold")
        )
        self.node_texts[node] = text_id

    def _draw_edge(self, u, v, weight):
        """Dessine une arête avec un poids encercolé"""
        x1, y1 = self.nodes_pos[u]
        x2, y2 = self.nodes_pos[v]
        
        # Calculer l'angle pour décaler les flèches sur les arêtes non dirigées
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Ajuster les points de départ et d'arrivée pour toucher les bords des cercles
        r = 18  # Rayon du nœud
        offset_x1 = r * math.cos(angle)
        offset_y1 = r * math.sin(angle)
        offset_x2 = r * math.cos(angle + math.pi)
        offset_y2 = r * math.sin(angle + math.pi)
        
        start_x = x1 + offset_x1
        start_y = y1 + offset_y1
        end_x = x2 + offset_x2
        end_y = y2 + offset_y2
        
        # Dessiner la ligne avec effet de courbe légère
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Créer une ligne courbe pour les arêtes
        if self.graph.directed:
            # Ligne droite pour graphe dirigé
            edge_id = self.create_line(
                start_x, start_y, end_x, end_y,
                fill=self.colors["edge"],
                width=2.5,
                arrow=tk.LAST,
                arrowshape=(16, 20, 8)
            )
        else:
            # Ligne droite pour graphe non dirigé
            edge_id = self.create_line(
                start_x, start_y, end_x, end_y,
                fill=self.colors["edge"],
                width=2.5
            )
        
        self.edge_items[(u, v)] = edge_id
        
        # Dessiner le poids dans un cercle
        self._draw_weight_circle(mid_x, mid_y, weight)

    def _draw_weight_circle(self, x, y, weight):
        """Dessine un poids dans un cercle stylisé"""
        # Cercle de fond
        circle_id = self.create_oval(
            x-14, y-14, x+14, y+14,
            fill=self.colors["weight_bg"],
            outline=self.colors["weight_border"],
            width=2
        )
        
        # Petit dégradé
        self.create_oval(x-10, y-10, x+10, y+10,
                        fill="#2a2b3c", outline="", width=0)
        
        # Texte du poids
        text_id = self.create_text(
            x, y,
            text=str(weight),
            fill=self.colors["text"],
            font=("Arial", 10, "bold")
        )
        
        self.weight_items[(x, y)] = (circle_id, text_id)

    # ===================== ANIMATION METHODS =====================
    def reset_animation(self):
        """Réinitialise les couleurs du graphe pour une nouvelle animation"""
        self.reset_colors()

    def reset_colors(self):
        """Remet les couleurs par défaut à tous les éléments du graphe"""
        # Réinitialiser les couleurs des nœuds
        for node_id, item in self.node_items.items():
            self.itemconfig(item, fill=self.colors["node"], 
                          outline=self.colors["node_outline"], width=2.5)
            if node_id in self.node_texts:
                self.itemconfig(self.node_texts[node_id], fill=self.colors["text"])
        
        # Réinitialiser les couleurs des arêtes
        for edge_id, item in self.edge_items.items():
            self.itemconfig(item, fill=self.colors["edge"], width=2.5)

    def highlight_node(self, node, color):
        """Met en évidence un nœud avec une couleur spécifique"""
        if node in self.node_items:
            self.itemconfig(self.node_items[node], fill=color, 
                          outline="white", width=3)
            # Mettre le texte en blanc
            if node in self.node_texts:
                self.itemconfig(self.node_texts[node], fill="white")

    def highlight_edge(self, node1, node2, color):
        """Met en évidence une arête avec une couleur spécifique"""
        # Chercher l'arête dans les deux sens
        edge_key = (node1, node2)
        if edge_key in self.edge_items:
            self.itemconfig(self.edge_items[edge_key], fill=color, width=4)
        
        edge_key_reverse = (node2, node1)
        if edge_key_reverse in self.edge_items:
            self.itemconfig(self.edge_items[edge_key_reverse], fill=color, width=4)

    def update_distances(self, distances):
        """Met à jour l'affichage des distances sur les nœuds"""
        for node, dist in distances.items():
            if node in self.node_texts and node in self.nodes_pos:
                x, y = self.nodes_pos[node]
                if dist == float('inf'):
                    self.itemconfig(self.node_texts[node], text=node)
                else:
                    self.itemconfig(self.node_texts[node], text=f"{node}\n{dist}")
                    self.coords(self.node_texts[node], x, y)

    # ===================== PATH ANIMATION =====================
    def animate_path(self, path, i=0):
        """Anime le chemin trouvé"""
        if not path:
            return

        if i == 0:
            self.reset_colors()

        # Colorier les arêtes visitées
        for j in range(i):
            if j + 1 < len(path):
                u, v = path[j], path[j + 1]
                self._highlight_path_edge(u, v, "#9ece6a")

        # Colorier l'arête courante
        if i < len(path) - 1:
            u, v = path[i], path[i + 1]
            self._highlight_path_edge(u, v, "#f7768e", width=5)
            self.highlight_node(u, "#e0af68")
            self.highlight_node(v, "#e0af68")
            self.after(500, lambda: self.animate_path(path, i + 1))
        else:
            if path:
                self.highlight_node(path[-1], "#9ece6a")

    def _highlight_path_edge(self, u, v, color, width=4):
        """Met en évidence une arête du chemin"""
        if u in self.nodes_pos and v in self.nodes_pos:
            x1, y1 = self.nodes_pos[u]
            x2, y2 = self.nodes_pos[v]
            
            # Recalculer les points avec les offsets
            angle = math.atan2(y2 - y1, x2 - x1)
            r = 18
            offset_x1 = r * math.cos(angle)
            offset_y1 = r * math.sin(angle)
            offset_x2 = r * math.cos(angle + math.pi)
            offset_y2 = r * math.sin(angle + math.pi)
            
            start_x = x1 + offset_x1
            start_y = y1 + offset_y1
            end_x = x2 + offset_x2
            end_y = y2 + offset_y2
            
            self.create_line(
                start_x, start_y, end_x, end_y,
                fill=color,
                width=width,
                arrow=tk.LAST if self.graph.directed else None,
                arrowshape=(16, 20, 8)
            )

    # ===================== CANCEL =====================
    def cancel_action(self, event=None):
        self.selected_node = None
    

    def left_click(self, event):
       x, y = event.x, event.y
       node = self.get_node_at(x, y)

       if node:
          self.dragging_node = node
          return

       node_id = self.generate_node_name()
       self.graph.add_node(node_id)
       self.nodes_pos[node_id] = (x, y)

       self.draw()
    
    # Mettre à jour automatiquement le panel de contrôle
       self._update_control_panel()

    def _update_control_panel(self):
         """Met à jour le panel de contrôle avec les nouveaux nœuds"""
    try:
        # Remonter jusqu'à l'application principale
             root = self.winfo_toplevel()
             for child in root.winfo_children():
              if hasattr(child, 'controls'):
                child.controls.update_node_list()
                break
    except:
        pass  # Ignorer les erreurs si le panel n'existe pas encore