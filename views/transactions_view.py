import customtkinter as ctk
from config import *
from utils.helpers import format_currency, DatePickerButton
from tkinter import messagebox

# Golden ratio spacing: 8, 13, 21, 34, 55
# Dropdown style constants
DD_BG = "#e8e8e2"
DD_ARROW = "#c5c5bb"
DD_ARROW_HOVER = "#b0b0a6"
DD_MENU_BG = "#ebebdf"
DD_MENU_HOVER = "#deded4"
DD_RADIUS = 13


class TransactionsView(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_BG_DARK)
        self.app = app
        self._build()

    def _build(self):
        # -- Header
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=44, pady=(21, 21))

        left_top = ctk.CTkFrame(top, fg_color="transparent")
        left_top.pack(side="left")
        ctk.CTkLabel(left_top, text="Transactions", font=("Segoe UI", 30, "bold"), text_color=COLOR_TEXT).pack(anchor="w")
        ctk.CTkLabel(left_top, text="Gerez vos operations financieres.", font=("Segoe UI", 15), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(8, 0))

        btn_f = ctk.CTkFrame(top, fg_color="transparent")
        btn_f.pack(side="right")
        ctk.CTkButton(btn_f, text="Depot", width=110, height=44, corner_radius=DD_RADIUS, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, text_color="white", font=("Segoe UI", 15, "bold"), command=lambda: self._open_op("deposit")).pack(side="left", padx=(0, 13))
        ctk.CTkButton(btn_f, text="Retrait", width=110, height=44, corner_radius=DD_RADIUS, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="white", font=("Segoe UI", 15, "bold"), command=lambda: self._open_op("withdrawal")).pack(side="left", padx=(0, 13))
        ctk.CTkButton(btn_f, text="Transfert", width=120, height=44, corner_radius=DD_RADIUS, fg_color=COLOR_BG_CARD, hover_color=COLOR_BG_INPUT, text_color=COLOR_TEXT, border_width=1, border_color=COLOR_BORDER, font=("Segoe UI", 15, "bold"), command=lambda: self._open_op("transfer")).pack(side="left")

        # -- Filters: all on one row
        fc = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=DD_RADIUS, border_width=1, border_color=COLOR_BORDER)
        fc.pack(fill="x", padx=(44, 44), pady=(0, 21))

        row = ctk.CTkFrame(fc, fg_color="transparent")
        row.pack(fill="x", padx=21, pady=21)

        self.date_start = DatePickerButton(row, width=130, height=42, placeholder="Date debut")
        self.date_start.pack(side="left", padx=(0, 8))

        self.date_end = DatePickerButton(row, width=130, height=42, placeholder="Date fin")
        self.date_end.pack(side="left", padx=(0, 13))

        self.cat_var = ctk.StringVar(value="Toutes")
        ctk.CTkOptionMenu(row, variable=self.cat_var, values=["Toutes"] + [c.capitalize() for c in CATEGORIES], width=130, height=42, corner_radius=13, fg_color="#e8e8e2", button_color="#e8e8e2", button_hover_color="#deded4", dropdown_fg_color="#ebebdf", dropdown_hover_color="#deded4", text_color=COLOR_TEXT, font=("Segoe UI", 13)).pack(side="left", padx=(0, 8))

        self.type_var = ctk.StringVar(value="Tous")
        ctk.CTkOptionMenu(row, variable=self.type_var, values=["Tous", "Depot", "Retrait", "Transfert"], width=110, height=42, corner_radius=13, fg_color="#e8e8e2", button_color="#e8e8e2", button_hover_color="#deded4", dropdown_fg_color="#ebebdf", dropdown_hover_color="#deded4", text_color=COLOR_TEXT, font=("Segoe UI", 13)).pack(side="left", padx=(0, 8))

        self.sort_var = ctk.StringVar(value="Date")
        ctk.CTkOptionMenu(row, variable=self.sort_var, values=["Date", "Montant +", "Montant -"], width=110, height=42, corner_radius=13, fg_color="#e8e8e2", button_color="#e8e8e2", button_hover_color="#deded4", dropdown_fg_color="#ebebdf", dropdown_hover_color="#deded4", text_color=COLOR_TEXT, font=("Segoe UI", 13)).pack(side="left", padx=(0, 13))

        ctk.CTkButton(row, text="Filtrer", width=90, height=42, corner_radius=DD_RADIUS, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, text_color="white", font=("Segoe UI", 14, "bold"), command=self._refresh).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="X", width=42, height=42, corner_radius=DD_RADIUS, fg_color=DD_BG, hover_color=COLOR_BORDER, text_color=COLOR_TEXT_DIM, font=("Segoe UI", 14), command=self._reset_filters).pack(side="left")

        # -- Transaction list
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#d6d6cf", scrollbar_button_hover_color="#c0c0b8", scrollbar_fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=(44, 0), pady=(0, 13))
        self.list_frame._scrollbar.configure(width=6, corner_radius=3)
        self._refresh()

    def _build_filters(self):
        f = {}
        ds = self.date_start.get().strip()
        de = self.date_end.get().strip()
        if ds: f["date_start"] = ds
        if de: f["date_end"] = de
        cat = self.cat_var.get()
        if cat != "Toutes": f["category"] = cat.lower()
        tp = self.type_var.get()
        m = {"Depot": "deposit", "Retrait": "withdrawal", "Transfert": "transfer"}
        if tp in m: f["tx_type"] = m[tp]
        s = self.sort_var.get()
        if s == "Montant +": f["sort_amount"] = "asc"
        elif s == "Montant -": f["sort_amount"] = "desc"
        return f

    def _refresh(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        txs = self.app.db.get_transactions(self.app.current_user["id"], self._build_filters() or None)

        if not txs:
            ctk.CTkLabel(self.list_frame, text="Aucune transaction trouvee.", font=("Segoe UI", 17), text_color=COLOR_TEXT_DIM).pack(pady=55, padx=(0, 44))
            return

        # Table header
        hdr = ctk.CTkFrame(self.list_frame, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=DD_RADIUS, height=48)
        hdr.pack(fill="x", pady=(0, 8), padx=(0, 44))
        hdr.pack_propagate(False)
        cols = [("Ref.", 0.13), ("Description", 0.27), ("Categorie", 0.13), ("Type", 0.11), ("Date", 0.16), ("Montant", 0.20)]
        xoff = 0
        for label, w in cols:
            ctk.CTkLabel(hdr, text=label, font=("Segoe UI", 14, "bold"), text_color=COLOR_PRIMARY, anchor="w").place(relx=xoff, rely=0.5, anchor="w", relwidth=w, x=18)
            xoff += w

        for i, tx in enumerate(txs):
            self._tx_row(tx, COLOR_BG_INPUT if i % 2 == 0 else COLOR_BG_CARD)

    def _tx_row(self, tx, bg):
        amount = float(tx["amount"])
        color, sign = (COLOR_SUCCESS, "+") if tx["type"] == "deposit" else (COLOR_ACCENT, "-")
        row = ctk.CTkFrame(self.list_frame, fg_color=bg, corner_radius=8, height=55)
        row.pack(fill="x", pady=3, padx=(0, 44))
        row.pack_propagate(False)
        data = [
            (tx["reference"], COLOR_TEXT_DIM, "normal"),
            (tx["description"], COLOR_TEXT, "normal"),
            (tx["category"].capitalize(), COLOR_TEXT, "normal"),
            (TYPE_LABELS.get(tx["type"], ""), COLOR_TEXT_DIM, "normal"),
            (tx["date"].strftime("%d/%m/%Y %H:%M"), COLOR_TEXT_DIM, "normal"),
            (f"{sign}{amount:,.2f} EUR".replace(",", " ").replace(".", ","), color, "bold"),
        ]
        widths = [0.13, 0.27, 0.13, 0.11, 0.16, 0.20]
        xoff = 0
        for (text, tc, wt), w in zip(data, widths):
            ctk.CTkLabel(row, text=text, font=("Segoe UI", 14, wt), text_color=tc, anchor="w").place(relx=xoff, rely=0.5, anchor="w", relwidth=w, x=18)
            xoff += w

    def _reset_filters(self):
        self.date_start.clear()
        self.date_end.clear()
        self.cat_var.set("Toutes")
        self.type_var.set("Tous")
        self.sort_var.set("Date")
        self._refresh()

    def _open_op(self, op_type):
        win = ctk.CTkToplevel(self)
        win.configure(fg_color=COLOR_BG_DARK)
        win.attributes("-topmost", True)
        titles = {"deposit": "Effectuer un depot", "withdrawal": "Effectuer un retrait", "transfer": "Effectuer un transfert"}
        win.title(titles[op_type])
        win.geometry("640x750" if op_type == "transfer" else "640x670")

        ctk.CTkLabel(win, text=titles[op_type], font=("Segoe UI", 24, "bold"), text_color=COLOR_TEXT).pack(pady=(55, 8))
        ctk.CTkFrame(win, fg_color=COLOR_ACCENT, height=4, width=55, corner_radius=2).pack(pady=(0, 34))

        form = ctk.CTkFrame(win, fg_color=COLOR_BG_CARD, corner_radius=DD_RADIUS, border_width=1, border_color=COLOR_BORDER)
        form.pack(fill="x", padx=55)
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(padx=34, pady=34)

        ctk.CTkLabel(inner, text="MONTANT (EUR)", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 8))
        amount_e = ctk.CTkEntry(inner, height=55, corner_radius=DD_RADIUS, fg_color=DD_BG, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, placeholder_text="0.00", font=("Segoe UI", 18), width=460)
        amount_e.pack(fill="x", pady=(0, 21))

        ctk.CTkLabel(inner, text="DESCRIPTION", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 8))
        desc_e = ctk.CTkEntry(inner, height=52, corner_radius=DD_RADIUS, fg_color=DD_BG, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, placeholder_text="Ex: Salaire, Courses...", font=("Segoe UI", 16), width=460)
        desc_e.pack(fill="x", pady=(0, 21))

        ctk.CTkLabel(inner, text="CATEGORIE", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 8))
        cat_var = ctk.StringVar(value="Autre")
        ctk.CTkOptionMenu(inner, variable=cat_var, values=[c.capitalize() for c in CATEGORIES], width=460, height=50, corner_radius=13, fg_color="#e8e8e2", button_color="#e8e8e2", button_hover_color="#deded4", dropdown_fg_color="#ebebdf", dropdown_hover_color="#deded4", text_color=COLOR_TEXT, font=("Segoe UI", 16)).pack(fill="x", pady=(0, 21))

        rec_e = None
        if op_type == "transfer":
            ctk.CTkLabel(inner, text="E-MAIL DESTINATAIRE", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 8))
            rec_e = ctk.CTkEntry(inner, height=52, corner_radius=DD_RADIUS, fg_color=DD_BG, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, placeholder_text="destinataire@email.com", font=("Segoe UI", 16), width=460)
            rec_e.pack(fill="x", pady=(0, 21))

        err = ctk.CTkLabel(inner, text="", font=("Segoe UI", 14), text_color=COLOR_DANGER, wraplength=420)
        err.pack(fill="x")
        btn_c = {"deposit": COLOR_PRIMARY, "withdrawal": COLOR_ACCENT, "transfer": COLOR_PRIMARY}

        def execute():
            try: amount = float(amount_e.get().replace(",", "."))
            except ValueError: err.configure(text="Montant invalide."); return
            if amount <= 0: err.configure(text="Positif requis."); return
            desc = desc_e.get().strip() or titles[op_type]
            cat = cat_var.get().lower()
            uid = self.app.current_user["id"]
            try:
                if op_type == "deposit": ref = self.app.db.deposit(uid, amount, desc, cat)
                elif op_type == "withdrawal":
                    if amount > self.app.db.get_balance(uid) + 500: err.configure(text="Fonds insuffisants."); return
                    ref = self.app.db.withdraw(uid, amount, desc, cat)
                elif op_type == "transfer":
                    rec_email = rec_e.get().strip()
                    if not rec_email: err.configure(text="E-mail requis."); return
                    recipient = self.app.db.get_user_by_email(rec_email)
                    if not recipient: err.configure(text="Introuvable."); return
                    if recipient["id"] == uid: err.configure(text="Transfert vers soi impossible."); return
                    if amount > self.app.db.get_balance(uid) + 500: err.configure(text="Fonds insuffisants."); return
                    ref = self.app.db.transfer(uid, recipient["id"], amount, desc)
                self.app.current_user = self.app.db.get_user_by_id(uid)
                win.destroy(); self._refresh()
                messagebox.showinfo("Succes", f"Reference : {ref}")
            except Exception as e: err.configure(text=f"Erreur : {e}")

        ctk.CTkButton(inner, text="Confirmer", height=55, corner_radius=DD_RADIUS, fg_color=btn_c[op_type], hover_color=COLOR_PRIMARY_HOVER, text_color="white", font=("Segoe UI", 18, "bold"), command=execute).pack(fill="x", pady=(13, 0))
