from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baseNetControl.db'  # Base de datos SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definir el modelo de la tabla Reporte
class Reportes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    prioridad = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'Reporte({self.id}, {self.titulo}, {self.prioridad}, {self.estado}, {self.fecha})'
    
# Definir el modelo de la tabla inventario
class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(40), nullable=False)
    noSerie = db.Column(db.String(40), nullable=False)
    ubicacion = db.Column(db.String(40), nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'Reporte({self.id}, {self.nombre}, {self.modelo}, {self.noSerie}, {self.ubicacion}, {self.estado})'

# Crear la base de datos y las tablas
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos creada exitosamente.")
