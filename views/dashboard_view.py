import customtkinter as ctk
from config import *
from utils.helpers import format_currency, MONTH_NAMES
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# Golden ratio spacing: 8, 13, 21, 34, 55
BG_CHART = "#f2f2ed"


class DashboardView(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_BG_DARK)
        self.app = app
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#d6d6cf", scrollbar_button_hover_color="#c0c0b8", scrollbar_fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=(44, 0), pady=21)
        scroll._scrollbar.configure(width=6, corner_radius=3)

        user = self.app.current_user
        balance = self.app.db.get_balance(user["id"])
        monthly = self.app.db.get_monthly_summary(user["id"])
        cm = datetime.now().month
        dep_m, exp_m = 0.0, 0.0
        for m in monthly:
            if m["month"] == cm:
                dep_m = float(m["deposits"] or 0)
                exp_m = float(m["expenses"] or 0)

        # -- Header: greeting + balance card
        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 34), padx=(0, 21))

        left_hdr = ctk.CTkFrame(hdr, fg_color="transparent")
        left_hdr.pack(side="left")
        ctk.CTkLabel(left_hdr, text=f"Bonjour, {user['first_name']}",
                     font=("Segoe UI", 32, "bold"), text_color=COLOR_TEXT).pack(anchor="w")
        ctk.CTkLabel(left_hdr, text="Voici un aperçu de vos finances.",
                     font=("Segoe UI", 16), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(8, 0))

        bal_card = ctk.CTkFrame(hdr, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=13)
        bal_card.pack(side="right")
        bi = ctk.CTkFrame(bal_card, fg_color="transparent")
        bi.pack(padx=34, pady=21)
        ctk.CTkLabel(bi, text="Solde actuel", font=("Segoe UI", 14), text_color=COLOR_PRIMARY).pack(anchor="e")
        ctk.CTkLabel(bi, text=format_currency(balance), font=("Segoe UI", 30, "bold"),
                     text_color=COLOR_PRIMARY if balance >= 0 else COLOR_DANGER).pack(anchor="e", pady=(8, 0))

        # -- Alerts
        if balance < 0:
            self._alert(scroll, "Alerte découvert -- Votre solde est négatif.", COLOR_DANGER_LIGHT, COLOR_DANGER)
        elif balance < 100:
            self._alert(scroll, "Solde bas -- Inférieur à 100 EUR.", COLOR_WARNING_LIGHT, COLOR_WARNING)

        # -- Stats row
        stats = ctk.CTkFrame(scroll, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 34), padx=(0, 21))
        stats.columnconfigure((0, 1, 2), weight=1)

        self._stat_card(stats, "Revenus ce mois", format_currency(dep_m), COLOR_SUCCESS_LIGHT, COLOR_SUCCESS, 0)
        self._stat_card(stats, "Dépenses ce mois", format_currency(exp_m), COLOR_ACCENT_LIGHT, COLOR_ACCENT, 1)

        unread = self.app.db.count_unread_notifications(user["id"])
        nc = ctk.CTkFrame(stats, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        nc.grid(row=0, column=2, padx=8, sticky="nsew")
        nci = ctk.CTkFrame(nc, fg_color="transparent")
        nci.pack(padx=21, pady=21, fill="both", expand=True)
        ctk.CTkLabel(nci, text="Notifications", font=("Segoe UI", 15), text_color=COLOR_TEXT_DIM).pack(anchor="w")
        ctk.CTkLabel(nci, text=str(unread), font=("Segoe UI", 30, "bold"),
                     text_color=COLOR_ACCENT if unread > 0 else COLOR_TEXT_DIM).pack(anchor="w", pady=(8, 8))
        ctk.CTkButton(nci, text="Consulter", height=36, corner_radius=8,
                      fg_color=COLOR_ACCENT if unread > 0 else COLOR_BG_INPUT,
                      hover_color=COLOR_ACCENT_HOVER,
                      text_color="white" if unread > 0 else COLOR_TEXT_DIM,
                      font=("Segoe UI", 14, "bold"), command=self._show_notifications).pack(anchor="w")

        # -- Charts
        charts = ctk.CTkFrame(scroll, fg_color="transparent")
        charts.pack(fill="x", pady=(0, 34), padx=(0, 21))
        charts.columnconfigure(0, weight=3)
        charts.columnconfigure(1, weight=2)
        self._monthly_chart(charts, monthly, 0, 0)
        self._category_chart(charts, user["id"], 0, 1)

        # -- Recent transactions
        rc = ctk.CTkFrame(scroll, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        rc.pack(fill="x", padx=(0, 21))
        rch = ctk.CTkFrame(rc, fg_color="transparent")
        rch.pack(fill="x", padx=21, pady=(21, 13))
        ctk.CTkLabel(rch, text="Dernières transactions", font=("Segoe UI", 20, "bold"), text_color=COLOR_TEXT).pack(side="left")
        ctk.CTkButton(rch, text="Voir tout >", fg_color="transparent", hover_color=COLOR_BG_INPUT,
                      text_color=COLOR_PRIMARY, font=("Segoe UI", 15, "bold"), width=110,
                      command=lambda: self.app.show_view("transactions")).pack(side="right")

        recent = self.app.db.get_recent_transactions(user["id"], 6)
        if not recent:
            ctk.CTkLabel(rc, text="Aucune transaction.", font=("Segoe UI", 16), text_color=COLOR_TEXT_DIM).pack(pady=34)
        else:
            for i, tx in enumerate(recent):
                self._tx_row(rc, tx, COLOR_BG_INPUT if i % 2 == 0 else "transparent")
        ctk.CTkFrame(rc, height=13, fg_color="transparent").pack()

    def _stat_card(self, parent, title, value, bg, color, col):
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        card.grid(row=0, column=col, padx=8, sticky="nsew")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=21, pady=21, fill="x")
        ctk.CTkLabel(inner, text=title, font=("Segoe UI", 15), text_color=COLOR_TEXT_DIM).pack(anchor="w")
        ctk.CTkLabel(inner, text=value, font=("Segoe UI", 28, "bold"), text_color=color).pack(anchor="w", pady=(8, 0))

    def _alert(self, parent, text, bg, color):
        a = ctk.CTkFrame(parent, fg_color=bg, corner_radius=13, border_width=1, border_color=color)
        a.pack(fill="x", pady=(0, 21), padx=(0, 21))
        ctk.CTkLabel(a, text=text, font=("Segoe UI", 16, "bold"), text_color=color).pack(padx=21, pady=18)

    def _monthly_chart(self, parent, monthly, row, col):
        card = ctk.CTkFrame(parent, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        card.grid(row=row, column=col, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(card, text="Revenus vs Dépenses", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT).pack(padx=21, pady=(21, 8), anchor="w")

        fig = Figure(figsize=(6.5, 3.2), dpi=100, facecolor=BG_CHART)
        ax = fig.add_subplot(111)
        ax.set_facecolor(BG_CHART)
        data = {m["month"]: m for m in monthly}
        months = list(range(1, 13))
        deps = [float(data.get(m, {}).get("deposits", 0) or 0) for m in months]
        exps = [float(data.get(m, {}).get("expenses", 0) or 0) for m in months]
        x = range(len(months))
        w = 0.35
        ax.bar([i - w/2 for i in x], deps, w, color="#5eead4", label="Revenus", zorder=3)
        ax.bar([i + w/2 for i in x], exps, w, color="#fdba74", label="Dépenses", zorder=3)
        ax.set_xticks(list(x))
        ax.set_xticklabels([MONTH_NAMES[m] for m in months], fontsize=9, color=COLOR_TEXT_DIM)
        ax.tick_params(axis="y", colors=COLOR_TEXT_DIM, labelsize=9)
        ax.legend(fontsize=9, facecolor=BG_CHART, edgecolor=COLOR_BORDER, labelcolor=COLOR_TEXT)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(COLOR_BORDER)
        ax.spines["bottom"].set_color(COLOR_BORDER)
        ax.grid(axis="y", color=COLOR_BORDER, alpha=0.4, zorder=0)
        fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, card)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=13, pady=(0, 21), fill="both", expand=True)

    def _category_chart(self, parent, user_id, row, col):
        card = ctk.CTkFrame(parent, fg_color=COLOR_BG_CARD, corner_radius=13, border_width=1, border_color=COLOR_BORDER)
        card.grid(row=row, column=col, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(card, text="Par catégorie", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT).pack(padx=21, pady=(21, 8), anchor="w")
        breakdown = self.app.db.get_category_breakdown(user_id)
        if not breakdown:
            ctk.CTkLabel(card, text="Pas de données", font=("Segoe UI", 15), text_color=COLOR_TEXT_DIM).pack(pady=34)
            return
        fig = Figure(figsize=(3.8, 3.2), dpi=100, facecolor=BG_CHART)
        ax = fig.add_subplot(111)
        labels = [r["category"].capitalize() for r in breakdown]
        values = [float(r["total"]) for r in breakdown]
        ax.pie(values, labels=None, autopct="%1.0f%%", startangle=90,
               colors=CHART_COLORS[:len(values)], textprops={"fontsize": 9, "color": COLOR_TEXT})
        ax.legend(labels, loc="lower center", fontsize=8, ncol=2,
                  facecolor=BG_CHART, edgecolor=COLOR_BORDER, labelcolor=COLOR_TEXT,
                  bbox_to_anchor=(0.5, -0.15))
        fig.tight_layout(pad=1.0)
        canvas = FigureCanvasTkAgg(fig, card)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=13, pady=(0, 21), fill="both", expand=True)

    def _tx_row(self, parent, tx, bg):
        row = ctk.CTkFrame(parent, fg_color=bg, corner_radius=8)
        row.pack(fill="x", padx=21, pady=3)
        amount = float(tx["amount"])
        color, sign = (COLOR_SUCCESS, "+") if tx["type"] == "deposit" else (COLOR_ACCENT, "-")

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(13, 0), pady=13)
        ctk.CTkLabel(left, text=tx["description"], font=("Segoe UI", 16), text_color=COLOR_TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text=f"{TYPE_LABELS.get(tx['type'], '')}  |  {tx['date'].strftime('%d/%m/%Y')}",
                     font=("Segoe UI", 13), text_color=COLOR_TEXT_DIM).pack(anchor="w")

        ctk.CTkLabel(row, text=f"{sign}{amount:,.2f} EUR".replace(",", " ").replace(".", ","),
                     font=("Segoe UI", 17, "bold"), text_color=color).pack(side="right", padx=21, pady=13)

    def _show_notifications(self):
        self.app.db.mark_notifications_read(self.app.current_user["id"])
        notifs = self.app.db.get_notifications(self.app.current_user["id"])
        win = ctk.CTkToplevel(self)
        win.title("Notifications")
        win.geometry("560x620")
        win.configure(fg_color=COLOR_BG_DARK)
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="Notifications", font=("Segoe UI", 24, "bold"), text_color=COLOR_TEXT).pack(pady=(34, 21))
        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent", scrollbar_button_color="#d6d6cf", scrollbar_button_hover_color="#c0c0b8", scrollbar_fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=21, pady=(0, 21))
        scroll._scrollbar.configure(width=6, corner_radius=3)
        if not notifs:
            ctk.CTkLabel(scroll, text="Aucune notification.", font=("Segoe UI", 16), text_color=COLOR_TEXT_DIM).pack(pady=34)
        else:
            colors = {"info": (COLOR_PRIMARY, COLOR_PRIMARY_LIGHT), "warning": (COLOR_WARNING, COLOR_WARNING_LIGHT), "danger": (COLOR_DANGER, COLOR_DANGER_LIGHT)}
            for n in notifs:
                fg, bg = colors.get(n["type"], (COLOR_TEXT, COLOR_BG_CARD))
                nf = ctk.CTkFrame(scroll, fg_color=bg, corner_radius=13, border_width=1, border_color=fg)
                nf.pack(fill="x", pady=5)
                ctk.CTkLabel(nf, text=n["message"], font=("Segoe UI", 15), text_color=fg, wraplength=460).pack(padx=21, pady=16)
