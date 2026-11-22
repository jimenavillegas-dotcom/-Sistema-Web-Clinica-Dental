from datetime import datetime
from extensions import db


class OdontogramaDetalle(db.Model):
    __tablename__ = "odontograma_detalles"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("pacientes.id"),
        nullable=False
    )

    numero_diente = db.Column(
        db.String(5),
        nullable=False
    )

    superficie = db.Column(
        db.String(30),
        nullable=False,
        default="General"
    )

    estado = db.Column(
        db.String(50),
        nullable=False,
        default="Sano"
    )

    procedimiento = db.Column(
        db.String(150),
        nullable=True
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    costo = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    prioridad = db.Column(
        db.String(20),
        nullable=True
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    paciente = db.relationship(
        "Paciente",
        backref=db.backref(
            "odontograma_detalles",
            lazy=True
        )
    )

    __table_args__ = (
        db.UniqueConstraint(
            "paciente_id",
            "numero_diente",
            "superficie",
            name="uq_paciente_diente_superficie"
        ),
    )


class OdontogramaHistorial(db.Model):
    __tablename__ = "odontograma_historial"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("pacientes.id"),
        nullable=False
    )

    numero_diente = db.Column(
        db.String(5),
        nullable=False
    )

    superficie = db.Column(
        db.String(30),
        nullable=False
    )

    estado_anterior = db.Column(
        db.String(50),
        nullable=True
    )

    estado_nuevo = db.Column(
        db.String(50),
        nullable=False
    )

    procedimiento = db.Column(
        db.String(150),
        nullable=True
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.now
    )