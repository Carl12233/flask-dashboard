from flask import Flask, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta

app=Flask(__name__)
app.secret_key="secure_admin_secret"
DB="database.db"

def get_db():
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row
    return conn

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"].strip()
        p=request.form["password"]
        conn=get_db()
        admin=conn.execute("SELECT * FROM admins WHERE username=?",(u,)).fetchone()
        conn.close()
        if not admin or not check_password_hash(admin["password_hash"],p):
            flash("Adminname oder Passwort falsch")
            return redirect(url_for("login"))
        session.clear()
        session["admin_id"]=admin["id"]
        return redirect(url_for("dashboard"))
    return '''
    <h2>Admin Login</h2>
    <form method="post">
    Benutzername: <input name="username"><br>
    Passwort: <input name="password" type="password"><br>
    <button type="submit">Login</button>
    </form>
    '''

@app.route("/dashboard")
def dashboard():
    if "admin_id" not in session:
        flash("Bitte einloggen")
        return redirect(url_for("login"))
    conn=get_db()
    keys=conn.execute("SELECT * FROM licenses").fetchall()
    conn.close()
    html="<h2>Admin Dashboard</h2><a href='/logout'>Logout</a><br><h3>Lizenz-Keys</h3>"
    for k in keys:
        html+=f"Key: {k['key']}, expires at: {k['expires_at']}<br>"
    html+="<h3>Neuen Key erstellen</h3><form method='post' action='/create_key'>Key: <input name='key'> Stunden: <input name='hours'> <button type='submit'>Erstellen</button></form>"
    return html

@app.route("/create_key", methods=["POST"])
def create_key():
    if "admin_id" not in session:
        flash("Bitte einloggen")
        return redirect(url_for("login"))
    key=request.form["key"].strip()
    hours=int(request.form.get("hours",24))
    expires=(datetime.utcnow()+timedelta(hours=hours)).isoformat()
    conn=get_db()
    try:
        conn.execute("INSERT INTO licenses (key,expires_at) VALUES (?,?)",(key,expires))
        conn.commit()
    except:
        flash("Key existiert bereits")
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True, port=5051)
