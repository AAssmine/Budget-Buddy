import customtkinter as ctk
from config import *
from utils.helpers import format_currency, DatePickerButton
from tkinter import messagebox, filedialog
from datetime import datetime, date

# Golden ratio spacing: 8, 13, 21, 34
PAD_R = (0, 21)
DD = dict(corner_radius=13, fg_color="#e8e8e2", button_color="#e8e8e2", button_hover_color="#deded4", dropdown_fg_color="#ebebdf", dropdown_hover_color="#deded4", text_color=COLOR_TEXT)


class SettingsView(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_BG_DARK)
        self.app = app
        self.active_tab = "budgets"
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#d6d6cf", scrollbar_button_hover_color="#c0c0b8", scrollbar_fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=(44, 0), pady=21)
        scroll._scrollbar.configure(width=6, corner_radius=3)

        title = "Profil" if (self.app.current_user and self.app.current_user["role"] == "banker") else "Paramètres"
        ctk.CTkLabel(scroll, text=title, font=("Segoe UI", 30, "bold"), text_color=COLOR_TEXT).pack(anchor="w")
        ctk.CTkFrame(scroll, fg_color=COLOR_ACCENT, height=4, width=50, corner_radius=2).pack(anchor="w", pady=(8, 21))

        # Tabs based on role
        is_banker = self.app.current_user and self.app.current_user["role"] == "banker"
        if is_banker:
            tab_list = [("Profil", "profile")]
            self.active_tab = "profile"
        else:
            tab_list = [("Plafonds budget", "budgets"), ("Transferts auto", "recurring"), ("Profil", "profile")]

        # Only show tabs if more than 1
        if len(tab_list) > 1:
            tabs = ctk.CTkFrame(scroll, fg_color="transparent")
            tabs.pack(fill="x", pady=(0, 21), padx=PAD_R)
        else:
            tabs = None
        self.tab_buttons = {}
        if tabs:
            for label, val in tab_list:
                active = val == self.active_tab
                btn = ctk.CTkButton(tabs, text=label, width=140, height=42, corner_radius=13,
                                fg_color=COLOR_PRIMARY if active else COLOR_BG_CARD,
                                hover_color=COLOR_PRIMARY_HOVER if active else COLOR_BG_INPUT,
                                text_color="white" if active else COLOR_TEXT_DIM,
                                border_width=0 if active else 1, border_color=COLOR_BORDER,
                                font=("Segoe UI", 14, "bold"), command=lambda v=val: self._switch(v))
                btn.pack(side="left", padx=(0, 8))
                self.tab_buttons[val] = btn

        self.content = ctk.CTkFrame(scroll, fg_color="transparent")
        self.content.pack(fill="both", expand=True)
        if is_banker:
            self._show_profile()
        else:
            self._show_budgets()

    def _switch(self, tab):
        self.active_tab = tab
        for k, b in self.tab_buttons.items():
            a = k == tab
            b.configure(fg_color=COLOR_PRIMARY if a else COLOR_BG_CARD,
                        hover_color=COLOR_PRIMARY_HOVER if a else COLOR_BG_INPUT,
                        text_color="white" if a else COLOR_TEXT_DIM)
        for w in self.content.winfo_children(): w.destroy()
        {"budgets": self._show_budgets, "recurring": self._show_recurring, "profile": self._show_profile}[tab]()

    # ============================================================ BUDGETS
    def _show_budgets(self):
        f = self.content
        uid = self.app.current_user["id"]

        add = ctk.CTkFrame(f, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        add.pack(fill="x", padx=PAD_R, pady=(0, 21))
        ctk.CTkLabel(add, text="Définir un plafond mensuel", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT).pack(padx=21, pady=(21, 13), anchor="w")

        row = ctk.CTkFrame(add, fg_color="transparent")
        row.pack(fill="x", padx=21, pady=(0, 21))
        self.bgt_cat = ctk.StringVar(value=CATEGORIES[0].capitalize())
        ctk.CTkOptionMenu(row, variable=self.bgt_cat, values=[c.capitalize() for c in CATEGORIES], width=160, height=42, font=("Segoe UI", 14), **DD).pack(side="left", padx=(0, 8))
        self.bgt_amount = ctk.CTkEntry(row, height=42, width=160, corner_radius=13, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, placeholder_text="Montant max (EUR)", font=("Segoe UI", 14))
        self.bgt_amount.pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="Valider", width=100, height=42, corner_radius=13, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="white", font=("Segoe UI", 14, "bold"), command=self._add_budget).pack(side="left")

        limits = self.app.db.get_budget_limits(uid)
        if limits:
            lc = ctk.CTkFrame(f, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
            lc.pack(fill="x", padx=PAD_R)
            ctk.CTkLabel(lc, text="Plafonds actifs", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT).pack(padx=21, pady=(21, 13), anchor="w")
            for lim in limits:
                cat, cap = lim["category"], float(lim["monthly_limit"])
                spent = self.app.db.get_category_spending_this_month(uid, cat)
                pct = min(spent / cap, 1.0) if cap > 0 else 0
                sc = COLOR_DANGER if pct >= 1 else (COLOR_WARNING if pct >= 0.8 else COLOR_SUCCESS)

                lr = ctk.CTkFrame(lc, fg_color=COLOR_BG_INPUT, corner_radius=13)
                lr.pack(fill="x", padx=13, pady=4)
                tr = ctk.CTkFrame(lr, fg_color="transparent")
                tr.pack(fill="x", padx=13, pady=(13, 5))
                ctk.CTkLabel(tr, text=cat.capitalize(), font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT).pack(side="left")
                ctk.CTkLabel(tr, text=f"{format_currency(spent)} / {format_currency(cap)}", font=("Segoe UI", 13), text_color=COLOR_TEXT_DIM).pack(side="left", padx=(13, 0))
                ctk.CTkButton(tr, text="X", width=28, height=28, corner_radius=8, fg_color=COLOR_DANGER_LIGHT, hover_color=COLOR_DANGER, text_color=COLOR_DANGER, font=("Segoe UI", 13), command=lambda c=cat: self._del_budget(c)).pack(side="right")
                ctk.CTkLabel(tr, text=f"{pct*100:.0f}%", font=("Segoe UI", 13, "bold"), text_color=sc).pack(side="right", padx=(0, 8))

                bar = ctk.CTkProgressBar(lr, height=5, corner_radius=3, progress_color=sc, fg_color=COLOR_BG_DARK)
                bar.pack(fill="x", padx=13, pady=(0, 13))
                bar.set(pct)
            ctk.CTkFrame(lc, height=8, fg_color="transparent").pack()
        else:
            ctk.CTkLabel(f, text="Aucun plafond défini.", font=("Segoe UI", 14), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=13)

    def _add_budget(self):
        try: amount = float(self.bgt_amount.get().replace(",", "."))
        except ValueError: messagebox.showerror("Erreur", "Montant invalide."); return
        if amount <= 0: messagebox.showerror("Erreur", "Positif requis."); return
        self.app.db.set_budget_limit(self.app.current_user["id"], self.bgt_cat.get().lower(), amount)
        self._switch("budgets")

    def _del_budget(self, cat):
        self.app.db.delete_budget_limit(self.app.current_user["id"], cat)
        self._switch("budgets")

    # ============================================================ RECURRING
    def _show_recurring(self):
        f = self.content
        uid = self.app.current_user["id"]
        try: self.app.db.process_recurring(uid)
        except: pass

        add = ctk.CTkFrame(f, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        add.pack(fill="x", padx=PAD_R, pady=(0, 21))
        ctk.CTkLabel(add, text="Programmer un transfert automatique", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT).pack(padx=21, pady=(21, 13), anchor="w")

        row = ctk.CTkFrame(add, fg_color="transparent")
        row.pack(fill="x", padx=21, pady=(0, 21))

        self.rec_desc = ctk.CTkEntry(row, height=42, width=150, corner_radius=13, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, placeholder_text="Description", font=("Segoe UI", 13))
        self.rec_desc.pack(side="left", padx=(0, 8))
        self.rec_amount = ctk.CTkEntry(row, height=42, width=100, corner_radius=13, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, placeholder_text="Montant", font=("Segoe UI", 13))
        self.rec_amount.pack(side="left", padx=(0, 8))
        self.rec_email = ctk.CTkEntry(row, height=42, width=180, corner_radius=13, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, placeholder_text="E-mail destinataire", font=("Segoe UI", 13))
        self.rec_email.pack(side="left", padx=(0, 8))
        self.rec_freq = ctk.StringVar(value="Mensuel")
        ctk.CTkOptionMenu(row, variable=self.rec_freq, values=["Hebdo", "Mensuel", "Annuel"], width=100, height=42, font=("Segoe UI", 13), **DD).pack(side="left", padx=(0, 8))
        self.rec_date = DatePickerButton(row, width=130, height=42, placeholder="Date debut")
        self.rec_date.pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="Ajouter", width=90, height=42, corner_radius=13, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="white", font=("Segoe UI", 13, "bold"), command=self._add_recurring).pack(side="left")

        recs = self.app.db.get_recurring(uid)
        if recs:
            lc = ctk.CTkFrame(f, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
            lc.pack(fill="x", padx=PAD_R)
            ctk.CTkLabel(lc, text="Transferts automatiques actifs", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT).pack(padx=21, pady=(21, 13), anchor="w")
            freq_lbl = {"weekly": "Hebdo", "monthly": "Mensuel", "yearly": "Annuel"}
            for rec in recs:
                rr = ctk.CTkFrame(lc, fg_color=COLOR_BG_INPUT, corner_radius=13)
                rr.pack(fill="x", padx=13, pady=4)
                ri = ctk.CTkFrame(rr, fg_color="transparent")
                ri.pack(fill="x", padx=13, pady=13)
                # Get recipient name
                dest_text = ""
                if rec.get("recipient_id"):
                    dest = self.app.db.get_user_by_id(rec["recipient_id"])
                    if dest:
                        dest_text = f" vers {dest['first_name']} {dest['last_name']} |"
                ctk.CTkLabel(ri, text=rec["description"], font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT).pack(side="left")
                ctk.CTkLabel(ri, text=f"{format_currency(float(rec['amount']))}{dest_text} | {freq_lbl.get(rec['frequency'], '')} | Prochain : {rec['next_date']}", font=("Segoe UI", 13), text_color=COLOR_PRIMARY).pack(side="left", padx=(13, 0))
                ctk.CTkButton(ri, text="X", width=28, height=28, corner_radius=8, fg_color=COLOR_DANGER_LIGHT, hover_color=COLOR_DANGER, text_color=COLOR_DANGER, font=("Segoe UI", 13), command=lambda rid=rec["id"]: self._del_recurring(rid)).pack(side="right")
            ctk.CTkFrame(lc, height=8, fg_color="transparent").pack()
        else:
            ctk.CTkLabel(f, text="Aucun transfert automatique configuré.", font=("Segoe UI", 14), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=13)

    def _add_recurring(self):
        try: amount = float(self.rec_amount.get().replace(",", "."))
        except ValueError: messagebox.showerror("Erreur", "Montant invalide."); return
        if amount <= 0: messagebox.showerror("Erreur", "Positif requis."); return
        desc = self.rec_desc.get().strip()
        if not desc: messagebox.showerror("Erreur", "Description requise."); return
        email = self.rec_email.get().strip()
        if not email: messagebox.showerror("Erreur", "E-mail destinataire requis."); return
        recipient = self.app.db.get_user_by_email(email)
        if not recipient: messagebox.showerror("Erreur", "Destinataire introuvable."); return
        if recipient["id"] == self.app.current_user["id"]: messagebox.showerror("Erreur", "Transfert vers soi impossible."); return
        freq_map = {"Hebdo": "weekly", "Mensuel": "monthly", "Annuel": "yearly"}
        next_date = self.rec_date.get().strip() or date.today().isoformat()
        self.app.db.add_recurring(self.app.current_user["id"], desc, amount, "transfer", "autre", freq_map.get(self.rec_freq.get(), "monthly"), next_date, recipient["id"])
        self._switch("recurring")

    def _del_recurring(self, rid):
        self.app.db.delete_recurring(rid)
        self._switch("recurring")

    # ============================================================ EXPORT
    def _show_export(self):
        f = self.content
        user = self.app.current_user
        txs = self.app.db.get_transactions(user["id"])
        total_dep = sum(float(t["amount"]) for t in txs if t["type"] == "deposit")
        total_exp = sum(float(t["amount"]) for t in txs if t["type"] in ("withdrawal", "transfer"))

        # Summary + export in one card
        card = ctk.CTkFrame(f, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="x", padx=PAD_R)

        ctk.CTkLabel(card, text="Exporter vos données", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT).pack(padx=21, pady=(21, 8), anchor="w")
        ctk.CTkLabel(card, text="Téléchargez l'historique au format CSV. Compatible Excel, Sheets, LibreOffice.", font=("Segoe UI", 14), text_color=COLOR_TEXT_DIM).pack(padx=21, anchor="w")

        # Quick stats row
        sr = ctk.CTkFrame(card, fg_color="transparent")
        sr.pack(fill="x", padx=21, pady=(21, 0))
        sr.columnconfigure((0, 1, 2), weight=1)

        for i, (label, val, bg, color) in enumerate([
            ("Transactions", str(len(txs)), COLOR_BG_INPUT, COLOR_TEXT),
            ("Revenus", format_currency(total_dep), COLOR_BG_INPUT, COLOR_SUCCESS),
            ("Dépenses", format_currency(total_exp), COLOR_BG_INPUT, COLOR_ACCENT),
        ]):
            sc = ctk.CTkFrame(sr, fg_color=bg, corner_radius=13)
            sc.grid(row=0, column=i, padx=(0, 8) if i < 2 else 0, sticky="nsew")
            ctk.CTkLabel(sc, text=label, font=("Segoe UI", 12), text_color=COLOR_TEXT_DIM).pack(padx=13, pady=(13, 0), anchor="w")
            ctk.CTkLabel(sc, text=val, font=("Segoe UI", 18, "bold"), text_color=color).pack(padx=13, pady=(4, 13), anchor="w")

        ctk.CTkButton(card, text="Exporter en CSV", width=200, height=44, corner_radius=13, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="white", font=("Segoe UI", 14, "bold"), command=self._export_csv).pack(padx=21, pady=21, anchor="w")

    def _export_csv(self):
        fp = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile=f"budget_buddy_{datetime.now().strftime('%Y%m%d')}.csv")
        if fp:
            self.app.db.export_transactions_csv(self.app.current_user["id"], fp)
            messagebox.showinfo("Succès", f"Export terminé.\n{fp}")

    # ============================================================ PROFILE
    def _show_profile(self):
        f = self.content
        user = self.app.current_user
        is_banker = user["role"] == "banker"

        card = ctk.CTkFrame(f, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="x", padx=PAD_R)

        # Avatar + info
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=21, pady=21)

        avatar = ctk.CTkFrame(top, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=30, width=60, height=60)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=f"{user['first_name'][0]}{user['last_name'][0]}".upper(), font=("Segoe UI", 20, "bold"), text_color=COLOR_PRIMARY).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(top, fg_color="transparent")
        info.pack(side="left", padx=(13, 0))
        ctk.CTkLabel(info, text=f"{user['first_name']} {user['last_name']}", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT).pack(anchor="w")
        role_text = "Banquier" if is_banker else "Client"
        ctk.CTkLabel(info, text=f"{user['email']}  |  {role_text}  |  Membre depuis {user['created_at'].strftime('%d/%m/%Y')}", font=("Segoe UI", 13), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(2, 0))

        # Stats only for clients
        if not is_banker:
            txs = self.app.db.get_transactions(user["id"])
            total_dep = sum(float(t["amount"]) for t in txs if t["type"] == "deposit")
            total_exp = sum(float(t["amount"]) for t in txs if t["type"] in ("withdrawal", "transfer"))

            ctk.CTkFrame(card, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=21)

            ctk.CTkLabel(card, text="Statistiques", font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT).pack(padx=21, anchor="w", pady=(21, 13))

            sg = ctk.CTkFrame(card, fg_color="transparent")
            sg.pack(fill="x", padx=21, pady=(0, 21))
            sg.columnconfigure((0, 1, 2, 3), weight=1)

            for i, (label, val, color) in enumerate([
                ("Transactions", str(len(txs)), COLOR_TEXT),
                ("Revenus", format_currency(total_dep), COLOR_SUCCESS),
                ("Dépenses", format_currency(total_exp), COLOR_ACCENT),
                ("Solde", format_currency(float(user["balance"])), COLOR_TEXT),
            ]):
                sc = ctk.CTkFrame(sg, fg_color=COLOR_BG_INPUT, corner_radius=13)
                sc.grid(row=0, column=i, padx=(0, 8) if i < 3 else 0, sticky="nsew")
                ctk.CTkLabel(sc, text=label, font=("Segoe UI", 12), text_color=COLOR_TEXT_DIM).pack(padx=13, pady=(13, 0), anchor="w")
                ctk.CTkLabel(sc, text=val, font=("Segoe UI", 16, "bold"), text_color=color).pack(padx=13, pady=(4, 13), anchor="w")
