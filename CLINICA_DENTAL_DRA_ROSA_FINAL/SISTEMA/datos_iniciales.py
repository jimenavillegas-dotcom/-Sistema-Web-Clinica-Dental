from app import app
from extensions import db
from models import Rol


with app.app_context():

    roles = [
        ("Administrador", "Acceso completo al sistema"),
        ("Dentista", "Acceso a funciones clínicas y tratamientos"),
        ("Recepcionista", "Acceso a pacientes, citas y pagos")
    ]

    for nombre, descripcion in roles:

        rol_existente = Rol.query.filter_by(nombre=nombre).first()

        if not rol_existente:
            nuevo_rol = Rol(
                nombre=nombre,
                descripcion=descripcion
            )

            db.session.add(nuevo_rol)

    db.session.commit()

    print("Roles creados correctamente.")