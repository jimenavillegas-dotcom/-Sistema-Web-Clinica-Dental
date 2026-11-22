from extensions import db


class Rol(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    descripcion = db.Column(
        db.String(200),
        nullable=True
    )