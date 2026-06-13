import html
import hashlib
import hmac
import os
import secrets
import sqlite3
import string
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 5000
SESSIONS = {}
PEPPER = "Sup3rS3cr3tP3pp3r!2026"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")
MIN_PASSWORD_LENGTH = 12


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def setup_database():
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
    return strength, missing


def hash_password(password, salt_hex):
    return hashlib.sha256((password + salt_hex + PEPPER).encode("utf-8")).hexdigest()


def register_user(username, password, confirm_password):
    username = username.strip()
    if not username or not password or not confirm_password:
        return False, "Fields cannot be empty!"
    if password != confirm_password:
        return False, "Password and Confirm Password must match!"

    strength, missing = evaluate_password_strength(password)
    if strength != "Strong":
        return False, "Password must be Strong. Missing: " + ", ".join(missing)

    salt_hex = os.urandom(16).hex()
    hashed_password = hash_password(password, salt_hex)

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, hashed_password, salt) VALUES (?, ?, ?)",
                (username, hashed_password, salt_hex),
            )
            conn.commit()
        return True, "Registration Successful! You can now log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    except sqlite3.Error as error:
        return False, f"Database error: {error}"


def login_user(username, password):
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
        if hmac.compare_digest(hash_password(password, stored_salt), stored_hash):
            return True, "Login Successful!"
        return False, "Invalid Username or Password"
    except sqlite3.Error as error:
        return False, f"Database error: {error}"


def render_template_file(template_name, **context):
    """Render the project templates without requiring Flask for local preview."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", template_name)
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    replacements = {
        "{{ url_for('static', filename='style.css', v='6') }}": "/static/style.css?v=6",
        "{{ url_for('static', filename='auth.js', v='6') }}": "/static/auth.js?v=6",
        "{{ url_for('static', filename='auth-hero.png', v='6') }}": "/static/auth-hero.png?v=6",
        "{{ url_for('logout') }}": "/logout",
        "{{ active_tab }}": html.escape(context.get("active_tab", "login")),
        "{{ username }}": html.escape(context.get("username", "")),
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    message = context.get("message", "")
    if message:
        message_html = (
            f'<p class="server-message {html.escape(context.get("message_type", ""))}" '
            f'data-message-tab="{html.escape(context.get("message_tab", ""))}" '
            f'role="status">{html.escape(message)}</p>'
        )
    else:
        message_html = ""

    start = content.find("{% if message %}")
    end_marker = "{% endif %}"
    end = content.find(end_marker, start)
    if start != -1 and end != -1:
        content = content[:start] + message_html + content[end + len(end_marker):]

    return content.encode("utf-8")


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        setup_database()
        path = self.path.split("?", 1)[0]

        if path == "/":
            self.respond_html(render_template_file("index.html", active_tab="login"))
            return

        if path == "/dashboard":
            username = self.current_username()
            if not username:
                self.redirect("/")
                return
            self.respond_html(render_template_file("dashboard.html", username=username))
            return

        if path == "/logout":
            session_id = self.session_id()
            if session_id in SESSIONS:
                del SESSIONS[session_id]
            self.redirect("/")
            return

        return super().do_GET()

    def do_POST(self):
        setup_database()
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        action = self.first(form, "action")
        username = self.first(form, "username")
        password = self.first(form, "password")

        if action == "register":
            success, message = register_user(username, password, self.first(form, "confirm_password"))
            message_type = "success" if success else "error"
            active_tab = "login" if success else "register"
            message_tab = "login" if success else "register"
            self.respond_html(
                render_template_file(
                    "index.html",
                    message=message,
                    message_type=message_type,
                    message_tab=message_tab,
                    active_tab=active_tab,
                )
            )
            return

        success, message = login_user(username, password)
        if success:
            self.ensure_session(username.strip())
            return

        self.respond_html(
            render_template_file(
                "index.html",
                message=message,
                message_type="error",
                message_tab="login",
                active_tab="login",
            )
        )

    def respond_html(self, body):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location):
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.end_headers()

    def first(self, form, key):
        return form.get(key, [""])[0]

    def session_id(self):
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            name, _, value = part.strip().partition("=")
            if name == "preview_session":
                return value
        return ""

    def current_username(self):
        return SESSIONS.get(self.session_id())

    def ensure_session(self, username):
        session_id = self.session_id() or secrets.token_urlsafe(24)
        SESSIONS[session_id] = username
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Set-Cookie", f"preview_session={session_id}; HttpOnly; SameSite=Lax; Path=/")
        self.send_header("Location", "/dashboard")
        self.end_headers()


if __name__ == "__main__":
    setup_database()
    print(f"Local preview running at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), PreviewHandler).serve_forever()
