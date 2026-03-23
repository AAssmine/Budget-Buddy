import customtkinter as ctk
from config import *
from utils.helpers import format_currency
from tkinter import messagebox

DD = dict(corner_radius=13, fg_color="#e8e8e2", button_color="#e8e8e2", button_hover_color="#deded4", dropdown_fg_color="#ebebdf", dropdown_hover_color="#deded4", text_color=COLOR_TEXT)


class BankerView(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_BG_DARK)
        self.app = app
        self.selected_client = None
        self._build()

    def _build(self):
        # Header
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=44, pady=(21, 21))
        ctk.CTkLabel(top, text="Espace Banquier", font=("Segoe UI", 30, "bold"), text_color=COLOR_TEXT).pack(side="left")

        # Two panels side by side using pack
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=44, pady=(0, 21))

        # Left: client list (fixed width)
        left = ctk.CTkFrame(body, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER, width=300)
        left.pack(side="left", fill="y", padx=(0, 13))
        left.pack_propagate(False)

        lh = ctk.CTkFrame(left, fg_color="transparent")
        lh.pack(fill="x", padx=21, pady=(21, 13))
        ctk.CTkLabel(lh, text="Mes clients", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT).pack(side="left")
        ctk.CTkButton(lh, text="+ Ajouter", width=90, height=34, corner_radius=13, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="white", font=("Segoe UI", 13, "bold"), command=self._add_dialog).pack(side="right")

        self.client_list = ctk.CTkScrollableFrame(left, fg_color="transparent", scrollbar_button_color="#d6d6cf", scrollbar_button_hover_color="#c0c0b8", scrollbar_fg_color="transparent")
        self.client_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.client_list._scrollbar.configure(width=5, corner_radius=3)

        # Right: detail panel (fills remaining space)
        self.right_card = ctk.CTkFrame(body, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        self.right_card.pack(side="left", fill="both", expand=True)
        self.detail = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.detail.pack(fill="both", expand=True, padx=21, pady=21)

        self._refresh_clients()
        self._placeholder()

    def _refresh_clients(self):
        for w in self.client_list.winfo_children(): w.destroy()
        clients = self.app.db.get_clients_of_banker(self.app.current_user["id"])
        if not clients:
            ctk.CTkLabel(self.client_list, text="Aucun client.", font=("Segoe UI", 14), text_color=COLOR_TEXT_DIM).pack(pady=34)
            return
        for c in clients:
            sel = self.selected_client and self.selected_client["id"] == c["id"]
            bg = COLOR_PRIMARY_LIGHT if sel else "transparent"
            row = ctk.CTkFrame(self.client_list, fg_color=COLOR_PRIMARY_LIGHT if sel else COLOR_BG_INPUT, corner_radius=10, cursor="hand2", border_width=1, border_color=COLOR_PRIMARY if sel else COLOR_BORDER)
            row.pack(fill="x", pady=3)
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=13, pady=13)
            balance = float(c["balance"])
            color = COLOR_SUCCESS if balance >= 0 else COLOR_DANGER
            ctk.CTkLabel(inner, text=f"{c['first_name']} {c['last_name']}", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT).pack(anchor="w")
            ctk.CTkLabel(inner, text=f"{format_currency(balance)}", font=("Segoe UI", 13), text_color=color).pack(anchor="w")
            for w in [row, inner] + inner.winfo_children():
                w.bind("<Button-1>", lambda e, cl=c: self._select(cl))

    def _placeholder(self):
        for w in self.detail.winfo_children(): w.destroy()
        ctk.CTkLabel(self.detail, text="Sélectionnez un client dans la liste.", font=("Segoe UI", 16), text_color=COLOR_TEXT_DIM).place(relx=0.5, rely=0.5, anchor="center")

    def _select(self, client):
        self.selected_client = client
        self._refresh_clients()
        self._show_detail(client)

    def _show_detail(self, client):
        for w in self.detail.winfo_children(): w.destroy()

        # Client name + remove button
        hdr = ctk.CTkFrame(self.detail, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 21))
        ctk.CTkLabel(hdr, text=f"{client['first_name']} {client['last_name']}", font=("Segoe UI", 22, "bold"), text_color=COLOR_TEXT).pack(side="left")
        ctk.CTkButton(hdr, text="Retirer", width=80, height=34, corner_radius=10, fg_color=COLOR_DANGER_LIGHT, hover_color=COLOR_DANGER, text_color=COLOR_DANGER, font=("Segoe UI", 13, "bold"), command=lambda: self._remove(client)).pack(side="right")

        # Balance + email
        balance = self.app.db.get_balance(client["id"])
        bal_color = COLOR_SUCCESS if balance >= 0 else COLOR_DANGER
        info = ctk.CTkFrame(self.detail, fg_color=COLOR_BG_INPUT, corner_radius=13)
        info.pack(fill="x", pady=(0, 21))
        ii = ctk.CTkFrame(info, fg_color="transparent")
        ii.pack(fill="x", padx=21, pady=16)
        ctk.CTkLabel(ii, text=f"Solde : {format_currency(balance)}", font=("Segoe UI", 20, "bold"), text_color=bal_color).pack(side="left")
        ctk.CTkLabel(ii, text=client["email"], font=("Segoe UI", 13), text_color=COLOR_TEXT_DIM).pack(side="right")

        # Action buttons
        acts = ctk.CTkFrame(self.detail, fg_color="transparent")
        acts.pack(fill="x", pady=(0, 21))
        ctk.CTkButton(acts, text="Dépôt", height=40, corner_radius=13, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, text_color="white", font=("Segoe UI", 14, "bold"), command=lambda: self._op(client, "deposit")).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkButton(acts, text="Retrait", height=40, corner_radius=13, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="white", font=("Segoe UI", 14, "bold"), command=lambda: self._op(client, "withdrawal")).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkButton(acts, text="Transfert", height=40, corner_radius=13, fg_color=COLOR_BG_CARD, hover_color=COLOR_BG_INPUT, text_color=COLOR_TEXT, border_width=1, border_color=COLOR_BORDER, font=("Segoe UI", 14, "bold"), command=lambda: self._op(client, "transfer")).pack(side="left", expand=True, fill="x")

        # Recent transactions
        ctk.CTkLabel(self.detail, text="Historique récent", font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT).pack(anchor="w", pady=(0, 13))
        txs = self.app.db.get_recent_transactions(client["id"], 10)
        if not txs:
            ctk.CTkLabel(self.detail, text="Aucune transaction.", font=("Segoe UI", 14), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=8)
        else:
            tx_scroll = ctk.CTkScrollableFrame(self.detail, fg_color="transparent", scrollbar_button_color="#d6d6cf", scrollbar_fg_color="transparent")
            tx_scroll.pack(fill="both", expand=True)
            tx_scroll._scrollbar.configure(width=5, corner_radius=3)
            for i, tx in enumerate(txs):
                bg = COLOR_BG_INPUT if i % 2 == 0 else "transparent"
                r = ctk.CTkFrame(tx_scroll, fg_color=bg, corner_radius=8)
                r.pack(fill="x", pady=2)
                ri = ctk.CTkFrame(r, fg_color="transparent")
                ri.pack(fill="x", padx=13, pady=10)
                amount = float(tx["amount"])
                c, s = (COLOR_SUCCESS, "+") if tx["type"] == "deposit" else (COLOR_ACCENT, "-")
                left_tx = ctk.CTkFrame(ri, fg_color="transparent")
                left_tx.pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(left_tx, text=tx["description"], font=("Segoe UI", 14), text_color=COLOR_TEXT).pack(anchor="w")
                ctk.CTkLabel(left_tx, text=f"{TYPE_LABELS.get(tx['type'], '')}  |  {tx['date'].strftime('%d/%m/%Y')}", font=("Segoe UI", 12), text_color=COLOR_TEXT_DIM).pack(anchor="w")
                ctk.CTkLabel(ri, text=f"{s}{amount:,.2f} EUR".replace(",", " ").replace(".", ","), font=("Segoe UI", 14, "bold"), text_color=c).pack(side="right")

    def _add_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Ajouter un client")
        win.geometry("580x480")
        win.configure(fg_color=COLOR_BG_DARK)
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="Rechercher un client", font=("Segoe UI", 22, "bold"), text_color=COLOR_TEXT).pack(pady=(34, 21))
        se = ctk.CTkEntry(win, height=46, corner_radius=13, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, placeholder_text="Nom ou e-mail...", font=("Segoe UI", 14), width=380)
        se.pack(padx=55)
        res = ctk.CTkScrollableFrame(win, fg_color="transparent", height=160)
        res.pack(fill="both", expand=True, padx=55, pady=21)

        def search(e=None):
            for w in res.winfo_children(): w.destroy()
            q = se.get().strip()
            if len(q) < 2: return
            for r in self.app.db.search_clients(q):
                rf = ctk.CTkFrame(res, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
                rf.pack(fill="x", pady=4)
                ctk.CTkLabel(rf, text=f"{r['first_name']} {r['last_name']} - {r['email']}", font=("Segoe UI", 14), text_color=COLOR_TEXT).pack(side="left", padx=16, pady=13)
                ctk.CTkButton(rf, text="Ajouter", width=80, height=34, corner_radius=10, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="white", font=("Segoe UI", 13, "bold"), command=lambda c=r: self._assign(c, win)).pack(side="right", padx=13)
        se.bind("<KeyRelease>", search)

    def _assign(self, client, win):
        self.app.db.assign_client_to_banker(client["id"], self.app.current_user["id"])
        win.destroy()
        self._refresh_clients()

    def _remove(self, client):
        if messagebox.askyesno("Confirmer", f"Retirer {client['first_name']} {client['last_name']} ?"):
            self.app.db.unassign_client(client["id"])
            self.selected_client = None
            self._refresh_clients()
            self._placeholder()

    def _op(self, client, op_type):
        win = ctk.CTkToplevel(self)
        win.configure(fg_color=COLOR_BG_DARK)
        win.attributes("-topmost", True)
        titles = {"deposit": "Dépôt", "withdrawal": "Retrait", "transfer": "Transfert"}
        win.title(f"{titles[op_type]} pour {client['first_name']}")
        win.geometry("640x670" if op_type != "transfer" else "640x750")

        ctk.CTkLabel(win, text=f"{titles[op_type]} pour le client", font=("Segoe UI", 22, "bold"), text_color=COLOR_TEXT).pack(pady=(55, 4))
        ctk.CTkLabel(win, text=f"{client['first_name']} {client['last_name']}", font=("Segoe UI", 15), text_color=COLOR_TEXT_DIM).pack(pady=(0, 21))
        ctk.CTkFrame(win, fg_color=COLOR_ACCENT, height=4, width=55, corner_radius=2).pack(pady=(0, 21))

        form = ctk.CTkFrame(win, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        form.pack(fill="x", padx=55)
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(padx=34, pady=34)

        ctk.CTkLabel(inner, text="MONTANT (EUR)", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 8))
        ae = ctk.CTkEntry(inner, height=50, corner_radius=13, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, font=("Segoe UI", 16), width=400)
        ae.pack(fill="x", pady=(0, 21))
        ctk.CTkLabel(inner, text="DESCRIPTION", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 8))
        de = ctk.CTkEntry(inner, height=50, corner_radius=13, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, font=("Segoe UI", 14), width=400)
        de.pack(fill="x", pady=(0, 21))

        re_e = None
        if op_type == "transfer":
            ctk.CTkLabel(inner, text="E-MAIL DESTINATAIRE", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 8))
            re_e = ctk.CTkEntry(inner, height=50, corner_radius=13, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, font=("Segoe UI", 14), width=400)
            re_e.pack(fill="x", pady=(0, 21))

        err = ctk.CTkLabel(inner, text="", font=("Segoe UI", 13), text_color=COLOR_DANGER, wraplength=380)
        err.pack(fill="x")
        btn_c = {"deposit": COLOR_PRIMARY, "withdrawal": COLOR_ACCENT, "transfer": COLOR_PRIMARY}

        def execute():
            try: amount = float(ae.get().replace(",", "."))
            except ValueError: err.configure(text="Montant invalide."); return
            if amount <= 0: err.configure(text="Positif requis."); return
            desc = de.get().strip() or "Opération banquier"
            cid = client["id"]
            try:
                if op_type == "deposit": self.app.db.deposit(cid, amount, desc)
                elif op_type == "withdrawal": self.app.db.withdraw(cid, amount, desc)
                elif op_type == "transfer":
                    rec = self.app.db.get_user_by_email(re_e.get().strip())
                    if not rec: err.configure(text="Introuvable."); return
                    self.app.db.transfer(cid, rec["id"], amount, desc)
                win.destroy()
                self._select(self.app.db.get_user_by_id(cid))
                self._refresh_clients()
            except Exception as e: err.configure(text=f"Erreur : {e}")

        ctk.CTkButton(inner, text="Confirmer", height=50, corner_radius=13, fg_color=btn_c[op_type], hover_color=COLOR_PRIMARY_HOVER, text_color="white", font=("Segoe UI", 16, "bold"), command=execute).pack(fill="x", pady=(13, 0))
