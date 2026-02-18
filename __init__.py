from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3


# app.py
from flask import Flask, request, jsonify
import sqlite3


app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html') #Comm2

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))

  # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Vérifier les identifiants
        if request.form['username'] == 'admin' and request.form['password'] == 'password': # password à cacher par la suite
            session['authentifie'] = True
            # Rediriger vers la route lecture après une authentification réussie
            return redirect(url_for('lecture'))
        else:
            # Afficher un message d'erreur si les identifiants sont incorrects
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Rediriger vers la page d'accueil après l'enregistrement


# --- Authentification "user" de l'exercice 2 ---
def check_user_auth(username, password):
    return username == "user" and password == "12345"

# (Optionnel) Route d'accueil
@app.route('/')
def hello():
    return "Hello World!"

# --- Nouvelle route : /fiche_nom/ ---
@app.route('/fiche_nom/', methods=['GET'])
def fiche_nom():
    # On récupère les paramètres ?username=...&password=...&nom=...
    username = request.args.get('username')
    password = request.args.get('password')
    nom = request.args.get('nom')  # le nom du client à rechercher

    # Contrôle d'accès (exercice 2) : user / 12345
    if not check_user_auth(username, password):
        return jsonify({"error": "Accès refusé"}), 403

    if not nom:
        return jsonify({"error": "Paramètre 'nom' manquant"}), 400

    # Connexion à la base SQLite
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Recherche exacte sur le nom — requête paramétrée (sécurisée)
    cur.execute("SELECT id, nom, email FROM clients WHERE nom = ?", (nom,))
    rows = cur.fetchall()
    conn.close()

    # Formatage du résultat en JSON
    clients = [{"id": r[0], "nom": r[1], "email": r[2]} for r in rows]

    if clients:
        return jsonify({"clients": clients}), 200
    else:
        return jsonify({"message": "Aucun client trouvé"}), 200


@app.route("/tasks")
def list_tasks():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = c.fetchall()
    conn.close()
    return render_template("tasks_list.html", tasks=tasks)

@app.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        deadline = request.form["deadline"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO tasks (title, description, deadline) VALUES (?, ?, ?)",
                  (title, description, deadline))
        conn.commit()
        conn.close()

        return redirect("/tasks")

    return render_template("tasks_add.html")

@app.route("/tasks/delete/<int:task_id>")
def tasks_delete(task_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/tasks")

@app.route("/tasks/complete/<int:task_id>")
def tasks_complete(task_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/tasks")

# Lancement local (utile si tu testes en local)
if __name__ == "__main__":
    app.run(debug=True)
