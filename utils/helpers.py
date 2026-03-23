from datetime import datetime
import customtkinter as ctk
from tkcalendar import Calendar

MONTH_NAMES = [
    "", "Jan", "Fev", "Mar", "Avr", "Mai", "Juin",
    "Juil", "Aout", "Sep", "Oct", "Nov", "Dec"
]


def format_currency(amount):
    """Format a numeric amount as a EUR string (e.g. '1 234,50 EUR')."""
    if amount is None:
        return "0,00 EUR"
    sign = "-" if amount < 0 else ""
    return f"{sign}{abs(amount):,.2f} EUR".replace(",", " ").replace(".", ",")


def format_date(dt):
    if isinstance(dt, str):
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%d/%m/%Y %H:%M")


def format_date_short(dt):
    if isinstance(dt, str):
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%d/%m/%Y")


class DatePickerButton(ctk.CTkButton):
    """A button that opens a calendar popup and stores the selected date."""

    def __init__(self, parent, width=130, height=42, placeholder="Choisir date",
                 fg_color="#e8e8e2", hover_color="#deded4", text_color="#6b7280",
                 text_color_selected="#1a1a1a", border_color="#d6d6cf",
                 font=("Segoe UI", 13), corner_radius=13, **kwargs):
        self._selected_date = ""
        self._placeholder = placeholder
        self._text_color_dim = text_color
        self._text_color_sel = text_color_selected
        super().__init__(
            parent, text=placeholder, width=width, height=height,
            corner_radius=corner_radius, fg_color=fg_color,
            hover_color=hover_color, text_color=text_color,
            border_width=1, border_color=border_color,
            font=font, anchor="w", command=self._open_calendar, **kwargs
        )

    def _open_calendar(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Calendrier")
        popup.geometry("320x320")
        popup.configure(fg_color="#eeeee9")
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        cal = Calendar(
            popup, selectmode="day", date_pattern="yyyy-mm-dd",
            background="#eeeee9", foreground="#1a1a1a",
            headersbackground="#0d9488", headersforeground="white",
            selectbackground="#f4a261", selectforeground="white",
            normalbackground="#f7f7f4", normalforeground="#1a1a1a",
            weekendbackground="#f7f7f4", weekendforeground="#6b7280",
            othermonthbackground="#eeeee9", othermonthforeground="#9ca3af",
            bordercolor="#d6d6cf", font=("Segoe UI", 11),
        )
        cal.pack(fill="both", expand=True, padx=13, pady=(13, 8))

        def on_select():
            self._selected_date = cal.get_date()
            self.configure(text=self._selected_date, text_color=self._text_color_sel)
            popup.destroy()

        ctk.CTkButton(
            popup, text="Valider", height=38, corner_radius=10,
            fg_color="#0d9488", hover_color="#0f766e", text_color="white",
            font=("Segoe UI", 13, "bold"), command=on_select
        ).pack(fill="x", padx=13, pady=(0, 13))

    def get(self):
        """Return the selected date string (YYYY-MM-DD) or empty string."""
        return self._selected_date

    def clear(self):
        """Reset to placeholder."""
        self._selected_date = ""
        self.configure(text=self._placeholder, text_color=self._text_color_dim)
