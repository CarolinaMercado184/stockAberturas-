
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'

def init_db():
    conn = sqlite3.connect('aberturas.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS stock (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT,
                        medida TEXT,
                        material TEXT,
                        cantidad INTEGER,
                        usuario TEXT)''')
    users = [
        ('admin', 'scrypt:32768:8:1$3YQJVfX3JNuuMwmc$fc6f435994816f8b827e32e9cfd52ada64f8c8d5f3045b65d310c39cbc29c9337e3f749e7c4cff34f16ee8028786c5e9ae863e92997916da718e25851f9ecdb6', 'admin'),
        ('laeconomica', 'scrypt:32768:8:1$AM7zIbBJJbc7fNBU$29bac08df894937396e5a1b8cef5da813571a328abc42cf057fddb93649b665f814b16ce07d3b7a12f6facf5514a47389a08a132820f756683f7ae97f1294cf1', 'usuario'),
        ('byg', 'scrypt:32768:8:1$eemPP42JU7gpbGV5$c8c41c74f000067e1c0cacdb2585bfe4766d9077c96588ab4dd5da1ac5a599c8ddd6bab28efb097e938291baa04fdd419694711b631363fff03edcc7a8f20fc9', 'usuario')
    ]
    for u in users:
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", u)
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('aberturas.db')
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('aberturas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock")
    datos = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', stock=datos, user=session['username'])

@app.route('/agregar', methods=['POST'])
def agregar():
    if 'username' not in session:
        return redirect(url_for('login'))
    tipo = request.form['tipo']
    medida = request.form['medida']
    material = request.form['material']
    cantidad = int(request.form['cantidad'])
    usuario = session['username']
    conn = sqlite3.connect('aberturas.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO stock (tipo, medida, material, cantidad, usuario) VALUES (?, ?, ?, ?, ?)",
                   (tipo, medida, material, cantidad, usuario))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/sumar/<int:id>')
def sumar(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('aberturas.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE stock SET cantidad = cantidad + 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/restar/<int:id>')
def restar(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('aberturas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT cantidad FROM stock WHERE id = ?", (id,))
    actual = cursor.fetchone()[0]
    if actual > 0:
        cursor.execute("UPDATE stock SET cantidad = cantidad - 1 WHERE id = ?", (id,))
        conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
