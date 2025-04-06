from flask import Flask, render_template, request, redirect, url_for, session import sqlite3 from werkzeug.security import check_password_hash

app = Flask(name) app.secret_key = 'tu_clave_secreta'

DATABASE_PATH = 'stock_aberturas.db'

Inicializar base de datos si es necesario

def init_db(): conn = sqlite3.connect(DATABASE_PATH) cursor = conn.cursor() cursor.execute('''CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)''') cursor.execute('''CREATE TABLE IF NOT EXISTS stock ( id INTEGER PRIMARY KEY AUTOINCREMENT, producto TEXT NOT NULL, cantidad INTEGER NOT NULL, ubicacion TEXT NOT NULL)''') conn.commit() conn.close()

Iniciar base de datos

init_db()

@app.route('/') def login(): return render_template('login.html')

@app.route('/login', methods=['POST']) def do_login(): username = request.form['username'] password = request.form['password'] conn = sqlite3.connect(DATABASE_PATH) cursor = conn.cursor() cursor.execute("SELECT * FROM users WHERE username = ?", (username,)) user = cursor.fetchone() conn.close()

if user and check_password_hash(user[2], password):
    session['username'] = user[1]
    session['role'] = user[3]
    return redirect(url_for('dashboard'))
else:
    return render_template('login.html', error='Usuario o contraseña incorrectos')

@app.route('/dashboard', methods=['GET', 'POST']) def dashboard(): if 'username' not in session: return redirect(url_for('login'))

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

ubicacion_actual = request.form.get('ubicacion')

if ubicacion_actual and ubicacion_actual != '':
    cursor.execute("SELECT * FROM stock WHERE ubicacion = ?", (ubicacion_actual,))
else:
    cursor.execute("SELECT * FROM stock")

datos = cursor.fetchall()
conn.close()

return render_template('dashboard.html', stock=datos, user=session['username'], ubicacion_actual=ubicacion_actual)

@app.route('/agregar', methods=['GET', 'POST']) def agregar(): if 'username' not in session: return redirect(url_for('login'))

if request.method == 'POST':
    producto = request.form['producto']
    cantidad = int(request.form['cantidad'])
    ubicacion = request.form['ubicacion']

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO stock (producto, cantidad, ubicacion) VALUES (?, ?, ?)",
                   (producto, cantidad, ubicacion))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

return render_template('agregar.html')

@app.route('/logout') def logout(): session.clear() return redirect(url_for('login'))

if name == 'main': app.run(debug=True)
