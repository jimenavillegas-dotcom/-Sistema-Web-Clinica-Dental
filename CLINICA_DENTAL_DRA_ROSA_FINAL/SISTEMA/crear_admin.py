import os

from app import app
from extensions import db
from models import Rol, Usuario
from werkzeug.security import generate_password_hash


with app.app_context():

    rol_admin = Rol.query.filter_by(nombre="Administrador").first()

    if not rol_admin:
        print("Primero debes ejecutar datos_iniciales.py")
    else:

        correo = "admin@dental.com"

        usuario_existente = Usuario.query.filter_by(correo=correo).first()

        if usuario_existente:
            print("El administrador ya existe.")

        else:

            nuevo_admin = Usuario(
                nombre="Administrador",
                apellidos="Sistema",
                correo=correo,
                password=generate_password_hash(os.environ["ADMIN_PASSWORD"]),
                activo=True,
                rol_id=rol_admin.id
            )

            db.session.add(nuevo_admin)
            db.session.commit()

            print("Administrador creado correctamente.")