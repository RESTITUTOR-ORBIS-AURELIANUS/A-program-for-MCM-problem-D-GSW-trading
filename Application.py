import tkinter as tk
from tkinter import messagebox, ttk


class Player:
    def __init__(self, name, ws, three_p, ast_to, height, weight, wingspan):
        self.name = name
        self.ws = float(ws)
        self.three_p = float(three_p)
        self.ast_to = float(ast_to)
        self.height = float(height)
        self.weight = float(weight)
        self.wingspan = float(wingspan)
        self.ss = self.calculate_ss()
        self.pe = self.calculate_pe()
    def calculate_ss(self):
        B0 = -1.132
        a = 0.0692
        b = 0.0218
        c = 0.00117
        d = 0.25
        L = self.wingspan - self.height
        penalty = 1.0 if (self.height >= 82 and self.weight >= 245) else 0.0
        ss = B0 + (a * L) + (b * self.height) - (c * self.weight) - (d * penalty)
        return ss
    def calculate_pe(self):
        intercept = -0.58024
        c_ws = 0.47267
        c_ws_ss = 0.23633
        c_ws_3p = 0.67623
        c_ws_at = 0.01185

        pe = (intercept +
              (c_ws * self.ws) +
              (c_ws_ss * self.ws * self.ss) +
              (c_ws_3p * self.ws * self.three_p) +
              (c_ws_at * self.ws * self.ast_to))
        return pe

class TradeEvaluatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Warriors Trade Evaluator Model")
        self.root.geometry("950x650")
        self.outgoing_players = []
        self.incoming_players = []
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Arial", 12, "bold"))
        style.configure("Result.TLabel", font=("Arial", 14, "bold"), foreground="blue")
        header_frame = tk.Frame(root, pady=15)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header_frame, text="2026 Offseason Trade Decision Support System", font=("Arial", 18, "bold"),
                 fg="#1D428A").pack()
        tk.Label(header_frame, text="Based on Multivariate Regression & Ss Switching Model", font=("Arial", 10),
                 fg="gray").pack()
        content_frame = tk.Frame(root, padx=10, pady=10)
        content_frame.pack(expand=True, fill=tk.BOTH)
        self.left_frame = tk.LabelFrame(content_frame, text=" Outgoing Assets ", font=("Arial", 11, "bold"),
                                        fg="#FFC72C", bg="#333333")
        self.left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)

        self.outgoing_tree = self.create_treeview(self.left_frame)
        btn_frame_l = tk.Frame(self.left_frame, bg="#333333")
        btn_frame_l.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame_l, text="+ Add Player", command=lambda: self.open_add_player_window("outgoing"),
                  bg="#FFC72C", fg="black", width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame_l, text="- Remove Selected", command=lambda: self.delete_player("outgoing"), bg="#FF6666",
                  fg="white", width=15).pack(side=tk.RIGHT, padx=10)
        self.right_frame = tk.LabelFrame(content_frame, text=" Incoming Assets ", font=("Arial", 11, "bold"),
                                         fg="#1D428A", bg="white")
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5)

        self.incoming_tree = self.create_treeview(self.right_frame)
        btn_frame_r = tk.Frame(self.right_frame, bg="white")
        btn_frame_r.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame_r, text="+ Add Player", command=lambda: self.open_add_player_window("incoming"),
                  bg="#1D428A", fg="white", width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame_r, text="- Remove Selected", command=lambda: self.delete_player("incoming"), bg="#FF6666",
                  fg="white", width=15).pack(side=tk.RIGHT, padx=10)
        bottom_frame = tk.Frame(root, pady=20, bg="#f0f0f0")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.eval_btn = tk.Button(bottom_frame, text="Evaluate Trade Value", font=("Arial", 14, "bold"),
                                  bg="#1D428A", fg="white", command=self.evaluate_trade, padx=20, pady=5)
        self.eval_btn.pack()

        self.result_label = tk.Label(bottom_frame, text="Waiting for calculation...", font=("Arial", 16), bg="#f0f0f0",
                                     pady=10)
        self.result_label.pack()

    def create_treeview(self, parent):
        columns = ("name", "pe", "ss", "ws")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        tree.heading("name", text="Name")
        tree.heading("pe", text="Pe (Contrib)")
        tree.heading("ss", text="Ss (Switch)")
        tree.heading("ws", text="WS")

        tree.column("name", width=120)
        tree.column("pe", width=80)
        tree.column("ss", width=80)
        tree.column("ws", width=60)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return tree
    def open_add_player_window(self, side):
        win = tk.Toplevel(self.root)
        win.title("Add Player Data")
        win.geometry("400x500")
        fields = [
            ("Player Name:", "entry"),
            ("Last Season WS (Win Shares):", "entry_float"),
            ("3P% (Decimal, e.g., 0.38):", "entry_float"),
            ("AST/TO Ratio:", "entry_float"),
            ("Height (inches):", "entry_float"),
            ("Weight (lbs):", "entry_float"),
            ("Wingspan (inches):", "entry_float")
        ]
        entries = {}
        for i, (label_text, ftype) in enumerate(fields):
            tk.Label(win, text=label_text, font=("Arial", 10)).pack(anchor="w", padx=30, pady=(10, 0))
            e = tk.Entry(win)
            e.pack(fill=tk.X, padx=30, pady=2)
            entries[label_text] = e
        def save():
            try:
                name = entries["Player Name:"].get()
                ws = entries["Last Season WS (Win Shares):"].get()
                tp = entries["3P% (Decimal, e.g., 0.38):"].get()
                ato = entries["AST/TO Ratio:"].get()
                h = entries["Height (inches):"].get()
                w = entries["Weight (lbs):"].get()
                wing = entries["Wingspan (inches):"].get()
                if not name: raise ValueError("Name is required.")
                p = Player(name, ws, tp, ato, h, w, wing)
                if side == "outgoing":
                    self.outgoing_players.append(p)
                    self.refresh_list("outgoing")
                else:
                    self.incoming_players.append(p)
                    self.refresh_list("incoming")
                win.destroy()
            except ValueError as e:
                messagebox.showerror("Input Error",
                                     f"Invalid input format.\nPlease ensure numeric fields are correct.\nError: {e}")
        tk.Button(win, text="Save & Add", command=save, bg="#1D428A", fg="white", font=("Arial", 11, "bold"), pady=5,
                  width=20).pack(pady=30)
    def refresh_list(self, side):
        if side == "outgoing":
            tree = self.outgoing_tree
            players = self.outgoing_players
        else:
            tree = self.incoming_tree
            players = self.incoming_players
        for item in tree.get_children():
            tree.delete(item)
        for p in players:
            tree.insert("", "end", values=(p.name, f"{p.pe:.4f}", f"{p.ss:.4f}", p.ws))

    def delete_player(self, side):
        if side == "outgoing":
            tree = self.outgoing_tree
            lst = self.outgoing_players
        else:
            tree = self.incoming_tree
            lst = self.incoming_players

        selected = tree.selection()
        if not selected: return
        for item_id in selected:
            item_values = tree.item(item_id, 'values')
            name_to_del = item_values[0]
            for p in lst:
                if p.name == name_to_del:
                    lst.remove(p)
                    break
        self.refresh_list(side)

    def evaluate_trade(self):
        sum_out_pe = sum(p.pe for p in self.outgoing_players)
        sum_in_pe = sum(p.pe for p in self.incoming_players)

        diff = sum_in_pe - sum_out_pe

        result_text = f"Total Outgoing Pe: {sum_out_pe:.4f}  vs  Total Incoming Pe: {sum_in_pe:.4f}\n"
        result_text += f"Net Difference: {diff:+.4f}\n\n"

        if diff > 0:
            conclusion = "✅ VERDICT: Trade APPROVED (Worthwhile)"
            color = "green"
        else:
            conclusion = "❌ VERDICT: Trade REJECTED (Not Worthwhile)"
            color = "red"
        self.result_label.config(text=result_text + conclusion, fg=color)
if __name__ == "__main__":
    root = tk.Tk()
    try:
        pass
    except:
        pass

    app = TradeEvaluatorApp(root)
    root.mainloop()