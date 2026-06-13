import binascii
import hashlib
import hmac
import os
import sqlite3
import string

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-for-deployment")

PEPPER = "Sup3rS3cr3tP3pp3r!2026"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")
MIN_PASSWORD_LENGTH = 12


def get_connection():
    """Create a SQLite connection for the users database."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def setup_database():
    """Create the required users table."""
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
    """Check lowercase, uppercase, digit, symbol, and minimum length rules."""
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
    return strength, passed, missing


def hash_password(password, salt_hex):
    """Hash password + salt + pepper using SHA-256."""
    combined_string = password + salt_hex + PEPPER
    return hashlib.sha256(combined_string.encode("utf-8")).hexdigest()


def register_user(username, password, confirm_password):
    """Register a user only after all password rules pass."""
    username = username.strip()
    if not username or not password or not confirm_password:
        return False, "Fields cannot be empty!"

    if password != confirm_password:
        return False, "Password and Confirm Password must match!"

    strength, _, missing = evaluate_password_strength(password)
    if strength != "Strong":
        return False, "Password must be Strong. Missing: " + ", ".join(missing)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, "Username already exists!"

            salt = os.urandom(16)
            salt_hex = binascii.hexlify(salt).decode("utf-8")
            hashed_password = hash_password(password, salt_hex)

            cursor.execute(
                "INSERT INTO users (username, hashed_password, salt) VALUES (?, ?, ?)",
                (username, hashed_password, salt_hex),
            )
            conn.commit()
            return True, "Registration Successful!"
    except sqlite3.Error as error:
        return False, f"Database error: {error}"


def login_user(username, password):
    """Validate login by recomputing the stored password hash."""
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


@app.route("/", methods=["GET", "POST"])
def index():
    setup_database()
    message = ""
    message_type = ""
    message_tab = ""
    active_tab = "login"

    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if action == "register":
            active_tab = "register"
            message_tab = "register"
            confirm_password = request.form.get("confirm_password", "")
            success, message = register_user(username, password, confirm_password)
        else:
            message_tab = "login"
            success, message = login_user(username, password)

        if success and action == "login":
            session["username"] = username.strip()
            return redirect(url_for("dashboard"))

        message_type = "success" if success else "error"
        if success and action == "register":
            active_tab = "login"
            message_tab = "login"

    return render_template(
        "index.html",
        message=message,
        message_type=message_type,
        message_tab=message_tab,
        active_tab=active_tab,
    )


@app.route("/dashboard")
def dashboard():
    username = session.get("username")
    if not username:
        return redirect(url_for("index"))

    return render_template("dashboard.html", username=username)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
