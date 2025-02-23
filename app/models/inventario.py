from .database import db

class UnidadActiva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventario_id = db.Column(db.Integer, db.ForeignKey('inventario.id'), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    inventario = db.relationship('Inventario', backref=db.backref('unidades_activas', lazy=True))

class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    noSerie = db.Column(db.String(100), unique=True, nullable=False)
    cantidadTotal = db.Column(db.Integer, nullable=False, default=0)
    cantidadActiva = db.Column(db.Integer, nullable=False, default=0)
    cantidadInventario = db.Column(db.Integer, nullable=False, default=0)
    ubicacion = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False)

