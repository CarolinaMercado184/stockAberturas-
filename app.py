from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FOLDER = 'data'
STOCK_FILE = os.path.join(DATA_FOLDER, 'stock.json')
UBICACIONES_FILE = os.path.join(DATA_FOLDER, 'ubicaciones.json')
MOVIMIENTOS_FILE = os.path.join(DATA_FOLDER, 'movimientos.json')


def leer_datos(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def escribir_datos(archivo, datos):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    stock = leer_datos(STOCK_FILE)
    ubicaciones = leer_datos(UBICACIONES_FILE)
    vista = request.args.get('vista', 'general')

    stock_por_ubicacion = {}
    for u in ubicaciones:
        nombre = u['nombre']
        stock_por_ubicacion[nombre] = [s for s in stock if s['ubicacion'] == nombre]

    return render_template('dashboard.html', stock=stock, ubicaciones=ubicaciones, vista=vista, stock_por_ubicacion=stock_por_ubicacion)

@app.route('/productos')
def productos():
    stock = leer_datos(STOCK_FILE)
    return render_template('productos.html', stock=stock)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        stock = leer_datos(STOCK_FILE)
        nuevo = {
            'id': len(stock) + 1,
            'tipo': request.form['tipo'],
            'medida': request.form['medida'],
            'color': request.form['color'],
            'cantidad': int(request.form['cantidad']),
            'ubicacion': request.form['ubicacion']
        }
        stock.append(nuevo)
        escribir_datos(STOCK_FILE, stock)
        return redirect(url_for('dashboard'))
    ubicaciones = leer_datos(UBICACIONES_FILE)
    return render_template('agregar.html', ubicaciones=ubicaciones)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    stock = leer_datos(STOCK_FILE)
    producto = next((p for p in stock if p['id'] == id), None)
    if request.method == 'POST':
        producto['tipo'] = request.form['tipo']
        producto['medida'] = request.form['medida']
        producto['color'] = request.form['color']
        producto['cantidad'] = int(request.form['cantidad'])
        producto['ubicacion'] = request.form['ubicacion']
        escribir_datos(STOCK_FILE, stock)
        return redirect(url_for('dashboard'))
    ubicaciones = leer_datos(UBICACIONES_FILE)
    return render_template('editar.html', producto=producto, ubicaciones=ubicaciones)

@app.route('/nuevo_movimiento', methods=['GET', 'POST'])
def nuevo_movimiento():
    if request.method == 'POST':
        movimientos = leer_datos(MOVIMIENTOS_FILE)
        stock = leer_datos(STOCK_FILE)

        tipo = request.form['tipo']
        medida = request.form['medida']
        color = request.form['color']
        origen = request.form['origen']
        destino = request.form['destino']
        cantidad = int(request.form['cantidad'])

        # actualizar stock
        for item in stock:
            if item['tipo'] == tipo and item['medida'] == medida and item['color'] == color:
                if item['ubicacion'] == origen:
                    item['cantidad'] -= cantidad
                elif item['ubicacion'] == destino:
                    item['cantidad'] += cantidad

        escribir_datos(STOCK_FILE, stock)

        # guardar movimiento
        movimiento = {
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tipo': tipo,
            'medida': medida,
            'color': color,
            'origen': origen,
            'destino': destino,
            'cantidad': cantidad
        }
        movimientos.append(movimiento)
        escribir_datos(MOVIMIENTOS_FILE, movimientos)

        return redirect(url_for('dashboard'))

    stock = leer_datos(STOCK_FILE)
    ubicaciones = leer_datos(UBICACIONES_FILE)
    tipos = list(set(item['tipo'] for item in stock))
