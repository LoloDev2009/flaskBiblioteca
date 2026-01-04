from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

# Configuración de la base de datos
def database(query, params=()):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        
        # Si la consulta es un SELECT, devolvemos solo el primer resultado usando fetchone().
        if query.strip().lower().startswith("select"):
            data = cursor.fetchone()  # Obtener solo el primer resultado
        else:
            data = None  # Para otros comandos, no devolvemos datos.
        
        conn.commit()
        return data  # Devolvemos el primer resultado o None
    except Exception as e:
        conn.rollback()  # En caso de error, hacemos rollback.
        raise e  # Lanza la excepción
    finally:
        conn.close()  # Cerramos la conexión

# Inicialización de la app de Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

db = 'src/database.db'

# Crear la tabla si no existe
database('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio INTEGER,
                codigo INTEGER UNIQUE
            );
        ''')

database('''
            CREATE TABLE IF NOT EXISTS mesas (
                id_mesa INTEGER PRIMARY KEY AUTOINCREMENT,
                numero INTEGER NOT NULL UNIQUE,
                mozo INTEGER NOT NULL,
                estado TEXT DEFAULT 'libre' CHECK(estado IN ('libre', 'ocupada', 'reservada'))
            );
        ''')

database('''
            CREATE TABLE IF NOT EXISTS platos (
                id_plato INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL
            );
        ''')

database('''
            CREATE TABLE IF NOT EXISTS consumos (
                id_consumo INTEGER PRIMARY KEY AUTOINCREMENT,
                id_mesa INTEGER NOT NULL,
                id_plato INTEGER NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (id_mesa) REFERENCES mesas (id_mesa),
                FOREIGN KEY (id_plato) REFERENCES platos (id_plato)
            );
        ''')

mesaActual = None

@app.route('/facturacion')
def facturacion():
    return render_template('index.html')

@app.route('/facturacion/mesa', methods=['POST'])
def mesa():
    global mesaActual
    mesa_numero = request.form['mesa']  # Número de mesa enviado por el formulario
    try:
        # Inserta la mesa en la base de datos y asigna el número de mesa a mesaActual
        database('''INSERT INTO mesas (numero, mozo) VALUES (?, ?)''', (int(mesa_numero), 6))
        mesaActual = mesa_numero  # Asigna la mesa seleccionada a la variable global
        return'a' #ver_mesa(mesa)
    except sqlite3.IntegrityError as e:
        if str(e) in ('UNIQUE constraint failed: mesas.numero'):
            return ver_mesa(mesa_numero)



@app.route('/facturacion/mesa/cod', methods=['POST'])
def agregarPlato():
    global mesaActual  # Declara que la variable mesaActual es global
    if mesaActual is None:
        return 'No has seleccionado una mesa'
    
    # Usa mesaActual como el ID de la mesa
    id_mesa = mesaActual
    id_plato = request.form['codigo']
    if id_plato.count('*'):
        cantidad = id_plato.split('*')
        id_plato = int(cantidad[0])
        cantidad = int(cantidad[1])
    else:
        cantidad = 1
  
    try:
        database('''
        INSERT INTO consumos (id_mesa, id_plato, cantidad)
        VALUES (?, ?, ?);
    ''',(id_mesa,id_plato,cantidad))
    except:
        
        return 'Error al agregar plato'
    try:
        data = database('''
                 SELECT * FROM consumos WHERE id_mesa = ?''',(id_mesa,))
        print(data)
    except Exception as e:
        print(e)
        return 'Error al agregar plato'
    return render_template('agregarPlato.html', consumos=data)

    
def ver_mesa(mesa):
    global mesaActual
    # Aquí estamos llamando a database(), lo que devolverá una lista de resultados si es un SELECT.
    # La llamada correcta es:
    cursor = database('SELECT * FROM mesas WHERE numero = ?', (mesa,))
    
    # Usamos fetchone() para obtener un solo resultado (si se espera un solo valor para 'numero')
    mesa_data = cursor if cursor else None
    
    if mesa_data:
        mesaActual = mesa
        print(mesa_data)  # Ver los datos de la mesa
        return render_template('agregarPlato.html', data=mesa_data)  # Pasa los datos a la plantilla
    else:
        return 'Mesa no encontrada'



@app.route('/productos', methods=['POST'])
def create_product():
    try:
        nombre = request.json['name']
        precio = request.json['price']
        codigo = request.json['code']
        
        # Usar parámetros para evitar inyecciones SQL
        database('''
            INSERT INTO productos (nombre, precio, codigo) 
            VALUES (?, ?, ?)
        ''', (nombre, precio, codigo))
        
        return jsonify({'message': f'Producto {nombre} añadido correctamente.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@app.route('/productos', methods=['GET'])
def get_all_products():
    products = database('SELECT * FROM productos')
    return jsonify(products), 200

@app.route('/producto/<int:id>', methods=['GET'])
def get_product(id):
    product = database('SELECT * FROM productos WHERE codigo = ?', (id,))
    if product:
        return jsonify(product[0]), 200
    else:
        return jsonify({'message': 'Producto no encontrado'}), 404

@app.route('/producto/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        database('DELETE FROM productos WHERE codigo = ?', (id,))
        return jsonify({'message': f'Producto {id} eliminado correctamente.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/producto/<int:id>', methods=['PUT'])
def update_product(id):
    try:
        nombre = request.json.get('name')
        precio = request.json.get('price')
        codigo = request.json.get('code')

        # Actualizar el producto
        database('''
            UPDATE productos
            SET nombre = ?, precio = ?, codigo = ?
            WHERE codigo = ?9
        ''', (nombre, precio, codigo, codigo))

        return jsonify({'message': f'Producto {id} actualizado correctamente.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
