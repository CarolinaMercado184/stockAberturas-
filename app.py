import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'

# Usamos una ruta de base de datos que Render permite escribir
DATABASE_PATH = '/tmp/aberturas.db'

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    # Crear tabla de stock
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            medida TEXT,
            material TEXT,
            cantidad INTEGER,
            usuario TEXT
        )
    ''')
    # Insertar usuarios de ejemplo (si no existen)
    users = [
        ('admin', generate_password_hash('admin123'), 'admin'),
        ('laeconomica', generate_password_hash('clave123'), 'usuario'),
        ('byg', generate_password_hash('clave123'), 'usuario')
    ]
    for u in users:
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", u)
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

# Llamamos a init_db() para crear la base de datos cada vez que se inicia la app
init_db()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[2], password):
        session['username'] = user[1]
        session['role'] = user[3]
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='Usuario o contraseña incorrectos')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock")
    datos = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', stock=datos, user=session['username'])
app = Flask(_name_)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        # Aquí va la lógica para agregar una abertura al stock
        return redirect(url_for('index'))  # Cambia 'index' si usas otra ruta principal
    return render_template('agregar.html')  # Asegúrate de que el archivo existe

if _name_ == '_main_':
    app.run(debug=True)
