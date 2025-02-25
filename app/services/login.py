from flask import jsonify
from app.models.login import Login

def iniciar_sesion(data):
    usuario = data.get("usuario")
    password = data.get("password")

    # Buscar el usuario en la base de datos
    user = Login.query.filter_by(usuario=usuario).first()

    if user and user.password == password:
        return jsonify({"success": True, "message": "Inicio de sesión exitoso"})
    else:
        return jsonify({"success": False, "message": "Usuario o contraseña incorrectos"}), 401
