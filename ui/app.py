import tkinter as tk
from ui.canvas import GraphCanvas
from ui.panel import ResultsPanel
from ui.controls import ControlPanel
from core.graph import Graph
from core.algorithms import run_dijkstra
import re


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Solver Pro")
        self.root.geometry("1400x900")

        self.graph = Graph()
        
        # Initialiser les attributs
        self.steps = []
        self.path = []
        self.dist = {}
        self.tables = []
        self.start_node = None
        self.end_node = None

        # layout
        self.main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill="both", expand=True)

        # LEFT
        self.left_frame = tk.Frame(self.main_pane)
        self.canvas = GraphCanvas(self.left_frame, self.graph)
        self.canvas.pack(fill="both", expand=True)
        self.main_pane.add(self.left_frame, minsize=800)

        # RIGHT
        self.right_frame = tk.Frame(self.main_pane, bg="#0f0f13")
        self.controls = ControlPanel(self.right_frame, self)
        self.controls.pack(fill="x")
        self.main_pane.add(self.right_frame, minsize=300)

        # BOTTOM
        self.bottom_frame = tk.Frame(root, height=250, bg="#24283b")
        self.bottom_frame.pack(fill="x", side="bottom")

        self.panel = ResultsPanel(self.bottom_frame)
        self.panel.pack(fill="both", expand=True)

    def run_dijkstra(self, start, end):
        if start not in self.graph.get_nodes() or end not in self.graph.get_nodes():
            return

        self.start_node = start
        self.end_node = end

        # Réinitialiser l'affichage
        self.canvas.reset_animation()
        self.canvas.draw()

        # Exécuter l'algorithme
        result = run_dijkstra(self.graph, start, end)

        self.steps = result.get("steps", [])
        self.path = result.get("path", [])
        self.dist = result.get("distance", {})
        self.tables = result.get("tables", [])
        parent = result.get("parent", {})
        visited = result.get("visited", set())

        # Afficher le résultat
        self.panel.show_result(
            self.dist, self.path, "DIJKSTRA",
            self.steps, parent, visited
        )
        
        # Démarrer l'animation
        if self.steps and self.tables:
            self._animate_dijkstra(0)

    def _animate_dijkstra(self, i=0):
        if i >= len(self.steps):
            if self.path:
                self.canvas.animate_path(self.path)
            return

        step = self.steps[i]
        self.panel.steps_text.insert("end", step + "\n")
        self.panel.steps_text.see("end")

        if i < len(self.tables):
            self.panel.show_table_step(self.tables[i])
            table = self.tables[i]
            if isinstance(table, dict) and "dist" in table:
                self.canvas.update_distances(table["dist"])

        # Colorier le nœud ou l'arête selon l'étape
        if "Choix du sommet" in step:
            match = re.search(r"Choix du sommet (\w+)", step)
            if match:
                self.canvas.highlight_node(match.group(1), "#f7768e")
        elif "Relaxation" in step:
            match = re.search(r"Relaxation: (\w+)->(\w+)", step)
            if match:
                self.canvas.highlight_edge(match.group(1), match.group(2), "#e0af68")

        self.root.after(800, lambda: self._animate_dijkstra(i + 1))

    def reset(self):
       """Réinitialise l'affichage"""
       if hasattr(self, 'canvas'):
        self.canvas.reset_animation()
        self.canvas.draw()
       if hasattr(self, 'panel'):
        self.panel.table_text.delete("1.0", tk.END)
        self.panel.steps_text.delete("1.0", tk.END)
    # Réinitialiser les variables
       self.steps = []
       self.path = []
       self.dist = {}
       self.tables = []