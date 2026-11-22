from datetime import datetime
from extensions import db


class Cita(db.Model):
    __tablename__ = "citas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("pacientes.id"),
        nullable=False
    )

    tratamiento_id = db.Column(
        db.Integer,
        db.ForeignKey("tratamientos.id"),
        nullable=True
    )

    fecha = db.Column(
        db.Date,
        nullable=False
    )

    hora = db.Column(
        db.Time,
        nullable=False
    )

    motivo = db.Column(
        db.String(200),
        nullable=False
    )

    odontologo = db.Column(
        db.String(150),
        nullable=True
    )

    estado = db.Column(
        db.String(30),
        nullable=False,
        default="Programada"
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.now
    )

    paciente = db.relationship(
        "Paciente",
        backref=db.backref(
            "citas",
            lazy=True
        )
    )

    tratamiento = db.relationship(
        "Tratamiento",
        backref=db.backref(
            "citas",
            lazy=True
        )
    )