from datetime import datetime
from extensions import db


class Tratamiento(db.Model):
    __tablename__ = "tratamientos"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("pacientes.id"),
        nullable=False
    )

    numero_diente = db.Column(
        db.String(5),
        nullable=True
    )

    diagnostico = db.Column(
        db.String(200),
        nullable=False
    )

    procedimiento = db.Column(
        db.String(200),
        nullable=False
    )

    prioridad = db.Column(
        db.String(20),
        nullable=True
    )

    estado = db.Column(
        db.String(30),
        nullable=False,
        default="Pendiente"
    )

    costo = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.now
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    paciente = db.relationship(
        "Paciente",
        backref=db.backref(
            "tratamientos",
            lazy=True
        )
    )