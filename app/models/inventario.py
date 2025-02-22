from .database import db

class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(40), nullable=False)
    noSerie = db.Column(db.String(40), nullable=False)
    cantidad = db.Column(db.String(40), nullable=False)
    ubicacion = db.Column(db.String(40), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
