from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)
DATABASE = "datenbank.db"

# --- Datenbankverbindung ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Startseite mit HTML-Formular ---
@app.route("/")
def index():
    html = """
    <!doctype html>
    <html lang="de">
    <head>
        <meta charset="utf-8">
        <title>Mein Mini-Dashboard</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f9f9f9; }
            h1 { color: #333; }
            form { margin-bottom: 20px; }
            input, button { padding: 8px; margin: 5px; }
            table { border-collapse: collapse; width: 50%; background: white; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #eee; }
        </style>
    </head>
    <body>
        <h1>📊 Mein Mini-Dashboard</h1>
        <form id="dataForm">
            <input type="text" id="name" placeholder="Name" required>
            <input type="text" id="wert" placeholder="Wert" required>
            <button type="submit">Speichern</button>
        </form>

        <table id="dataTable">
            <thead><tr><th>ID</th><th>Name</th><th>Wert</th></tr></thead>
            <tbody></tbody>
        </table>

        <script>
            async function ladeDaten() {
                const res = await fetch("/daten");
                const daten = await res.json();
                const tbody = document.querySelector("#dataTable tbody");
                tbody.innerHTML = "";
                daten.forEach(d => {
                    tbody.innerHTML += `<tr><td>${d.id}</td><td>${d.name}</td><td>${d.wert}</td></tr>`;
                });
            }

            document.querySelector("#dataForm").addEventListener("submit", async (e) => {
                e.preventDefault();
                const name = document.querySelector("#name").value;
                const wert = document.querySelector("#wert").value;
                await fetch("/daten", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({name, wert})
                });
                document.querySelector("#name").value = "";
                document.querySelector("#wert").value = "";
                ladeDaten();
            });

            ladeDaten();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

# --- API: Daten abrufen ---
@app.route("/daten", methods=["GET"])
def get_daten():
    conn = get_db()
    daten = conn.execute("SELECT * FROM eintraege").fetchall()
    conn.close()
    return jsonify([dict(row) for row in daten])

# --- API: Daten hinzufügen ---
@app.route("/daten", methods=["POST"])
def add_daten():
    data = request.get_json()
    name = data.get("name")
    wert = data.get("wert")

    conn = get_db()
    conn.execute("INSERT INTO eintraege (name, wert) VALUES (?, ?)", (name, wert))
    conn.commit()
    conn.close()
    return jsonify({"message": "Eintrag hinzugefügt!"}), 201

# --- Datenbank anlegen, falls sie fehlt ---
if __name__ == "__main__":
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS eintraege (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            wert TEXT NOT NULL
        )
    """)
    conn.close()

    app.run(debug=True, port=5050)
