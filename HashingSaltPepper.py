import binascii
import hashlib
import hmac
import os
import sqlite3
import string
import tkinter as tk
from tkinter import ttk

# ==========================================
# SECURITY CONFIGURATION
# ==========================================

PEPPER = "Sup3rS3cr3tP3pp3r!2026"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")
MIN_PASSWORD_LENGTH = 12


def get_connection():
    """Create a SQLite connection configured to better handle contention."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def setup_database():
    """Create the users table if it does not already exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                hashed_password TEXT NOT NULL,
                salt TEXT NOT NULL
            )
            """
        )
        conn.commit()


def evaluate_password_strength(password):
    """Check the password rules required by the project instructions."""
    checks = {
        "lowercase letter": any(ch.islower() for ch in password),
        "uppercase letter": any(ch.isupper() for ch in password),
        "number": any(ch.isdigit() for ch in password),
        "symbol": any(ch in string.punctuation for ch in password),
        "at least 12 characters": len(password) >= MIN_PASSWORD_LENGTH,
    }
    passed = sum(checks.values())

    if passed <= 2:
        strength = "Weak"
    elif passed <= 4:
        strength = "Medium"
    else:
        strength = "Strong"

    missing = [rule for rule, is_valid in checks.items() if not is_valid]
    return strength, passed, checks, missing


def hash_password(password, salt_hex):
    """Combine password + salt + pepper, then hash using SHA-256."""
    combined_string = password + salt_hex + PEPPER
    return hashlib.sha256(combined_string.encode("utf-8")).hexdigest()


def register_user(username, password, confirm_password):
    """Validate and securely register a new user."""
    username = username.strip()
    if not username or not password or not confirm_password:
        return False, "Fields cannot be empty!"

    if password != confirm_password:
        return False, "Password and Confirm Password must match!"

    strength, _, _, missing = evaluate_password_strength(password)
    if strength != "Strong":
        return False, "Password must be Strong. Missing: " + ", ".join(missing)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, "Username already exists!"

            # A unique random salt is generated for every registered user.
            salt = os.urandom(16)
            salt_hex = binascii.hexlify(salt).decode("utf-8")
            hashed_password = hash_password(password, salt_hex)

            # Store only the username, password hash, and salt. Never store pepper.
            cursor.execute(
                "INSERT INTO users (username, hashed_password, salt) VALUES (?, ?, ?)",
                (username, hashed_password, salt_hex),
            )
            conn.commit()
            return True, "Registration Successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    except sqlite3.Error as error:
        return False, f"Database error: {error}"


def login_user(username, password):
    """Verify login by recomputing the hash with the stored salt and pepper."""
    username = username.strip()
    if not username or not password:
        return False, "Fields cannot be empty!"

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT hashed_password, salt FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()

        if row is None:
            return False, "Invalid Username or Password"

        stored_hash, stored_salt = row
        calculated_hash = hash_password(password, stored_salt)

        if hmac.compare_digest(calculated_hash, stored_hash):
            return True, "Login Successful!"
        return False, "Invalid Username or Password"
    except sqlite3.Error as error:
        return False, f"Database error: {error}"


# ==========================================
# USER INTERFACE
# ==========================================

class SecureApp(tk.Tk):
    def __init__(self):
        super().__init__()
        setup_database()

        self.title("Secure Registration and Login System")
        self.geometry("520x650")
        self.resizable(False, False)
        self.configure(bg="#eef2f7")

        self.login_password_visible = False
        self.reg_password_visible = False
        self.confirm_password_visible = False

        self._configure_styles()
        self._build_layout()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#eef2f7", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(20, 10), font=("Segoe UI", 10, "bold"))
        style.configure("TFrame", background="#ffffff")
        style.configure("Card.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("TLabel", background="#ffffff", foreground="#1f2937", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#0f172a")
        style.configure("Hint.TLabel", font=("Segoe UI", 9), foreground="#64748b")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Strength.Horizontal.TProgressbar", thickness=12)

    def _build_layout(self):
        container = ttk.Frame(self, style="Card.TFrame", padding=24)
        container.pack(fill="both", expand=True, padx=24, pady=24)

        ttk.Label(
            container,
            text="Secure Registration and Login System",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            container,
            text="Hashing, salt, pepper, and password strength validation",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(4, 18))

        self.tabs = ttk.Notebook(container)
        self.tabs.pack(fill="both", expand=True)

        self.login_tab = ttk.Frame(self.tabs, padding=18)
        self.register_tab = ttk.Frame(self.tabs, padding=18)
        self.tabs.add(self.login_tab, text="Login")
        self.tabs.add(self.register_tab, text="Register")

        self._setup_login_tab()
        self._setup_register_tab()

        self.status_label = ttk.Label(
            container,
            text="",
            font=("Segoe UI", 10, "bold"),
            wraplength=430,
        )
        self.status_label.pack(anchor="w", pady=(16, 0))

    def _field(self, parent, label_text, show=None):
        ttk.Label(parent, text=label_text, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        entry = ttk.Entry(parent, show=show, font=("Segoe UI", 10))
        entry.pack(fill="x", pady=(4, 14), ipady=5)
        return entry

    def _password_field(self, parent, label_text, toggle_command):
        ttk.Label(parent, text=label_text, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=(4, 14))

        entry = ttk.Entry(row, show="*", font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, ipady=5)

        button = ttk.Button(row, text="Show", command=toggle_command, width=8)
        button.pack(side="left", padx=(8, 0))
        return entry, button

    def _setup_login_tab(self):
        self.login_user_entry = self._field(self.login_tab, "Username")
        self.login_pass_entry, self.login_eye_btn = self._password_field(
            self.login_tab,
            "Password",
            self.toggle_login_password,
        )

        ttk.Button(
            self.login_tab,
            text="Login",
            style="Primary.TButton",
            command=self.handle_login,
        ).pack(fill="x", pady=(6, 0))

    def _setup_register_tab(self):
        self.reg_user_entry = self._field(self.register_tab, "Username")
        self.reg_pass_entry, self.reg_eye_btn = self._password_field(
            self.register_tab,
            "Password",
            self.toggle_reg_password,
        )
        self.reg_pass_entry.bind("<KeyRelease>", self.update_password_meter)

        self.confirm_pass_entry, self.confirm_eye_btn = self._password_field(
            self.register_tab,
            "Confirm Password",
            self.toggle_confirm_password,
        )

        meter = ttk.Frame(self.register_tab, padding=12, style="Card.TFrame")
        meter.pack(fill="x", pady=(0, 14))

        self.strength_label = ttk.Label(
            meter,
            text="Password Strength: Weak",
            font=("Segoe UI", 10, "bold"),
            foreground="#dc2626",
        )
        self.strength_label.pack(anchor="w")

        self.strength_progress = ttk.Progressbar(
            meter,
            style="Strength.Horizontal.TProgressbar",
            maximum=5,
            value=0,
        )
        self.strength_progress.pack(fill="x", pady=(8, 8))

        self.password_rules_label = ttk.Label(
            meter,
            text="Needs: lowercase, uppercase, number, symbol, at least 12 characters",
            style="Hint.TLabel",
            wraplength=420,
        )
        self.password_rules_label.pack(anchor="w")

        ttk.Button(
            self.register_tab,
            text="Register Account",
            style="Primary.TButton",
            command=self.handle_register,
        ).pack(fill="x")

    def handle_login(self):
        success, message = login_user(
            self.login_user_entry.get(),
            self.login_pass_entry.get(),
        )
        self.show_status(success, message)

        if success:
            self.login_user_entry.delete(0, tk.END)
            self.login_pass_entry.delete(0, tk.END)

    def handle_register(self):
        success, message = register_user(
            self.reg_user_entry.get(),
            self.reg_pass_entry.get(),
            self.confirm_pass_entry.get(),
        )
        self.show_status(success, message)

        if success:
            self.reg_user_entry.delete(0, tk.END)
            self.reg_pass_entry.delete(0, tk.END)
            self.confirm_pass_entry.delete(0, tk.END)
            self.update_password_meter()
            self.tabs.select(self.login_tab)

    def toggle_login_password(self):
        self.login_password_visible = not self.login_password_visible
        self.login_pass_entry.configure(show="" if self.login_password_visible else "*")
        self.login_eye_btn.configure(text="Hide" if self.login_password_visible else "Show")

    def toggle_reg_password(self):
        self.reg_password_visible = not self.reg_password_visible
        self.reg_pass_entry.configure(show="" if self.reg_password_visible else "*")
        self.reg_eye_btn.configure(text="Hide" if self.reg_password_visible else "Show")

    def toggle_confirm_password(self):
        self.confirm_password_visible = not self.confirm_password_visible
        self.confirm_pass_entry.configure(show="" if self.confirm_password_visible else "*")
        self.confirm_eye_btn.configure(text="Hide" if self.confirm_password_visible else "Show")

    def update_password_meter(self, event=None):
        password = self.reg_pass_entry.get()
        strength, passed, _, missing = evaluate_password_strength(password)

        if strength == "Strong":
            color = "#16a34a"
            detail = "All requirements met"
        elif strength == "Medium":
            color = "#ca8a04"
            detail = "Needs: " + ", ".join(missing)
        else:
            color = "#dc2626"
            detail = "Needs: " + ", ".join(missing)

        self.strength_label.configure(
            text=f"Password Strength: {strength}",
            foreground=color,
        )
        self.strength_progress.configure(value=passed)
        self.password_rules_label.configure(text=detail)

    def show_status(self, success, message):
        color = "#16a34a" if success else "#dc2626"
        self.status_label.configure(text=message, foreground=color)


if __name__ == "__main__":
    app = SecureApp()
    app.mainloop()
