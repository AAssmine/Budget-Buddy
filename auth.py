import re
import bcrypt
from config import PEPPER


def validate_password(password: str) -> tuple[bool, str]:

    if len(password) < 10:
        return False, "Le mot de passe doit contenir au moins 10 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "Il manque au moins une majuscule."
    if not re.search(r"[a-z]", password):
        return False, "Il manque au moins une minuscule."
    if not re.search(r"\d", password):
        return False, "Il manque au moins un chiffre."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Il manque au moins un caractere special."
    return True, ""


def password_strength(password: str) -> tuple[int, str]:

    score = 0
    if len(password) >= 10:
        score += 1
    if len(password) >= 14:
        score += 1
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        score += 1

    labels = {
        0: "Tres faible", 1: "Faible", 2: "Moyen",
        3: "Correct", 4: "Fort", 5: "Excellent"
    }
    return score, labels.get(score, "")


def hash_password(password: str) -> str:

    salted = (password + PEPPER).encode("utf-8")
    return bcrypt.hashpw(salted, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, stored_hash: str) -> bool:

    salted = (password + PEPPER).encode("utf-8")
    return bcrypt.checkpw(salted, stored_hash.encode("utf-8"))


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
