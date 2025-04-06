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
    for item in stock:
        key = (item['tipo'], item['medida'], item['color'])
        for ubicacion, cantidad in item['stock'].items():
            if ubicacion not in stock_por_ubicacion:
                stock_por_ubicacion[ubicacion] = {}
            if key not in stock_por_ubicacion[ubicacion]:
                stock_por_ubicacion[ubicacion][key] = 0
            stock_por_ubicacion[ubicacion][key] += cantidad

    if vista == 'general':
        stock_general = {}
        for item in stock:
            key = (item['tipo'], item['medida'], item['color'])
            stock_general[key] = stock_general.get(key, 0) + sum(item['stock'].values())
        return render_template('dashboard.html', stock_general=stock_general, vista=vista)
    else:
        return render_template('dashboard.html', stock_por_ubicacion=stock_por_ubicacion, ubicaciones=ubicaciones, vista=vista)


@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo_movimiento():
    if request.method == 'POST':
        tipo = request.form['tipo']
        medida = request.form['medida']
        color = request.form['color']
        origen = request.form['origen']
        destino = request.form['destino']
        cantidad = int(request.form['cantidad'])

        stock = leer_datos(STOCK_FILE)
        movimientos = leer_datos(MOVIMIENTOS_FILE)

        encontrado = False
        for item in stock:
            if item['tipo'] == tipo and item['medida'] == medida and item['color'] == color:
                if origen in item['stock']:
                    item['stock'][origen] -= cantidad
                else:
                    item['stock'][origen] = 0
                if destino in item['stock']:
                    item['stock'][destino] += cantidad
                else:
                    item['stock'][destino] = cantidad
                encontrado = True
                break

        if not encontrado:
            item = {
                'tipo': tipo,
                'medida': medida,
                'color': color,
                'stock': {
                    origen: 0,
                    destino: cantidad
                }
            }
            stock.append(item)

        escribir_datos(STOCK_FILE, stock)

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
    medidas = list(set(item['medida'] for item in stock))
    colores = list(set(item['color'] for item in stock))

    return render_template('nuevo_movimiento.html', tipos=tipos, medidas=medidas, colores=colores, ubicaciones=ubicaciones)


if __name__ == '__main__':
    app.run(debug=True)
