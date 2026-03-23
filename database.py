import csv
import uuid
from datetime import datetime

import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT


class Database:
    """Handles all database operations: users, transactions, notifications, budgets."""

    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT, autocommit=True
            )
        except Error as e:
            raise ConnectionError(f"MySQL connection failed: {e}")

    def _cursor(self):
        """Return a dict cursor, reconnecting if the connection was lost."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection.cursor(dictionary=True)

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    # ------------------------------------------------------------------ Users

    def create_user(self, first_name, last_name, email, password_hash, role="client"):
        cur = self._cursor()
        cur.execute(
            "INSERT INTO users (first_name, last_name, email, password_hash, role) "
            "VALUES (%s, %s, %s, %s, %s)",
            (first_name, last_name, email, password_hash, role)
        )
        return cur.lastrowid

    def get_user_by_email(self, email):
        cur = self._cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cur.fetchone()

    def get_user_by_id(self, user_id):
        cur = self._cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()

    def update_balance(self, user_id, delta):
        """Add (or subtract if negative) an amount to the user balance."""
        cur = self._cursor()
        cur.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (delta, user_id))

    def get_balance(self, user_id):
        cur = self._cursor()
        cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        return float(row["balance"]) if row else 0.0

    def get_all_clients(self):
        cur = self._cursor()
        cur.execute(
            "SELECT id, first_name, last_name, email, balance "
            "FROM users WHERE role = 'client' ORDER BY last_name"
        )
        return cur.fetchall()

    def get_clients_of_banker(self, banker_id):
        cur = self._cursor()
        cur.execute(
            "SELECT id, first_name, last_name, email, balance "
            "FROM users WHERE banker_id = %s ORDER BY last_name",
            (banker_id,)
        )
        return cur.fetchall()

    def assign_client_to_banker(self, client_id, banker_id):
        cur = self._cursor()
        cur.execute("UPDATE users SET banker_id = %s WHERE id = %s", (banker_id, client_id))

    def unassign_client(self, client_id):
        cur = self._cursor()
        cur.execute("UPDATE users SET banker_id = NULL WHERE id = %s", (client_id,))

    def search_clients(self, query):
        cur = self._cursor()
        like = f"%{query}%"
        cur.execute(
            "SELECT id, first_name, last_name, email, balance FROM users "
            "WHERE role = 'client' AND (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)",
            (like, like, like)
        )
        return cur.fetchall()

    # ------------------------------------------------------------- Transactions

    @staticmethod
    def _generate_ref():
        return "TX-" + uuid.uuid4().hex[:12].upper()

    def add_transaction(self, user_id, description, amount, tx_type, category="autre", recipient_id=None):
        ref = self._generate_ref()
        cur = self._cursor()
        cur.execute(
            "INSERT INTO transactions (reference, user_id, description, amount, type, category, recipient_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (ref, user_id, description, amount, tx_type, category, recipient_id)
        )
        return ref

    def deposit(self, user_id, amount, description="Depot", category="autre"):
        self.update_balance(user_id, amount)
        ref = self.add_transaction(user_id, description, amount, "deposit", category)
        self._check_overdraft(user_id)
        return ref

    def withdraw(self, user_id, amount, description="Retrait", category="autre"):
        self.update_balance(user_id, -amount)
        ref = self.add_transaction(user_id, description, amount, "withdrawal", category)
        self._check_overdraft(user_id)
        return ref

    def transfer(self, sender_id, recipient_id, amount, description="Transfert"):
        self.update_balance(sender_id, -amount)
        self.update_balance(recipient_id, amount)
        ref = self.add_transaction(sender_id, description, amount, "transfer", "autre", recipient_id)
        # Record incoming transaction for recipient
        self.add_transaction(recipient_id, f"Recu de transfert : {description}", amount, "deposit", "autre", sender_id)
        self._check_overdraft(sender_id)
        return ref

    def get_transactions(self, user_id, filters=None):
        """
        Retrieve transactions for a user with optional filters.
        Supported filter keys: date, date_start, date_end, category, tx_type, sort_amount.
        """
        query = "SELECT * FROM transactions WHERE user_id = %s"
        params = [user_id]

        if filters:
            if filters.get("date"):
                query += " AND DATE(date) = %s"
                params.append(filters["date"])
            if filters.get("date_start"):
                query += " AND DATE(date) >= %s"
                params.append(filters["date_start"])
            if filters.get("date_end"):
                query += " AND DATE(date) <= %s"
                params.append(filters["date_end"])
            if filters.get("category"):
                query += " AND category = %s"
                params.append(filters["category"])
            if filters.get("tx_type"):
                query += " AND type = %s"
                params.append(filters["tx_type"])

            sort = filters.get("sort_amount")
            if sort == "asc":
                query += " ORDER BY amount ASC"
            elif sort == "desc":
                query += " ORDER BY amount DESC"
            else:
                query += " ORDER BY date DESC"
        else:
            query += " ORDER BY date DESC"

        cur = self._cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def get_monthly_summary(self, user_id, year=None):
        if year is None:
            year = datetime.now().year
        cur = self._cursor()
        cur.execute("""
            SELECT MONTH(date) AS month,
                   SUM(CASE WHEN type = 'deposit' THEN amount ELSE 0 END) AS deposits,
                   SUM(CASE WHEN type IN ('withdrawal','transfer') THEN amount ELSE 0 END) AS expenses
            FROM transactions
            WHERE user_id = %s AND YEAR(date) = %s
            GROUP BY MONTH(date) ORDER BY month
        """, (user_id, year))
        return cur.fetchall()

    def get_category_breakdown(self, user_id):
        cur = self._cursor()
        cur.execute("""
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE user_id = %s AND type IN ('withdrawal','transfer')
            GROUP BY category ORDER BY total DESC
        """, (user_id,))
        return cur.fetchall()

    def get_recent_transactions(self, user_id, limit=5):
        cur = self._cursor()
        cur.execute(
            "SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC LIMIT %s",
            (user_id, limit)
        )
        return cur.fetchall()

    # ---------------------------------------------------------- Notifications

    def _check_overdraft(self, user_id):
        """Generate alerts if the balance is negative or dangerously low."""
        balance = self.get_balance(user_id)
        if balance < 0:
            self.add_notification(
                user_id,
                f"Attention : votre solde est negatif ({balance:.2f} EUR). Vous etes a decouvert.",
                "danger"
            )
        elif balance < 100:
            self.add_notification(
                user_id,
                f"Solde bas ({balance:.2f} EUR). Pensez a alimenter votre compte.",
                "warning"
            )

    def add_notification(self, user_id, message, notif_type="info"):
        cur = self._cursor()
        cur.execute(
            "INSERT INTO notifications (user_id, message, type) VALUES (%s, %s, %s)",
            (user_id, message, notif_type)
        )

    def get_notifications(self, user_id, unread_only=False):
        cur = self._cursor()
        query = "SELECT * FROM notifications WHERE user_id = %s"
        if unread_only:
            query += " AND is_read = FALSE"
        query += " ORDER BY created_at DESC LIMIT 20"
        cur.execute(query, (user_id,))
        return cur.fetchall()

    def mark_notifications_read(self, user_id):
        cur = self._cursor()
        cur.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (user_id,))

    def count_unread_notifications(self, user_id):
        cur = self._cursor()
        cur.execute(
            "SELECT COUNT(*) AS c FROM notifications WHERE user_id = %s AND is_read = FALSE",
            (user_id,)
        )
        row = cur.fetchone()
        return row["c"] if row else 0

    # --------------------------------------------------------- Budget limits

    def set_budget_limit(self, user_id, category, monthly_limit):
        cur = self._cursor()
        cur.execute(
            "INSERT INTO budget_limits (user_id, category, monthly_limit) "
            "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE monthly_limit = %s",
            (user_id, category, monthly_limit, monthly_limit)
        )

    def get_budget_limits(self, user_id):
        cur = self._cursor()
        cur.execute("SELECT * FROM budget_limits WHERE user_id = %s", (user_id,))
        return cur.fetchall()

    def delete_budget_limit(self, user_id, category):
        cur = self._cursor()
        cur.execute(
            "DELETE FROM budget_limits WHERE user_id = %s AND category = %s",
            (user_id, category)
        )

    def get_category_spending_this_month(self, user_id, category):
        cur = self._cursor()
        cur.execute("""
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE user_id = %s AND category = %s
              AND type IN ('withdrawal','transfer')
              AND MONTH(date) = MONTH(CURRENT_DATE())
              AND YEAR(date) = YEAR(CURRENT_DATE())
        """, (user_id, category))
        row = cur.fetchone()
        return float(row["total"]) if row else 0.0

    def check_budget_alerts(self, user_id):
        """Compare spending against budget limits and create notifications."""
        limits = self.get_budget_limits(user_id)
        for lim in limits:
            spent = self.get_category_spending_this_month(user_id, lim["category"])
            cap = float(lim["monthly_limit"])
            if cap <= 0:
                continue
            ratio = spent / cap
            if ratio >= 1.0:
                self.add_notification(
                    user_id,
                    f"Budget depasse : {lim['category']} - {spent:.2f} EUR / {cap:.2f} EUR",
                    "danger"
                )
            elif ratio >= 0.8:
                self.add_notification(
                    user_id,
                    f"Budget bientot atteint : {lim['category']} a {ratio*100:.0f}%",
                    "warning"
                )

    # ------------------------------------------------- Recurring transactions

    def add_recurring(self, user_id, description, amount, tx_type, category, frequency, next_date, recipient_id=None):
        cur = self._cursor()
        cur.execute(
            "INSERT INTO recurring_transactions "
            "(user_id, description, amount, type, category, frequency, next_date, recipient_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, description, amount, tx_type, category, frequency, next_date, recipient_id)
        )

    def get_recurring(self, user_id):
        cur = self._cursor()
        cur.execute(
            "SELECT * FROM recurring_transactions "
            "WHERE user_id = %s AND is_active = TRUE ORDER BY next_date",
            (user_id,)
        )
        return cur.fetchall()

    def delete_recurring(self, recurring_id):
        cur = self._cursor()
        cur.execute(
            "UPDATE recurring_transactions SET is_active = FALSE WHERE id = %s",
            (recurring_id,)
        )

    def process_recurring(self, user_id):
        """Execute all due recurring transactions and advance their next_date."""
        from dateutil.relativedelta import relativedelta

        cur = self._cursor()
        cur.execute(
            "SELECT * FROM recurring_transactions "
            "WHERE user_id = %s AND is_active = TRUE AND next_date <= CURDATE()",
            (user_id,)
        )
        due_list = cur.fetchall()

        deltas = {
            "weekly": relativedelta(weeks=1),
            "monthly": relativedelta(months=1),
            "yearly": relativedelta(years=1),
        }

        for rec in due_list:
            amount = float(rec["amount"])
            if rec["type"] == "deposit":
                self.deposit(user_id, amount, rec["description"], rec["category"])
            elif rec["type"] == "transfer" and rec.get("recipient_id"):
                self.transfer(user_id, rec["recipient_id"], amount, rec["description"])
            else:
                self.withdraw(user_id, amount, rec["description"], rec["category"])

            delta = deltas.get(rec["frequency"], relativedelta(months=1))
            new_date = rec["next_date"] + delta
            cur2 = self._cursor()
            cur2.execute(
                "UPDATE recurring_transactions SET next_date = %s WHERE id = %s",
                (new_date, rec["id"])
            )

    # -------------------------------------------------------------- Export

    def export_transactions_csv(self, user_id, filepath):
        """Write all transactions for the given user to a CSV file."""
        transactions = self.get_transactions(user_id)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Reference", "Description", "Montant", "Type", "Categorie", "Date"])
            for tx in transactions:
                writer.writerow([
                    tx["reference"], tx["description"], tx["amount"],
                    tx["type"], tx["category"],
                    tx["date"].strftime("%d/%m/%Y %H:%M")
                ])
        return filepath
