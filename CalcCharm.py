import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os

class DamageCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Dano - Tibia")
        self.root.geometry("950x750")
        
        # Conexão com o banco de dados
        self.db_path = os.path.join(os.path.dirname(__file__), "monsters.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        # Variáveis de entrada
        self.attack_value = tk.DoubleVar(value=318)
        self.auto_extra = tk.DoubleVar(value=9)
        self.crit_chance = tk.DoubleVar(value=10.0)
        self.crit_extra = tk.DoubleVar(value=57.5)
        self.life_leech = tk.DoubleVar(value=50.75)
        self.mana_leech = tk.DoubleVar(value=16.25)
        self.attacks_per_min = tk.DoubleVar(value=30.0)
        
        # Variável para hunt atual
        self.current_hunt_id = tk.IntVar(value=1)
        self.current_hunt_name = tk.StringVar()
        
        # Lista de monstros (será carregada do banco)
        self.monsters = []
        
        # Criar interface
        self.create_widgets()
        
        # Carregar hunts do banco e preencher combobox
        self.load_hunts()
        
        # Carregar monstros da hunt inicial (ID 1 se existir)
        self.load_monsters_for_hunt(self.current_hunt_id.get())
        
    def create_tables(self):
        # Cria as tabelas se não existirem
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS monsters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hunt_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                qty INTEGER NOT NULL,
                hp REAL NOT NULL,
                weakness REAL NOT NULL,
                rune_type TEXT NOT NULL,
                FOREIGN KEY (hunt_id) REFERENCES hunts (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()
        
        # Inserir algumas hunts de exemplo se a tabela estiver vazia
        self.cursor.execute("SELECT COUNT(*) FROM hunts")
        if self.cursor.fetchone()[0] == 0:
            example_hunts = [
                ("Bulltaur Lair",),
                ("Goannas",),
                ("Oramond",)
            ]
            self.cursor.executemany("INSERT INTO hunts (name) VALUES (?)", example_hunts)
            self.conn.commit()
            
            # Inserir monstros de exemplo para Bulltaur Lair (hunt_id = 1)
            example_monsters = [
                (1, "Bulltaur Alchemist", 614, 5960, 1.2, "Normal"),
                (1, "Bulltaur Brute", 607, 6560, 1.1, "Divine Wrath"),
                (1, "Bulltaur Forgepriest", 396, 6840, 1.1, "Freeze"),
                # Goannas (hunt_id = 2)
                (2, "Adult Goanna", 359, 8300, 1.2, "Zap"),
                (2, "Manticore", 340, 6700, 1.2, "Freeze"),
                (2, "Young Goanna", 319, 6944, 1.2, "Zap"),
                (2, "Feral Sphinx", 292, 9800, 1.15, "Freeze"),
                # Oramond (hunt_id = 3)
                (3, "Dark Torturer", 171, 7350, 1.1, "Divine Wrath"),
                (3, "Grim Reaper", 206, 3900, 1.0, "Zap"),
                (3, "Destroyer", 222, 3700, 1.0, "Low Blow"),
                (3, "Hellspawn", 269, 3500, 1.0, "Savage Blow"),
            ]
            self.cursor.executemany('''
                INSERT INTO monsters (hunt_id, name, qty, hp, weakness, rune_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', example_monsters)
            self.conn.commit()
    
    def create_widgets(self):
        # Frame superior com seleção de hunt e créditos
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text="Hunt atual:").pack(side="left", padx=5)
        self.hunt_combo = ttk.Combobox(top_frame, textvariable=self.current_hunt_name, state="readonly")
        self.hunt_combo.pack(side="left", padx=5)
        self.hunt_combo.bind("<<ComboboxSelected>>", self.on_hunt_selected)
        
        ttk.Button(top_frame, text="Nova Hunt", command=self.new_hunt).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Renomear Hunt", command=self.rename_hunt).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Excluir Hunt", command=self.delete_hunt).pack(side="left", padx=5)
        
        # Créditos
        ttk.Label(top_frame, text="Criado por Cedine Rush", font=("Arial", 9, "italic")).pack(side="right", padx=10)
        
        # Frame de parâmetros do personagem
        param_frame = ttk.LabelFrame(self.root, text="Parâmetros do Personagem", padding=10)
        param_frame.pack(fill="x", padx=10, pady=5)
        
        # Linha 1
        row1 = ttk.Frame(param_frame)
        row1.pack(fill="x", pady=2)
        ttk.Label(row1, text="Ataque Base:").pack(side="left", padx=5)
        ttk.Entry(row1, textvariable=self.attack_value, width=10).pack(side="left", padx=5)
        ttk.Label(row1, text="Dano Extra Auto:").pack(side="left", padx=5)
        ttk.Entry(row1, textvariable=self.auto_extra, width=10).pack(side="left", padx=5)
        
        # Linha 2
        row2 = ttk.Frame(param_frame)
        row2.pack(fill="x", pady=2)
        ttk.Label(row2, text="Chance Crítico (%):").pack(side="left", padx=5)
        ttk.Entry(row2, textvariable=self.crit_chance, width=10).pack(side="left", padx=5)
        ttk.Label(row2, text="Dano Crítico Extra (%):").pack(side="left", padx=5)
        ttk.Entry(row2, textvariable=self.crit_extra, width=10).pack(side="left", padx=5)
        
        # Linha 3
        row3 = ttk.Frame(param_frame)
        row3.pack(fill="x", pady=2)
        ttk.Label(row3, text="Life Leech (%):").pack(side="left", padx=5)
        ttk.Entry(row3, textvariable=self.life_leech, width=10).pack(side="left", padx=5)
        ttk.Label(row3, text="Mana Leech (%):").pack(side="left", padx=5)
        ttk.Entry(row3, textvariable=self.mana_leech, width=10).pack(side="left", padx=5)
        
        # Linha 4
        row4 = ttk.Frame(param_frame)
        row4.pack(fill="x", pady=2)
        ttk.Label(row4, text="Ataques por minuto:").pack(side="left", padx=5)
        ttk.Entry(row4, textvariable=self.attacks_per_min, width=10).pack(side="left", padx=5)
        
        # Botão para calcular dano médio e leech
        ttk.Button(param_frame, text="Calcular Dano Médio", command=self.calc_avg_damage).pack(pady=5)
        
        # Labels para exibir resultados
        self.result_label = ttk.Label(param_frame, text="", font=("Arial", 10, "bold"))
        self.result_label.pack()
        
        # Frame da lista de monstros
        monster_frame = ttk.LabelFrame(self.root, text="Monstros da Hunt", padding=10)
        monster_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview para mostrar os monstros
        columns = ("name", "qty", "hp", "weakness", "rune_type", "dmg_per_mob", "total_dmg")
        self.tree = ttk.Treeview(monster_frame, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="Nome")
        self.tree.heading("qty", text="Quantidade/h")
        self.tree.heading("hp", text="Vida")
        self.tree.heading("weakness", text="Fraqueza")
        self.tree.heading("rune_type", text="Tipo de Runa")
        self.tree.heading("dmg_per_mob", text="Dano por Mob")
        self.tree.heading("total_dmg", text="Dano Total/h")
        
        # Ajustar larguras
        self.tree.column("name", width=150)
        self.tree.column("qty", width=80)
        self.tree.column("hp", width=80)
        self.tree.column("weakness", width=80)
        self.tree.column("rune_type", width=100)
        self.tree.column("dmg_per_mob", width=100)
        self.tree.column("total_dmg", width=100)
        
        self.tree.pack(fill="both", expand=True)
        
        # Botões para gerenciar monstros
        btn_frame = ttk.Frame(monster_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Adicionar Monstro", command=self.add_monster_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar Monstro", command=self.edit_monster_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Remover Selecionado", command=self.remove_monster).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Calcular Totais", command=self.calc_totals).pack(side="left", padx=5)
        
        # Label para exibir totais
        self.total_label = ttk.Label(self.root, text="", font=("Arial", 11, "bold"))
        self.total_label.pack(pady=5)
        
    def load_hunts(self):
        """Carrega todas as hunts do banco e popula o combobox."""
        self.cursor.execute("SELECT id, name FROM hunts ORDER BY name")
        hunts = self.cursor.fetchall()
        self.hunt_list = hunts  # lista de (id, nome)
        hunt_names = [name for _, name in hunts]
        self.hunt_combo['values'] = hunt_names
        if hunt_names:
            self.current_hunt_name.set(hunt_names[0])
            self.current_hunt_id.set(hunts[0][0])
    
    def load_monsters_for_hunt(self, hunt_id):
        """Carrega os monstros da hunt_id e atualiza a treeview."""
        self.cursor.execute('''
            SELECT id, name, qty, hp, weakness, rune_type
            FROM monsters
            WHERE hunt_id = ?
            ORDER BY name
        ''', (hunt_id,))
        rows = self.cursor.fetchall()
        self.monsters = []
        for row in rows:
            self.monsters.append({
                "id": row[0],
                "name": row[1],
                "qty": row[2],
                "hp": row[3],
                "weakness": row[4],
                "rune_type": row[5]
            })
        self.refresh_tree()
    
    def on_hunt_selected(self, event=None):
        """Quando o usuário seleciona uma hunt no combobox."""
        selected_name = self.current_hunt_name.get()
        for hid, name in self.hunt_list:
            if name == selected_name:
                self.current_hunt_id.set(hid)
                self.load_monsters_for_hunt(hid)
                break
    
    def new_hunt(self):
        """Cria uma nova hunt."""
        name = simpledialog.askstring("Nova Hunt", "Nome da nova hunt:", parent=self.root)
        if name and name.strip():
            try:
                self.cursor.execute("INSERT INTO hunts (name) VALUES (?)", (name.strip(),))
                self.conn.commit()
                self.load_hunts()
                # Selecionar a nova hunt
                self.current_hunt_name.set(name.strip())
                self.on_hunt_selected()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Já existe uma hunt com esse nome.")
    
    def rename_hunt(self):
        """Renomeia a hunt atual."""
        if not self.hunt_list:
            return
        new_name = simpledialog.askstring("Renomear Hunt", "Novo nome:", parent=self.root,
                                          initialvalue=self.current_hunt_name.get())
        if new_name and new_name.strip():
            try:
                self.cursor.execute("UPDATE hunts SET name = ? WHERE id = ?",
                                    (new_name.strip(), self.current_hunt_id.get()))
                self.conn.commit()
                self.load_hunts()
                self.current_hunt_name.set(new_name.strip())
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Já existe uma hunt com esse nome.")
    
    def delete_hunt(self):
        """Exclui a hunt atual (com confirmação)."""
        if not self.hunt_list:
            return
        if len(self.hunt_list) == 1:
            messagebox.showwarning("Aviso", "Não é possível excluir a única hunt.")
            return
        confirm = messagebox.askyesno("Confirmar", f"Deseja realmente excluir a hunt '{self.current_hunt_name.get()}'?")
        if confirm:
            self.cursor.execute("DELETE FROM hunts WHERE id = ?", (self.current_hunt_id.get(),))
            self.conn.commit()
            self.load_hunts()
            # Selecionar a primeira hunt da lista
            if self.hunt_list:
                self.current_hunt_id.set(self.hunt_list[0][0])
                self.current_hunt_name.set(self.hunt_list[0][1])
                self.load_monsters_for_hunt(self.current_hunt_id.get())
    
    def refresh_tree(self):
        """Atualiza a treeview com os monstros atuais."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for mob in self.monsters:
            dmg_per_mob = self.calc_rune_damage(mob)
            total_dmg = dmg_per_mob * mob["qty"]
            self.tree.insert("", "end", values=(
                mob["name"],
                mob["qty"],
                mob["hp"],
                mob["weakness"],
                mob["rune_type"],
                round(dmg_per_mob, 2),
                round(total_dmg, 2)
            ), iid=mob["id"])  # usar o id do banco como identificador da linha
    
    def calc_rune_damage(self, mob):
        """Calcula o dano da runa baseado no tipo."""
        rune_type = mob["rune_type"].lower()
        if "low blow" in rune_type:
            mult = 0.08
        elif "savage blow" in rune_type:
            mult = 0.4
        else:
            mult = 0.05
        return mob["hp"] * mult * mob["weakness"]
    
    def calc_avg_damage(self):
        """Calcula o dano médio por ataque e os leechs."""
        try:
            base = self.attack_value.get() + self.auto_extra.get()
            crit_chance = self.crit_chance.get() / 100
            crit_extra = self.crit_extra.get() / 100
            
            normal_dmg = base
            crit_dmg = base * (1 + crit_extra)
            avg_dmg = (1 - crit_chance) * normal_dmg + crit_chance * crit_dmg
            
            life_leech_avg = avg_dmg * (self.life_leech.get() / 100)
            mana_leech_avg = avg_dmg * (self.mana_leech.get() / 100)
            
            result_text = f"Dano médio por ataque: {avg_dmg:.2f} | Life Leech: {life_leech_avg:.2f} | Mana Leech: {mana_leech_avg:.2f}"
            self.result_label.config(text=result_text)
            
            self.avg_damage = avg_dmg
            self.life_leech_avg = life_leech_avg
            self.mana_leech_avg = mana_leech_avg
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro nos cálculos: {e}")
    
    def add_monster_dialog(self, edit_mode=False, monster_id=None):
        """Janela de diálogo para adicionar ou editar monstro."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Monstro" if not edit_mode else "Editar Monstro")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variáveis
        name_var = tk.StringVar()
        qty_var = tk.IntVar()
        hp_var = tk.DoubleVar()
        weak_var = tk.DoubleVar(value=1.0)
        rune_var = tk.StringVar(value="Normal")
        
        # Se for edição, carregar dados
        if edit_mode and monster_id:
            for mob in self.monsters:
                if mob["id"] == monster_id:
                    name_var.set(mob["name"])
                    qty_var.set(mob["qty"])
                    hp_var.set(mob["hp"])
                    weak_var.set(mob["weakness"])
                    rune_var.set(mob["rune_type"])
                    break
        
        ttk.Label(dialog, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Quantidade por hora:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(dialog, textvariable=qty_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Vida:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(dialog, textvariable=hp_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Fraqueza (ex: 1.2 para 120%):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(dialog, textvariable=weak_var, width=30).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Tipo de Runa:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        rune_combo = ttk.Combobox(dialog, textvariable=rune_var, values=["Normal", "Low Blow", "Savage Blow"], state="readonly", width=27)
        rune_combo.grid(row=4, column=1, padx=5, pady=5)
        
        def save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Aviso", "Nome não pode estar vazio")
                return
            try:
                qty = int(qty_var.get())
                hp = float(hp_var.get())
                weakness = float(weak_var.get())
                rune = rune_var.get()
            except ValueError:
                messagebox.showerror("Erro", "Valores numéricos inválidos")
                return
            
            if edit_mode and monster_id:
                # Atualizar no banco
                self.cursor.execute('''
                    UPDATE monsters
                    SET name=?, qty=?, hp=?, weakness=?, rune_type=?
                    WHERE id=?
                ''', (name, qty, hp, weakness, rune, monster_id))
            else:
                # Inserir no banco
                self.cursor.execute('''
                    INSERT INTO monsters (hunt_id, name, qty, hp, weakness, rune_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.current_hunt_id.get(), name, qty, hp, weakness, rune))
            self.conn.commit()
            
            # Recarregar monstros da hunt atual
            self.load_monsters_for_hunt(self.current_hunt_id.get())
            dialog.destroy()
        
        ttk.Button(dialog, text="Salvar", command=save).grid(row=5, column=0, columnspan=2, pady=20)
    
    def edit_monster_dialog(self):
        """Abre o diálogo de edição para o monstro selecionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um monstro para editar")
            return
        monster_id = int(selected[0])
        self.add_monster_dialog(edit_mode=True, monster_id=monster_id)
    
    def remove_monster(self):
        """Remove o monstro selecionado do banco de dados."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um monstro para remover")
            return
        monster_id = int(selected[0])
        confirm = messagebox.askyesno("Confirmar", "Remover este monstro?")
        if confirm:
            self.cursor.execute("DELETE FROM monsters WHERE id = ?", (monster_id,))
            self.conn.commit()
            self.load_monsters_for_hunt(self.current_hunt_id.get())
    
    def calc_totals(self):
        """Calcula dano físico por hora, dano das runas e total."""
        try:
            attacks_per_hour = self.attacks_per_min.get() * 60
            if not hasattr(self, 'avg_damage'):
                self.calc_avg_damage()  # calcula se não foi feito
            phys_damage_hour = self.avg_damage * attacks_per_hour
            
            # Dano das runas (soma dos totais na tree)
            rune_damage_hour = 0
            for mob in self.monsters:
                dmg_per_mob = self.calc_rune_damage(mob)
                rune_damage_hour += dmg_per_mob * mob["qty"]
            
            total_damage = phys_damage_hour + rune_damage_hour
            
            self.total_label.config(
                text=f"Dano Físico/h: {phys_damage_hour:,.0f} | Dano Runas/h: {rune_damage_hour:,.0f} | Dano Total/h: {total_damage:,.0f}"
            )
            # Atualizar a tree (os valores de dano por mob podem ter mudado se a runa foi alterada)
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular totais: {e}")
    
    def __del__(self):
        """Fecha a conexão com o banco ao finalizar."""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = DamageCalculator(root)
    root.mainloop()
