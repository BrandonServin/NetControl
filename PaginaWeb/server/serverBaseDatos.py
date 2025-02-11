from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Obtener la ruta donde está el archivo server.py
db_path = os.path.join(basedir, 'assets', 'python','instance','baseNetControl.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'  # Ruta a la base de datos en la carpeta 'data'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f'Ruta de la base de datos: {db_path}')

db = SQLAlchemy(app)
CORS(app)  # Habilitar CORS para comunicación con el frontend


#- - - - - - - - - - - - Metodos De La Tabla Para El Apartado De Fallas - - - - - - - - - - - -
# Modelo de la base de datos
class Reportes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    prioridad = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.String(10), nullable=False)

# Ruta para obtener todos los reportes
@app.route('/reportes', methods=['GET'])
def obtener_reportes():
    reportes = Reportes.query.all()
    return jsonify([{"id": r.id, "titulo": r.titulo, "prioridad": r.prioridad, "estado": r.estado, "fecha": r.fecha} for r in reportes])

# Ruta para agregar un nuevo reporte
@app.route('/reportes', methods=['POST'])
def agregar_reporte():
    data = request.json
    nuevo_reporte = Reportes(titulo=data['titulo'], prioridad=data['prioridad'], estado=data['estado'], fecha=data['fecha'])
    db.session.add(nuevo_reporte)
    db.session.commit()
    return jsonify({"mensaje": "Reporte agregado correctamente"}), 201

# Ruta para actualizar el estado
@app.route('/reportes/<int:id>', methods=['PUT'])
def actualizar_reporte(id):
    data = request.json
    nuevo_estado = data.get("estado")

    if not nuevo_estado:
        return jsonify({"error": "Estado requerido"}), 400

    reporte = Reportes.query.get(id)

    if reporte is None:
        return jsonify({"error": "Reporte no encontrado"}), 404

    reporte.estado = nuevo_estado
    db.session.commit()

    return jsonify({"message": "Estado actualizado correctamente", "nuevo_estado": nuevo_estado}), 200

#- - - - - - - - - - - - Fin De Los Metodos De La Tabla Para El Apartado De Fallas - - - - - - - - - - - -

#- - - - - - - - - - - - Metodos De La Tabla Para El Apartado De Inventario - - - - - - - - - - - -
class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(40), nullable=False)
    noSerie = db.Column(db.String(40), nullable=False)
    ubicacion = db.Column(db.String(40), nullable=False)

# Ruta para agregar un nuevo reporte
@app.route('/inventario', methods=['POST'])
def agregar_inv():
    data = request.json
    nuevo_inv = Reportes(nombre=data['nombre'], modelo=data['modelo'], noSerie=data['noSerie'], ubicacion=data['ubicacion'])
    db.session.add(nuevo_inv)
    db.session.commit()
    return jsonify({"mensaje": "Inventario agregado correctamente"}), 201






if __name__ == '__main__':
    app.run(debug=True)
