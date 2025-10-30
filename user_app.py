from flask import Flask, request, render_template_string, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secure_user_secret"
DB = "database.db"

# --- DB Helper
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# --- Routes
@app.route("/")
def index():
    return '<h2>Willkommen</h2><a href="/register">Registrieren</a> | <a href="/login">Login</a>'

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u = request.form["username"].strip()
        p = request.form["password"]
        key = request.form["license_key"].strip()
        conn = get_db()
        if conn.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone():
            flash("Benutzername existiert!")
            return redirect(url_for("register"))
        lic = conn.execute("SELECT * FROM licenses WHERE key=?", (key,)).fetchone()
        if not lic:
            flash("Ungültiger Lizenz-Key")
            return redirect(url_for("register"))
        expires = datetime.fromisoformat(lic["expires_at"])
        if expires < datetime.utcnow():
            flash("Lizenz abgelaufen")
            return redirect(url_for("register"))
        pw_hash = generate_password_hash(p)
        conn.execute("INSERT INTO users (username,password_hash,license_id) VALUES (?,?,?)",(u,pw_hash,lic["id"]))
        conn.commit()
        conn.close()
        flash("Registrierung erfolgreich!")
        return redirect(url_for("login"))
    return '''
    <h2>Registrieren</h2>
    <form method="post">
    Benutzername: <input name="username"><br>
    Passwort: <input name="password" type="password"><br>
    Lizenz-Key: <input name="license_key"><br>
    <button type="submit">Registrieren</button>
    </form>
    '''

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"].strip()
        p=request.form["password"]
        conn=get_db()
        user=conn.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone()
        conn.close()
        if not user or not check_password_hash(user["password_hash"],p):
            flash("Benutzername oder Passwort falsch")
            return redirect(url_for("login"))
        session.clear()
        session["user_id"]=user["id"]
        return redirect(url_for("dashboard"))
    return '''
    <h2>Login</h2>
    <form method="post">
    Benutzername: <input name="username"><br>
    Passwort: <input name="password" type="password"><br>
    <button type="submit">Login</button>
    </form>
    '''

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Bitte einloggen")
        return redirect(url_for("login"))
    uid=session["user_id"]
    conn=get_db()
    user=conn.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone()
    lic=None
    hours_left=None
    if user["license_id"]:
        lic=conn.execute("SELECT * FROM licenses WHERE id=?",(user["license_id"],)).fetchone()
        if lic:
            delta=datetime.fromisoformat(lic["expires_at"])-datetime.utcnow()
            hours_left=round(delta.total_seconds()/3600,2)
    conn.close()
    return f'''
    <h2>Dashboard</h2>
    Willkommen, {user["username"]} | <a href="/logout">Logout</a><br>
    Lizenz: {lic["key"] if lic else "keine"}<br>
    Verbleibende Stunden: {hours_left if hours_left else "0"}<br>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__=="__main__":
    app.run(debug=True, port=5050)
