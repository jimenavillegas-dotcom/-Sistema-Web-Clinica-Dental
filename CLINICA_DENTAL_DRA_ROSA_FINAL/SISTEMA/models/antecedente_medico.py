from datetime import datetime
from extensions import db


class AntecedenteMedico(db.Model):
    __tablename__ = "antecedentes_medicos"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(
        db.Integer,
        db.ForeignKey("pacientes.id"),
        nullable=False,
        unique=True
    )

    # Hábitos
    tabaquismo = db.Column(db.Boolean, default=False)
    alcohol = db.Column(db.Boolean, default=False)
    otras_sustancias = db.Column(db.Boolean, default=False)
    detalle_sustancias = db.Column(db.String(250), nullable=True)
    habito_oral = db.Column(db.String(250), nullable=True)

    # Estado médico actual
    enfermedad_ultimo_anio = db.Column(db.Boolean, default=False)
    detalle_enfermedad = db.Column(db.Text, nullable=True)

    tratamiento_medico = db.Column(db.Boolean, default=False)
    detalle_tratamiento = db.Column(db.Text, nullable=True)

    alergias = db.Column(db.Boolean, default=False)
    detalle_alergias = db.Column(db.Text, nullable=True)

    # Anestesia y hemorragias
    anestesia_previa = db.Column(db.Boolean, default=False)
    reaccion_anestesia = db.Column(db.Boolean, default=False)
    detalle_reaccion_anestesia = db.Column(db.Text, nullable=True)

    sangrado_excesivo = db.Column(db.Boolean, default=False)
    sitio_sangrado = db.Column(db.String(250), nullable=True)

    # Antecedentes personales patológicos
    diabetes = db.Column(db.Boolean, default=False)
    hipertension = db.Column(db.Boolean, default=False)
    hipotension = db.Column(db.Boolean, default=False)
    enfermedad_venerea = db.Column(db.Boolean, default=False)
    hepatitis = db.Column(db.Boolean, default=False)
    asma = db.Column(db.Boolean, default=False)
    epilepsia = db.Column(db.Boolean, default=False)
    artritis = db.Column(db.Boolean, default=False)
    cancer = db.Column(db.Boolean, default=False)
    vih_sida = db.Column(db.Boolean, default=False)

    otros_padecimientos = db.Column(db.Text, nullable=True)

    # Antecedentes familiares
    antecedentes_heredofamiliares = db.Column(
        db.Text,
        nullable=True
    )

    # Embarazo
    embarazada = db.Column(db.Boolean, default=False)
    meses_embarazo = db.Column(db.Integer, nullable=True)

    fecha_actualizacion = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    paciente = db.relationship(
        "Paciente",
        backref=db.backref(
            "antecedente_medico",
            uselist=False
        )
    )