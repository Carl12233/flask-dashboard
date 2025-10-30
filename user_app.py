from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "database.db"

# --- Root / redirect to login ---
@app.route('/')
def home():
    return redirect(url_for('login'))

# --- Login-Seite ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
        if user:
            return f"Willkommen {username}! Dein Lizenz-Key ist gültig für {user[3]} Stunden."
        else:
            return "Login fehlgeschlagen."
    return render_template('login.html')

# --- Registrieren-Seite ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        license_key = request.form['license_key']
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, license_hours) VALUES (?, ?, ?)",
                           (username, password, 24))  # z.B. 24 Stunden Lizenz
            conn.commit()
        return "Registrierung erfolgreich!"
    return render_template('register.html')

# --- DB Initialisierung ---
def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                license_hours INTEGER
            )
            """)
            conn.commit()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
