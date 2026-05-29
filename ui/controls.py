import tkinter as tk
from tkinter import ttk, messagebox

class ControlPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#1a1b26")
        self.app = app
        self.graph = app.graph  # Référence directe au graphe

        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()

        # 📦 Container principal
        container = tk.Frame(self, bg="#1a1b26")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # 🎨 Styles pour combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TCombobox", 
                       fieldbackground="#2a2b3c",
                       background="#2a2b3c",
                       foreground="#c0caf5",
                       arrowcolor="#7aa2f7",
                       bordercolor="#2a2b3c",
                       lightcolor="#2a2b3c",
                       darkcolor="#2a2b3c")
        style.map("Custom.TCombobox",
                 fieldbackground=[('readonly', '#2a2b3c')],
                 foreground=[('readonly', '#c0caf5')])

        # 📊 SECTION NŒUDS
        nodes_frame = tk.LabelFrame(container, text="⚙️ PARAMÈTRES", 
                                    bg="#2a2b3c", fg="#7aa2f7",
                                    font=("Segoe UI", 9, "bold"),
                                    relief="flat", bd=0)
        nodes_frame.pack(fill="x", pady=(0, 15))
        
        # Ligne décorative
        tk.Frame(nodes_frame, height=2, bg="#7aa2f7").pack(fill="x", padx=2)
        
        # Conteneur pour start et end
        input_frame = tk.Frame(nodes_frame, bg="#2a2b3c")
        input_frame.pack(fill="x", padx=15, pady=15)
        
        # START
        start_frame = tk.Frame(input_frame, bg="#2a2b3c")
        start_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Label(start_frame, text="🚀 NŒUD DE DÉPART", 
                fg="#9ece6a", bg="#2a2b3c",
                font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.start_combo = ttk.Combobox(start_frame, textvariable=self.start_var,
                                        font=("Segoe UI", 11),
                                        state="readonly",
                                        style="Custom.TCombobox")
        self.start_combo.pack(fill="x", ipady=5)
        
        # END
        end_frame = tk.Frame(input_frame, bg="#2a2b3c")
        end_frame.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        tk.Label(end_frame, text="🏁 NŒUD D'ARRIVÉE", 
                fg="#f7768e", bg="#2a2b3c",
                font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.end_combo = ttk.Combobox(end_frame, textvariable=self.end_var,
                                      font=("Segoe UI", 11),
                                      state="readonly",
                                      style="Custom.TCombobox")
        self.end_combo.pack(fill="x", ipady=5)
        
        # 🔘 BOUTONS
        button_frame = tk.Frame(container, bg="#1a1b26")
        button_frame.pack(fill="x", pady=10)
        
        self.btn_dijkstra = tk.Button(
            button_frame,
            text="▶ EXÉCUTER DIJKSTRA",
            command=self.run_dijkstra,
            bg="#7aa2f7",
            fg="#1a1b26",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=20,
            pady=12,
            activebackground="#5f89d9",
            cursor="hand2"
        )
        self.btn_dijkstra.pack(fill="x", ipady=5, pady=(0, 10))
        
        self.btn_reset = tk.Button(
            button_frame,
            text="🔄 RÉINITIALISER",
            command=self.reset,
            bg="#2a2b3c",
            fg="#c0caf5",
            font=("Segoe UI", 10),
            relief="flat",
            padx=20,
            pady=8,
            activebackground="#3b4268",
            cursor="hand2"
        )
        self.btn_reset.pack(fill="x", ipady=3)
        
        # 🔄 Bouton rafraîchir
        self.btn_refresh = tk.Button(
            button_frame,
            text="🔄 RAFRAÎCHIR LA LISTE",
            command=self.update_node_list,
            bg="#3b4268",
            fg="#c0caf5",
            font=("Segoe UI", 9),
            relief="flat",
            padx=20,
            pady=5,
            activebackground="#565f89",
            cursor="hand2"
        )
        self.btn_refresh.pack(fill="x", pady=(5, 0))
        
        # ℹ️ INFO
        info_label = tk.Label(container, 
                              text="💡 Cliquez droit sur un nœud → Créer une arête\n🔄 Cliquez sur 'Rafraîchir' pour mettre à jour la liste",
                              fg="#565f89", bg="#1a1b26",
                              font=("Segoe UI", 8),
                              justify="center")
        info_label.pack(pady=(15, 0))
        
        # Mettre à jour la liste initiale
        self.update_node_list()

    def update_node_list(self):
        """Met à jour les combobox avec les nœuds disponibles"""
        nodes = sorted(self.graph.get_nodes())
        print(f"Mise à jour des nœuds: {nodes}")  # Debug
        
        self.start_combo['values'] = nodes
        self.end_combo['values'] = nodes
        
        if nodes:
            # Si pas de sélection ou sélection invalide
            if not self.start_var.get() or self.start_var.get() not in nodes:
                self.start_var.set(nodes[0])
            if not self.end_var.get() or self.end_var.get() not in nodes:
                # Prendre le dernier nœud ou le premier si un seul nœud
                self.end_var.set(nodes[-1] if len(nodes) > 1 else nodes[0])
        else:
            self.start_var.set("")
            self.end_var.set("")
            self.start_combo['values'] = []
            self.end_combo['values'] = []

    def run_dijkstra(self):
        start = self.start_var.get()
        end = self.end_var.get()
        
        if not start or not end:
            messagebox.showerror("Erreur", "Sélectionnez les nœuds de départ et d'arrivée")
            return
        
        if start == end:
            messagebox.showerror("Erreur", "Les nœuds de départ et d'arrivée doivent être différents")
            return
        
        # Vérifier que les nœuds existent
        nodes = self.graph.get_nodes()
        if start not in nodes:
            messagebox.showerror("Erreur", f"Le nœud '{start}' n'existe pas")
            self.update_node_list()
            return
        
        if end not in nodes:
            messagebox.showerror("Erreur", f"Le nœud '{end}' n'existe pas")
            self.update_node_list()
            return
        
        self.app.run_dijkstra(start, end)

    def reset(self):
        self.start_var.set("")
        self.end_var.set("")
        self.update_node_list()
        if hasattr(self.app, 'reset'):
            self.app.reset()