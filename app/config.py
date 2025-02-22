import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    db_path = os.path.join(basedir, 'instance', 'baseNetControl.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mostrar la ruta completa de la base de datos
    print(f"Ruta de la base de datos: {db_path}")
