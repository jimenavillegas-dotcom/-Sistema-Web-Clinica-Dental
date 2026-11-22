from extensions import db
from datetime import datetime


class Paciente(db.Model):
    __tablename__ = "pacientes"

    id = db.Column(db.Integer, primary_key=True)

    numero_historia = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    apellidos = db.Column(
        db.String(150),
        nullable=False
    )

    documento_identidad = db.Column(
        db.String(50),
        nullable=True,
        unique=True
    )

    fecha_nacimiento = db.Column(
        db.Date,
        nullable=False
    )

    genero = db.Column(
        db.String(30),
        nullable=False
    )

    lugar_nacimiento = db.Column(
        db.String(150),
        nullable=True
    )

    domicilio = db.Column(
        db.String(250),
        nullable=True
    )

    ocupacion = db.Column(
        db.String(120),
        nullable=True
    )

    escolaridad = db.Column(
        db.String(100),
        nullable=True
    )

    estado_civil = db.Column(
        db.String(50),
        nullable=True
    )

    telefono = db.Column(
        db.String(20),
        nullable=True
    )

    correo = db.Column(
        db.String(150),
        nullable=True
    )

    motivo_consulta = db.Column(
        db.Text,
        nullable=True
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.now
    )