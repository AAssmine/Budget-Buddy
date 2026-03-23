import customtkinter as ctk
from config import *
from auth import validate_password, validate_email, hash_password, password_strength


class RegisterView(ctk.CTkFrame):

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

        center = ctk.CTkFrame(left, fg_color="transparent")
        center.pack(fill="both", expand=True)
        center.grid_rowconfigure(0, weight=1)
        center.grid_rowconfigure(2, weight=2)
        center.grid_columnconfigure(0, weight=1)

        lc = ctk.CTkFrame(center, fg_color="transparent")
        lc.grid(row=1, column=0)

        ctk.CTkLabel(lc, text="Votre sécurité,\nc'est notre\npriorité.",
                     font=("Segoe UI", 70, "bold"), text_color="white",
                     justify="center").pack(pady=(0, 28))

        ctk.CTkLabel(lc, text="Vos données sont protégées par un système\nde hachage avancé avec sel et poivre.",
                     font=("Segoe UI", 24), text_color="#a7f3d0",
                     justify="center").pack(pady=(0, 40))

        features = ctk.CTkFrame(lc, fg_color="transparent")
        features.pack()

        for title, desc in [
            ("Hachage bcrypt", "Sel unique généré à chaque inscription"),
            ("Poivre secret", "Stocké hors de la base de données"),
            ("SQL paramétré", "Protection contre les injections"),
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
        scroll = ctk.CTkScrollableFrame(right, fg_color="transparent", scrollbar_button_color="#d6d6cf", scrollbar_button_hover_color="#c0c0b8", scrollbar_fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        scroll._scrollbar.configure(width=6, corner_radius=3)

        form = ctk.CTkFrame(scroll, fg_color="transparent")
        form.pack(padx=56, pady=(44, 36), fill="x")

        ctk.CTkLabel(form, text="Créer un compte",
                     font=("Segoe UI", 34, "bold"), text_color=COLOR_TEXT).pack(anchor="w")
        ctk.CTkFrame(form, fg_color=COLOR_ACCENT, height=4, width=60, corner_radius=2).pack(anchor="w", pady=(8, 6))
        ctk.CTkLabel(form, text="Rejoignez Budget Buddy en quelques secondes.",
                     font=("Segoe UI", 16), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(6, 32))

        name_row = ctk.CTkFrame(form, fg_color="transparent")
        name_row.pack(fill="x", pady=(0, 16))
        lf = ctk.CTkFrame(name_row, fg_color="transparent")
        lf.pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkLabel(lf, text="PRÉNOM", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 5))
        self.first_name = ctk.CTkEntry(lf, height=52, corner_radius=12, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, font=("Segoe UI", 16))
        self.first_name.pack(fill="x")

        rf = ctk.CTkFrame(name_row, fg_color="transparent")
        rf.pack(side="left", expand=True, fill="x", padx=(6, 0))
        ctk.CTkLabel(rf, text="NOM", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 5))
        self.last_name = ctk.CTkEntry(rf, height=52, corner_radius=12, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, font=("Segoe UI", 16))
        self.last_name.pack(fill="x")

        ctk.CTkLabel(form, text="ADRESSE E-MAIL", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 5))
        self.email = ctk.CTkEntry(form, height=52, corner_radius=12, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, placeholder_text="nom@exemple.com", placeholder_text_color="#9ca3af", font=("Segoe UI", 16))
        self.email.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(form, text="MOT DE PASSE", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 5))
        self.password = ctk.CTkEntry(form, height=52, corner_radius=12, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, show="*", font=("Segoe UI", 16))
        self.password.pack(fill="x", pady=(0, 6))
        self.password.bind("<KeyRelease>", self._update_strength)

        str_row = ctk.CTkFrame(form, fg_color="transparent")
        str_row.pack(fill="x", pady=(0, 4))
        self.strength_bar = ctk.CTkProgressBar(str_row, height=4, corner_radius=2, progress_color=COLOR_DANGER)
        self.strength_bar.pack(side="left", fill="x", expand=True)
        self.strength_bar.set(0)
        self.strength_label = ctk.CTkLabel(str_row, text="", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_DIM)
        self.strength_label.pack(side="right", padx=(8, 0))

        ctk.CTkLabel(form, text="Min. 10 car. | 1 majuscule | 1 minuscule | 1 chiffre | 1 spécial",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 16))

        ctk.CTkLabel(form, text="CONFIRMER LE MOT DE PASSE", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 5))
        self.password_confirm = ctk.CTkEntry(form, height=52, corner_radius=12, fg_color=COLOR_BG_INPUT, border_color=COLOR_BORDER, border_width=1, text_color=COLOR_TEXT, show="*", font=("Segoe UI", 16))
        self.password_confirm.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(form, text="TYPE DE COMPTE", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(0, 8))
        self.role_var = ctk.StringVar(value="client")
        role_frame = ctk.CTkFrame(form, fg_color="transparent")
        role_frame.pack(fill="x", pady=(0, 14))

        self.role_client = ctk.CTkButton(
            role_frame, text="Client", height=48, corner_radius=10,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color="white", font=("Segoe UI", 15, "bold"),
            command=lambda: self._set_role("client"))
        self.role_client.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.role_banker = ctk.CTkButton(
            role_frame, text="Banquier", height=48, corner_radius=10,
            fg_color=COLOR_BG_INPUT, hover_color=COLOR_BORDER,
            text_color=COLOR_TEXT_DIM, font=("Segoe UI", 15, "bold"),
            command=lambda: self._set_role("banker"))
        self.role_banker.pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.error_label = ctk.CTkLabel(form, text="", font=("Segoe UI", 13), text_color=COLOR_DANGER, wraplength=400)
        self.error_label.pack(fill="x", pady=(6, 8))

        ctk.CTkButton(form, text="Créer mon compte", height=56, corner_radius=12,
                      fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                      text_color="white", font=("Segoe UI", 17, "bold"),
                      command=self._submit).pack(fill="x")

        div = ctk.CTkFrame(form, fg_color="transparent", height=20)
        div.pack(fill="x", pady=20)
        ctk.CTkFrame(div, height=1, fg_color=COLOR_BORDER).place(relwidth=1, rely=0.5)
        ctk.CTkLabel(div, text="  ou  ", font=("Segoe UI", 13),
                     text_color=COLOR_TEXT_DIM, fg_color=COLOR_BG_DARK).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(form, text="Se connecter à un compte existant", height=48, corner_radius=12,
                      fg_color="transparent", hover_color=COLOR_BG_INPUT,
                      border_width=1, border_color=COLOR_ACCENT,
                      text_color=COLOR_ACCENT, font=("Segoe UI", 15),
                      command=lambda: self.app.show_view("login")).pack(fill="x")

    def _set_role(self, role):
        self.role_var.set(role)
        if role == "client":
            self.role_client.configure(fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, text_color="white")
            self.role_banker.configure(fg_color=COLOR_BG_INPUT, hover_color=COLOR_BORDER, text_color=COLOR_TEXT_DIM)
        else:
            self.role_banker.configure(fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, text_color="white")
            self.role_client.configure(fg_color=COLOR_BG_INPUT, hover_color=COLOR_BORDER, text_color=COLOR_TEXT_DIM)

    def _update_strength(self, event=None):
        pw = self.password.get()
        if not pw:
            self.strength_bar.set(0)
            self.strength_label.configure(text="")
            return
        score, label = password_strength(pw)
        self.strength_bar.set(score / 5)
        colors = {0: "#dc2626", 1: "#dc2626", 2: "#d97706", 3: "#d97706", 4: "#16a34a", 5: "#0d9488"}
        c = colors.get(score, "#dc2626")
        self.strength_bar.configure(progress_color=c)
        self.strength_label.configure(text=label, text_color=c)

    def _submit(self):
        fn = self.first_name.get().strip()
        ln = self.last_name.get().strip()
        em = self.email.get().strip()
        pw = self.password.get()
        pwc = self.password_confirm.get()
        role = self.role_var.get()

        if not all([fn, ln, em, pw, pwc]):
            self.error_label.configure(text="Veuillez remplir tous les champs.")
            return
        if not validate_email(em):
            self.error_label.configure(text="Adresse e-mail invalide.")
            return
        if pw != pwc:
            self.error_label.configure(text="Les mots de passe ne correspondent pas.")
            return
        valid, msg = validate_password(pw)
        if not valid:
            self.error_label.configure(text=msg)
            return
        if self.app.db.get_user_by_email(em):
            self.error_label.configure(text="Un compte existe déjà avec cet e-mail.")
            return

        try:
            hashed = hash_password(pw)
            uid = self.app.db.create_user(fn, ln, em, hashed, role)
            user = self.app.db.get_user_by_id(uid)
            self.error_label.configure(text="")
            self.app.login(user)
        except Exception as e:
            self.error_label.configure(text=f"Erreur : {e}")
