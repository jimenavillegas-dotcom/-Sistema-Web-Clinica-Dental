from datetime import datetime
from extensions import db


class NotaEvolucion(db.Model):
    __tablename__ = "notas_evolucion"

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

    numero_diente = db.Column(
        db.String(5),
        nullable=True
    )

    procedimiento = db.Column(
        db.String(255),
        nullable=False
    )

    evolucion = db.Column(
        db.Text,
        nullable=False
    )

    indicaciones = db.Column(
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
            "notas_evolucion",
            lazy=True
        )
    )
