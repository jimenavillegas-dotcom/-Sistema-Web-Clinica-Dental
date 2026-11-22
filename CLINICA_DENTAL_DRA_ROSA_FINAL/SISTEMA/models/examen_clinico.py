from datetime import datetime
from extensions import db


class ExamenClinico(db.Model):
    __tablename__ = "examenes_clinicos"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("pacientes.id"),
        nullable=False,
        unique=True
    )

    # Cara
    cara_estado = db.Column(db.String(20), nullable=True)
    cara_observaciones = db.Column(db.Text, nullable=True)

    # Cuello
    cuello_estado = db.Column(db.String(20), nullable=True)
    cuello_observaciones = db.Column(db.Text, nullable=True)

    # Labios
    labios_estado = db.Column(db.String(20), nullable=True)
    labios_observaciones = db.Column(db.Text, nullable=True)

    # Carrillos
    carrillos_estado = db.Column(db.String(20), nullable=True)
    carrillos_observaciones = db.Column(db.Text, nullable=True)

    # Paladar blando
    paladar_blando_estado = db.Column(db.String(20), nullable=True)
    paladar_blando_observaciones = db.Column(db.Text, nullable=True)

    # Paladar duro
    paladar_duro_estado = db.Column(db.String(20), nullable=True)
    paladar_duro_observaciones = db.Column(db.Text, nullable=True)

    # Lengua
    lengua_estado = db.Column(db.String(20), nullable=True)
    lengua_observaciones = db.Column(db.Text, nullable=True)

    # Amígdalas
    amigdalas_estado = db.Column(db.String(20), nullable=True)
    amigdalas_observaciones = db.Column(db.Text, nullable=True)

    # Piso de boca
    piso_boca_estado = db.Column(db.String(20), nullable=True)
    piso_boca_observaciones = db.Column(db.Text, nullable=True)

    # Glándulas salivales
    glandulas_salivales_estado = db.Column(db.String(20), nullable=True)
    glandulas_salivales_observaciones = db.Column(db.Text, nullable=True)

    # ATM
    atm_estado = db.Column(db.String(20), nullable=True)
    atm_observaciones = db.Column(db.Text, nullable=True)

    # Oclusión
    oclusion_estado = db.Column(db.String(20), nullable=True)
    oclusion_observaciones = db.Column(db.Text, nullable=True)

    # Observaciones generales
    observaciones_generales = db.Column(
        db.Text,
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
            "examen_clinico",
            uselist=False
        )
    )