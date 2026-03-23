import customtkinter as ctk
from config import *
from auth import verify_password


class LoginView(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_BG_DARK)
        self.app = app
        self._build()

    def _build(self):
        right = ctk.CTkFrame(self, fg_color=COLOR_BG_DARK, corner_radius=0, width=560)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        left = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY, corner_radius=0)
        left.pack(side="left", fill="both", expand=True)

        # ============ LEFT ============
        ctk.CTkLabel(left, text="BUDGET BUDDY", font=("DESIGNER", 28),
                     text_color="white").pack(anchor="w", padx=52, pady=(44, 0))

        # Container for everything below logo - content centered within
        center = ctk.CTkFrame(left, fg_color="transparent")
        center.pack(fill="both", expand=True)
        center.grid_rowconfigure(0, weight=1)
        center.grid_rowconfigure(2, weight=2)
        center.grid_columnconfigure(0, weight=1)

        lc = ctk.CTkFrame(center, fg_color="transparent")
        lc.grid(row=1, column=0)

        ctk.CTkLabel(lc, text="Tout ce qu'il faut\npour gérer\nvos finances.",
                     font=("Segoe UI", 70, "bold"), text_color="white",
                     justify="center").pack(pady=(0, 28))

        ctk.CTkLabel(lc, text="Suivez vos dépenses, définissez des plafonds\net gardez le contrôle sur tous vos comptes.",
                     font=("Segoe UI", 24), text_color="#a7f3d0",
                     justify="center").pack(pady=(0, 40))

        features = ctk.CTkFrame(lc, fg_color="transparent")
        features.pack()

        for title, desc in [
            ("Espace Client", "Dépenses, plafonds, export CSV, récurrences"),
            ("Espace Banquier", "Portefeuille clients, opérations déléguées"),
            ("Sécurité", "Hachage bcrypt, sel, poivre, SQL paramétré"),
        ]:
            row = ctk.CTkFrame(features, fg_color="transparent")
            row.pack(fill="x", pady=6)
            dot = ctk.CTkFrame(row, fg_color=COLOR_ACCENT, corner_radius=6, width=12, height=12)
            dot.pack(side="left", padx=(0, 14), pady=8)
            dot.pack_propagate(False)
            txt = ctk.CTkFrame(row, fg_color="transparent")
            txt.pack(side="left")
            ctk.CTkLabel(txt, text=title, font=("Segoe UI", 22, "bold"),
                         text_color="white").pack(anchor="w")
            ctk.CTkLabel(txt, text=desc, font=("Segoe UI", 18),
                         text_color="#a7f3d0").pack(anchor="w")

        # ============ RIGHT ============
        ctk.CTkFrame(right, fg_color="transparent").pack(fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(padx=56, fill="x")

        ctk.CTkLabel(form, text="Connexion",
                     font=("Segoe UI", 34, "bold"), text_color=COLOR_TEXT).pack(anchor="w")
        # Orange accent bar under title
        ctk.CTkFrame(form, fg_color=COLOR_ACCENT, height=4, width=60, corner_radius=2).pack(anchor="w", pady=(8, 6))
        ctk.CTkLabel(form, text="Ravi de vous revoir. Entrez vos identifiants.",
                     font=("Segoe UI", 16), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(6, 36))

        ctk.CTkLabel(form, text="ADRESSE E-MAIL", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 6))
        self.email_entry = ctk.CTkEntry(
            form, height=54, corner_radius=12, fg_color=COLOR_BG_INPUT,
            border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT,
            placeholder_text="nom@exemple.com", placeholder_text_color="#9ca3af",
            font=("Segoe UI", 16)
        )
        self.email_entry.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(form, text="MOT DE PASSE", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 6))
        self.password_entry = ctk.CTkEntry(
            form, height=54, corner_radius=12, fg_color=COLOR_BG_INPUT,
            border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT,
            placeholder_text="Votre mot de passe", placeholder_text_color="#9ca3af",
            show="*", font=("Segoe UI", 16)
        )
        self.password_entry.pack(fill="x", pady=(0, 14))
        self.password_entry.bind("<Return>", lambda e: self._login())

        self.error_label = ctk.CTkLabel(form, text="", font=("Segoe UI", 13), text_color=COLOR_DANGER)
        self.error_label.pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            form, text="Se connecter", height=56, corner_radius=12,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
            text_color="white", font=("Segoe UI", 17, "bold"), command=self._login
        ).pack(fill="x")

        div = ctk.CTkFrame(form, fg_color="transparent", height=20)
        div.pack(fill="x", pady=28)
        ctk.CTkFrame(div, height=1, fg_color=COLOR_BORDER).place(relwidth=1, rely=0.5)
        ctk.CTkLabel(div, text="  ou  ", font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_DIM, fg_color=COLOR_BG_DARK).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(
            form, text="Créer un compte", height=56, corner_radius=12,
            fg_color="transparent", hover_color=COLOR_BG_INPUT,
            border_width=1, border_color=COLOR_ACCENT,
            text_color=COLOR_ACCENT, font=("Segoe UI", 16),
            command=lambda: self.app.show_view("register")
        ).pack(fill="x")

        ctk.CTkFrame(right, fg_color="transparent").pack(fill="both", expand=True)

    def _login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        if not email or not password:
            self.error_label.configure(text="Veuillez remplir tous les champs.")
            return
        user = self.app.db.get_user_by_email(email)
        if not user:
            self.error_label.configure(text="Aucun compte avec cet e-mail.")
            return
        if not verify_password(password, user["password_hash"]):
            self.error_label.configure(text="Mot de passe incorrect.")
            return
        self.error_label.configure(text="")
        self.app.login(user)
