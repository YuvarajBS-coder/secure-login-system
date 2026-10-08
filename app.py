from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import bcrypt
import pyotp
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")
DATABASE = "users.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            totp_secret TEXT
        )
    """)
    conn.commit()
    conn.close()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3:
            flash("Username must contain at least 3 characters.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return render_template("register.html")

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")
            conn.close()
            return render_template("register.html")
        conn.close()

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])

@app.route("/setup-2fa", methods=["GET", "POST"])
@login_required
def setup_2fa():
    conn = get_db()
    user = conn.execute(
        "SELECT totp_secret FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if not user["totp_secret"]:
        secret = pyotp.random_base32()
        conn.execute(
            "UPDATE users SET totp_secret = ? WHERE id = ?",
            (secret, session["user_id"])
        )
        conn.commit()
    else:
        secret = user["totp_secret"]

    conn.close()

    otp_uri = pyotp.TOTP(secret).provisioning_uri(
        name=session["username"],
        issuer_name="Secure Login System"
    )

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        if pyotp.TOTP(secret).verify(code):
            session["two_fa_verified"] = True
            flash("Two-factor authentication verified successfully.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid authentication code.", "danger")

    return render_template("setup_2fa.html", secret=secret, otp_uri=otp_uri)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
