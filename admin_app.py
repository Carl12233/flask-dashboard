from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "database.db"

# --- Root / redirect to /users ---
@app.route('/')
def home():
    return "Admin-App läuft! Gehe zu /users für Übersicht."

# --- Alle User anzeigen ---
@app.route('/users')
def users():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, license_hours FROM users")
        all_users = cursor.fetchall()
    return jsonify(all_users)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
