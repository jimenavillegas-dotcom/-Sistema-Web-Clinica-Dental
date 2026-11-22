from datetime import datetime
from extensions import db


class Consentimiento(db.Model):
    __tablename__ = "consentimientos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("pacientes.id"),
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )

    tipo = db.Column(
        db.String(150),
        nullable=False
    )

    procedimiento = db.Column(
        db.String(255),
        nullable=True
    )

    contenido = db.Column(
        db.Text,
        nullable=False
    )

    firmado_paciente = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    nombre_paciente = db.Column(
        db.String(200),
        nullable=True
    )

    firma_paciente = db.Column(
        db.Text,
        nullable=True
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    paciente = db.relationship(
        "Paciente",
        backref=db.backref(
            "consentimientos",
            lazy=True
        )
    )
