import customtkinter as ctk
from config import *
from database import Database
from views.login_view import LoginView
from views.register_view import RegisterView
from views.dashboard_view import DashboardView
from views.transactions_view import TransactionsView
from views.banker_view import BankerView
from views.settings_view import SettingsView


class BudgetBuddyApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1000, 600)
        self.configure(fg_color=COLOR_BG_DARK)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Load custom font for logo
        import os
        font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "DESIGNER.otf")
        if os.path.exists(font_path):
            ctk.FontManager.load_font(font_path)

        self.db = Database()
        self.current_user = None
        self.current_view = None
        self.content_frame = None
        self.sidebar = None

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.show_view("login")

    # -------------------------------------------------------------- Routing

    def show_view(self, view_name):
        """Destroy the current view and display a new one."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
        if self.content_frame:
            self.content_frame.destroy()
            self.content_frame = None
        if self.sidebar:
            self.sidebar.destroy()
            self.sidebar = None

        is_auth = self.current_user and view_name not in ("login", "register")
        if is_auth:
            self._build_sidebar(view_name)

        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        if is_auth:
            self.content_frame.pack(side="right", fill="both", expand=True)
        else:
            self.content_frame.pack(fill="both", expand=True)

        views = {
            "login": LoginView,
            "register": RegisterView,
            "dashboard": DashboardView,
            "transactions": TransactionsView,
            "banker": BankerView,
            "settings": SettingsView,
        }

        view_class = views.get(view_name)
        if view_class:
            self.current_view = view_class(self.content_frame, self)
            self.current_view.pack(fill="both", expand=True)

    # -------------------------------------------------------------- Sidebar

    def _build_sidebar(self, active_view):
        self.sidebar = ctk.CTkFrame(
            self.main_container, fg_color=COLOR_BG_CARD,
            width=260, corner_radius=0, border_width=1, border_color=COLOR_BORDER
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=21, pady=(21, 34))

        ctk.CTkLabel(logo_frame, text="BUDGET BUDDY", font=("DESIGNER", 19), text_color=COLOR_TEXT).pack(anchor="w")
        ctk.CTkFrame(logo_frame, fg_color=COLOR_ACCENT, height=3, width=44, corner_radius=2).pack(anchor="w", pady=(8, 0))

        # Navigation items based on role
        if self.current_user and self.current_user["role"] == "banker":
            nav = [
                ("Espace banquier", "banker"),
                ("Profil", "settings"),
            ]
        else:
            nav = [
                ("Tableau de bord", "dashboard"),
                ("Transactions", "transactions"),
                ("Parametres", "settings"),
            ]

        for label, view in nav:
            active = view == active_view
            ctk.CTkButton(
                self.sidebar, text=f"  {label}", anchor="w", height=46, corner_radius=10,
                fg_color=COLOR_PRIMARY if active else "transparent",
                hover_color=COLOR_BG_INPUT if not active else COLOR_PRIMARY_HOVER,
                text_color="white" if active else COLOR_TEXT_DIM,
                font=("Segoe UI", 15, "bold" if active else "normal"),
                command=lambda v=view: self.show_view(v)
            ).pack(fill="x", padx=13, pady=3)

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # User info
        user_frame = ctk.CTkFrame(self.sidebar, fg_color=COLOR_BG_INPUT, corner_radius=13)
        user_frame.pack(fill="x", padx=13, pady=(0, 8))
        uf = ctk.CTkFrame(user_frame, fg_color="transparent")
        uf.pack(fill="x", padx=13, pady=13)

        name = f"{self.current_user['first_name']} {self.current_user['last_name']}"
        role = "Banquier" if self.current_user["role"] == "banker" else "Client"
        ctk.CTkLabel(uf, text=name, font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT, anchor="w").pack(fill="x")
        ctk.CTkLabel(uf, text=role, font=("Segoe UI", 12), text_color=COLOR_TEXT_DIM, anchor="w").pack(fill="x")

        # Logout
        ctk.CTkButton(
            self.sidebar, text="Deconnexion", height=40, corner_radius=10,
            fg_color="transparent", hover_color="#fee2e2",
            text_color=COLOR_DANGER, font=("Segoe UI", 14),
            command=self.logout
        ).pack(fill="x", padx=13, pady=(5, 21))

    # -------------------------------------------------------------- Auth

    def login(self, user):
        self.current_user = user
        if user["role"] == "client":
            try:
                self.db.process_recurring(user["id"])
            except Exception:
                pass
            try:
                self.db.check_budget_alerts(user["id"])
            except Exception:
                pass
            self.current_user = self.db.get_user_by_id(user["id"])
            self.show_view("dashboard")
        else:
            self.show_view("banker")

    def logout(self):
        self.current_user = None
        self.show_view("login")

    def on_closing(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = BudgetBuddyApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
