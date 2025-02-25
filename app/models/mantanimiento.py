from .database import db

# Modelo de la tabla Plans
class Mantenimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    file_name = db.Column(db.String(255))
    file_data = db.Column(db.LargeBinary)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "file_name": self.file_name,
        }