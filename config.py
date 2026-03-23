import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "budget_buddy")
DB_PORT = int(os.getenv("DB_PORT", 3306))
PEPPER = os.getenv("PEPPER", "")

APP_NAME = "Budget Buddy"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750

# -- Light theme with pastels
COLOR_BG_DARK = "#eeeee9"
COLOR_BG_CARD = "#f7f7f4"
COLOR_BG_INPUT = "#e8e8e2"
COLOR_PRIMARY = "#0d9488"
COLOR_PRIMARY_HOVER = "#0f766e"
COLOR_PRIMARY_LIGHT = "#ccfbf1"
COLOR_ACCENT = "#f4a261"
COLOR_ACCENT_HOVER = "#e68f4a"
COLOR_ACCENT_LIGHT = "#fef0e1"
COLOR_SUCCESS = "#16a34a"
COLOR_SUCCESS_LIGHT = "#dcfce7"
COLOR_DANGER = "#dc2626"
COLOR_DANGER_LIGHT = "#fee2e2"
COLOR_WARNING = "#d97706"
COLOR_WARNING_LIGHT = "#fef3c7"
COLOR_TEXT = "#1a1a1a"
COLOR_TEXT_DIM = "#6b7280"
COLOR_BORDER = "#d6d6cf"

# Pastel chart colors
CHART_COLORS = ["#0d9488", "#f4a261", "#a78bfa", "#f472b6", "#34d399", "#60a5fa", "#fbbf24", "#fb923c", "#94a3b8"]

CATEGORIES = [
    "alimentation", "transport", "loisir", "repas",
    "santé", "logement", "éducation", "pot-de-vin", "autre"
]

TYPE_LABELS = {
    "deposit": "Dépôt",
    "withdrawal": "Retrait",
    "transfer": "Transfert"
}
