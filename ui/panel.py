import tkinter as tk

class ResultsPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#24283b")

        # LEFT = TABLEAU
        self.table_frame = tk.Frame(self, bg="#1a1b26")
        self.table_frame.pack(side="left", fill="both", expand=True)

        # RIGHT = DEMARCHE
        self.steps_frame = tk.Frame(self, bg="#0f0f13")
        self.steps_frame.pack(side="right", fill="both", expand=True)

        # Style pour le tableau
        self.table_text = tk.Text(
            self.table_frame,
            bg="#1a1b26",
            fg="#c0caf5",
            font=("Courier New", 10),
            wrap=tk.NONE,
            relief="flat",
            padx=10,
            pady=10
        )
        
        # Scrollbar horizontale pour le tableau
        h_scrollbar = tk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.table_text.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.table_text.config(xscrollcommand=h_scrollbar.set)
        
        # Scrollbar verticale
        v_scrollbar = tk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table_text.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table_text.config(yscrollcommand=v_scrollbar.set)
        
        self.table_text.pack(fill="both", expand=True)

        # Panel des étapes avec style amélioré
        self.steps_text = tk.Text(
            self.steps_frame,
            bg="#0f0f13",
            fg="#7dcfff",
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            relief="flat",
            padx=10,
            pady=10
        )
        
        # Scrollbar pour les étapes
        steps_scrollbar = tk.Scrollbar(self.steps_frame, orient=tk.VERTICAL, command=self.steps_text.yview)
        steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.steps_text.config(yscrollcommand=steps_scrollbar.set)
        
        self.steps_text.pack(fill="both", expand=True)

    # =========================
    # RESULTAT COMPLET
    # =========================
    def show_result(self, dist, path, algo, steps=None, parent=None, visited=None):
        self.table_text.delete("1.0", tk.END)
        self.steps_text.delete("1.0", tk.END)

        visited = visited or set()
        parent = parent or {}

        # ================= TITRE =================
        self.table_text.insert(tk.END, f"{'='*60}\n", "title")
        self.table_text.insert(tk.END, f"{algo:^60}\n", "title")
        self.table_text.insert(tk.END, f"{'='*60}\n\n", "title")

        # ================= CHEMIN =================
        self.table_text.insert(tk.END, " CHEMIN TROUVÉ\n", "subtitle")
        self.table_text.insert(tk.END, f"{'-'*60}\n", "line")
        self.table_text.insert(tk.END, f" {' → '.join(path)}\n\n", "path")

        # ================= TABLEAU =================
        self.table_text.insert(tk.END, " TABLEAU DES DISTANCES\n", "subtitle")
        self.table_text.insert(tk.END, f"{'-'*60}\n", "line")
        
        # En-tête du tableau
        self.table_text.insert(
            tk.END,
            f"{'│':<1}{'Sommet':^10}{'│':<1}{'Distance (depuis source)':^25}{'│':<1}{'Prédécesseur':^12}{'│':<1}{'Visité':^8}{'│':<1}\n",
            "header"
        )
        self.table_text.insert(tk.END, f"{'├'}{'─'*10}{'┼'}{'─'*25}{'┼'}{'─'*12}{'┼'}{'─'*8}{'┤'}\n", "line")
        
        # TRI PAR DISTANCE
        nodes = sorted(dist.keys(), key=lambda x: dist[x])

        for k in nodes:
            v = dist.get(k, float('inf'))
            val = "∞" if v == float('inf') else str(v)
            p = parent.get(k, "-")
            if p is None:
                p = "-"
            vis = "Oui" if k in visited else "Non"
            
            self.table_text.insert(
                tk.END,
                f"{'│':<1}{k:^10}{'│':<1}{val:^25}{'│':<1}{p:^12}{'│':<1}{vis:^8}{'│':<1}\n",
                "row"
            )
        
        self.table_text.insert(tk.END, f"{'└'}{'─'*10}{'┴'}{'─'*25}{'┴'}{'─'*12}{'┴'}{'─'*8}{'┘'}\n", "line")

        # ================= DEMARCHE =================
        self.steps_text.insert(tk.END, f"{'='*50}\n", "title")
        self.steps_text.insert(tk.END, f"DÉMARCHE DE L'ALGORITHME\n", "title")
        self.steps_text.insert(tk.END, f"{'='*50}\n\n", "title")

        if steps:
            for i, s in enumerate(steps):
                step_num = f"{i+1:02d}"
                self.steps_text.insert(tk.END, f"┌{'─'*48}┐\n", "step_box")
                self.steps_text.insert(tk.END, f"│ {step_num} ➤ {s:<44}│\n", "step")
                self.steps_text.insert(tk.END, f"└{'─'*48}┘\n\n", "step_box")
        else:
            self.steps_text.insert(tk.END, "│ Aucune étape enregistrée │\n", "step")

        # Configuration des styles
        self._configure_tags()

    def _configure_tags(self):
        """Configure les styles pour le texte"""
        # Styles pour le tableau
        self.table_text.tag_config("title", font=("Courier New", 11, "bold"), foreground="#7aa2f7")
        self.table_text.tag_config("subtitle", font=("Courier New", 10, "bold"), foreground="#9ece6a")
        self.table_text.tag_config("line", foreground="#565f89")
        self.table_text.tag_config("header", font=("Courier New", 10, "bold"), foreground="#e0af68")
        self.table_text.tag_config("row", foreground="#c0caf5")
        self.table_text.tag_config("path", font=("Courier New", 10, "bold"), foreground="#9ece6a")
        
        # Styles pour les étapes
        self.steps_text.tag_config("title", font=("Segoe UI", 11, "bold"), foreground="#7aa2f7")
        self.steps_text.tag_config("step_box", foreground="#565f89")
        self.steps_text.tag_config("step", foreground="#7dcfff")

    # =========================
    # TABLE ÉTAPE (animation)
    # =========================
    def show_table_step(self, table):
        """Affiche une étape de la table Dijkstra pendant l'animation"""
        self.table_text.delete("1.0", tk.END)
        
        # En-tête
        self.table_text.insert("end", f"{'='*60}\n", "title")
        self.table_text.insert("end", " ÉTAPE DE L'ALGORITHME\n", "subtitle")
        self.table_text.insert("end", f"{'='*60}\n\n", "title")
        
        # En-tête du tableau
        self.table_text.insert(
            "end",
            f"{'│':<1}{'Sommet':^10}{'│':<1}{'Distance':^25}{'│':<1}{'Prédécesseur':^12}{'│':<1}\n",
            "header"
        )
        self.table_text.insert("end", f"{'├'}{'─'*10}{'┼'}{'─'*25}{'┼'}{'─'*12}{'┤'}\n", "line")
        
        # Récupérer les données
        if isinstance(table, dict):
            dist = table.get("dist", {})
            parent = table.get("parent", {})
        else:
            dist = table if isinstance(table, dict) else {}
            parent = {}
        
        if not dist:
            self.table_text.insert("end", f"{'│':<1}{'Aucune donnée disponible':^49}{'│':<1}\n")
            self.table_text.insert("end", f"{'└'}{'─'*10}{'┴'}{'─'*25}{'┴'}{'─'*12}{'┘'}\n")
            return
        
        # Trier par distance
        nodes = sorted(dist.keys(), key=lambda x: dist[x])
        
        # Afficher chaque ligne
        for k in nodes:
            v = dist[k]
            val = "∞" if v == float('inf') else str(v)
            p = parent.get(k, "-")
            if p is None:
                p = "-"
            
            self.table_text.insert(
                "end",
                f"{'│':<1}{k:^10}{'│':<1}{val:^25}{'│':<1}{p:^12}{'│':<1}\n",
                "row"
            )
        
        self.table_text.insert("end", f"{'└'}{'─'*10}{'┴'}{'─'*25}{'┴'}{'─'*12}{'┘'}\n", "line")
        
        # Appliquer les styles
        self._configure_tags()

    # =========================
    # AJOUTER UNE ÉTAPE (animation)
    # =========================
    def add_step(self, step_text):
        """Ajoute une étape textuelle dans le panel de droite"""
        step_num = self.steps_text.index('end-1c').split('.')[0]
        self.steps_text.insert("end", f"┌{'─'*48}┐\n", "step_box")
        self.steps_text.insert("end", f"│ {step_num} ➤ {step_text:<44}│\n", "step")
        self.steps_text.insert("end", f"└{'─'*48}┘\n\n", "step_box")
        self.steps_text.see("end")
        
        self._configure_tags()

    def clear(self):
        """Efface tous les panels"""
        self.table_text.delete("1.0", tk.END)
        self.steps_text.delete("1.0", tk.END)