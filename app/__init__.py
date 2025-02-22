from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config

# Importar db desde database.py
from .models.database import db  

def create_app():
    """Función para crear la aplicación de Flask."""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)  # Cargar configuración desde config.py
    
    # Inicializar extensiones con la app
    db.init_app(app)  # Se registra la base de datos correctamente
    CORS(app)

    # Importamos y registramos las rutas después de inicializar `db`
    from .routes import main
    app.register_blueprint(main)

    return app
