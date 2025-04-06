import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'

DATABASE_PATH = '/tmp/aberturas.db'
if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)
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
# Crear tabla de ubicaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ubicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE
        )
    ''')

    # Insertar sucursales y galpón si no existen
    cursor.execute("INSERT OR IGNORE INTO ubicaciones (id, nombre) VALUES (1, 'BYG')")
    cursor.execute("INSERT OR IGNORE INTO ubicaciones (id, nombre) VALUES (2, 'LA ECONÓMICA')")
    cursor.execute("INSERT OR IGNORE INTO ubicaciones (id, nombre) VALUES (3, 'GALPÓN')")
    # Crear tabla de stock
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            medida TEXT,
            material TEXT,
            cantidad INTEGER,
            usuario TEXT
            ubicacion_id INTEGER
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
            pass  # Ya existe el usuario

    conn.commit()
    conn.close()

# Inicializar base de datos
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
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    ubicacion_seleccionada = request.form.get('ubicacion')

    if ubicacion_seleccionada:
        cursor.execute("SELECT * FROM stock WHERE ubicacion = ?", (ubicacion_seleccionada,))
    else:
        cursor.execute("SELECT * FROM stock")

    stock = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', stock=stock, ubicacion_actual=ubicacion_seleccionada)
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

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        tipo = request.form['tipo']
        medida = request.form['medida']
        material = request.form['material']
        cantidad = int(request.form['cantidad'])
        usuario = session['username']
ubicacion_id = int(request.form['ubicacion_id'])
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
     cursor.execute('''
    INSERT INTO stock (tipo, medida, material, cantidad, usuario, ubicacion_id)
    VALUES (?, ?, ?, ?, ?, ?)
''', (tipo, medida, material, cantidad, usuario, ubicacion_id))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('agregar.html')

if __name__ == '__main__':
    app.run(debug=True)
