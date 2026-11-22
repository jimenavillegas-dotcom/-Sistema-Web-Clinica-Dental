from decimal import Decimal, InvalidOperation
from datetime import datetime
from io import BytesIO
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from config import Config
from extensions import db, login_manager
from models import (
    Rol,
    Usuario,
    Paciente,
    AntecedenteMedico,
    ExamenClinico,
    OdontogramaDetalle,
    OdontogramaHistorial,
    Tratamiento,
    Cita,
    NotaEvolucion,
    Consentimiento
)


app = Flask(__name__)
app.config.from_object(Config)


CONSENTIMIENTOS_PDF = {
    'Pacientes comprometidos sistémicamente': '01_pacientes_comprometidos_sistemicamente.pdf',
    'Aclaramiento dental': '02_aclaramiento_dental.pdf',
    'Armonización orofacial': '03_armonizacion_orofacial.pdf',
    'Anestesia en odontología': '04_anestesia_odontologia.pdf',
    'Carillas': '05_carillas.pdf',
    'Tallado de dientes pilares, coronas y prótesis fija': '06_coronas_protesis_fija.pdf',
    'Valoración, profilaxis y detartraje': '07_valoracion_profilaxis_detartraje.pdf',
    'Endodoncia': '08_endodoncia.pdf',
    'Exodoncia simple': '09_exodoncia_simple.pdf',
    'Exodoncia de terceros molares': '10_exodoncia_terceros_molares.pdf',
    'Atención odontológica en pacientes gestantes': '11_gestantes.pdf',
    'Gingivectomía': '12_gingivectomia.pdf',
    'Implantes dentales': '13_implantes_dentales.pdf',
    'Operatoria dental': '14_operatoria_dental.pdf',
    'Ortodoncia': '15_ortodoncia.pdf',
    'Odontopediatría': '16_odontopediatria.pdf',
    'Prótesis parcial removible': '17_protesis_parcial_removible.pdf',
    'Prótesis total removible': '18_protesis_total_removible.pdf',
    'Pulpectomía': '19_pulpectomia.pdf',
    'Pulpotomía': '20_pulpotomia.pdf',
    'Toma de registros clínicos y radiográficos': '21_registros_clinicos_radiograficos.pdf',
}

# Datos profesionales confirmados de la responsable del consultorio.
# El registro profesional/cédula se deja vacío hasta contar con el número real;
# no se inventa información clínica o legal.
DATOS_ODONTOLOGA = {
    "nombre": "Dra. Rosa Elisa Arriaga Aguilar",
    "profesion": "Odontóloga general",
    "registro_profesional": "08780558",
}

db.init_app(app)
login_manager.init_app(app)


# =========================================================
# CARGAR USUARIO
# =========================================================

@login_manager.user_loader
def cargar_usuario(usuario_id):
    return db.session.get(Usuario, int(usuario_id))


# =========================================================
# CREAR TABLAS
# =========================================================

with app.app_context():
    db.create_all()


# =========================================================
# INICIO
# =========================================================

@app.route("/")
def inicio():
    return redirect(url_for("login"))


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        correo = request.form.get("correo")
        password = request.form.get("password")

        usuario = Usuario.query.filter_by(
            correo=correo
        ).first()

        if (
            usuario
            and usuario.activo
            and check_password_hash(
                usuario.password,
                password
            )
        ):
            login_user(usuario)
            return redirect(url_for("dashboard"))

        flash("Correo o contraseña incorrectos.")

    return render_template("auth/login.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    hoy = datetime.now().date()

    total_pacientes = Paciente.query.filter_by(
        activo=True
    ).count()

    agenda_hoy = Cita.query.filter(
        Cita.fecha == hoy
    ).order_by(
        Cita.hora.asc()
    ).all()

    total_citas_hoy = len(
        agenda_hoy
    )

    tratamientos_en_curso = Tratamiento.query.filter(
        Tratamiento.estado == "En proceso"
    ).count()

    proximas_citas = Cita.query.filter(
        Cita.fecha >= hoy,
        Cita.estado.in_(
            ["Programada", "Confirmada"]
        )
    ).count()

    todas_las_citas = Cita.query.order_by(
        Cita.fecha.asc(),
        Cita.hora.asc()
    ).all()

    citas_calendario = []

    for cita in todas_las_citas:

        nombre_paciente = (
            f"{cita.paciente.nombre} "
            f"{cita.paciente.apellidos}"
        ).strip()

        citas_calendario.append({
            "id": cita.id,
            "fecha": cita.fecha.isoformat(),
            "hora": cita.hora.strftime("%H:%M"),
            "paciente": nombre_paciente,
            "motivo": cita.motivo,
            "estado": cita.estado,
            "url": url_for(
                "expediente_paciente",
                paciente_id=cita.paciente_id,
                tab="citas",
                cita_id=cita.id
            )
        })

    return render_template(
        "dashboard/index.html",
        total_pacientes=total_pacientes,
        total_citas_hoy=total_citas_hoy,
        tratamientos_en_curso=tratamientos_en_curso,
        proximas_citas=proximas_citas,
        hoy=hoy,
        agenda_hoy=agenda_hoy,
        citas_calendario=citas_calendario
    )


# =========================================================
# LISTA DE PACIENTES
# =========================================================

@app.route("/pacientes")
@login_required
def pacientes():

    lista_pacientes = Paciente.query.order_by(
        Paciente.fecha_registro.desc()
    ).all()

    return render_template(
        "pacientes/index.html",
        pacientes=lista_pacientes
    )




# =========================================================
# EXPEDIENTES - BÚSQUEDA DIRECTA
# =========================================================

@app.route("/expedientes")
@login_required
def expedientes():
    termino = request.args.get("q", "").strip()
    estado = request.args.get("estado", "todos").strip().lower()

    lista = Paciente.query.order_by(
        Paciente.apellidos.asc(),
        Paciente.nombre.asc()
    ).all()

    if estado == "activos":
        lista = [paciente for paciente in lista if paciente.activo]
    elif estado == "inactivos":
        lista = [paciente for paciente in lista if not paciente.activo]
    else:
        estado = "todos"

    if termino:
        buscado = termino.casefold()

        def coincide(paciente):
            campos = [
                paciente.numero_historia,
                paciente.nombre,
                paciente.apellidos,
                paciente.documento_identidad,
                paciente.telefono,
                paciente.correo,
            ]
            texto = " ".join(str(valor or "") for valor in campos).casefold()
            return buscado in texto

        lista = [paciente for paciente in lista if coincide(paciente)]

    total = Paciente.query.count()
    total_activos = Paciente.query.filter_by(activo=True).count()
    total_inactivos = total - total_activos

    return render_template(
        "expedientes/index.html",
        pacientes=lista,
        q=termino,
        estado=estado,
        total=total,
        total_activos=total_activos,
        total_inactivos=total_inactivos,
    )


# =========================================================
# NUEVO PACIENTE
# =========================================================

@app.route(
    "/pacientes/nuevo",
    methods=["GET", "POST"]
)
@login_required
def nuevo_paciente():

    if request.method == "POST":

        nombre = request.form.get("nombre")
        apellidos = request.form.get("apellidos")
        documento_identidad = request.form.get("documento_identidad")
        fecha_nacimiento = request.form.get("fecha_nacimiento")
        genero = request.form.get("genero")
        lugar_nacimiento = request.form.get("lugar_nacimiento")
        domicilio = request.form.get("domicilio")
        ocupacion = request.form.get("ocupacion")
        escolaridad = request.form.get("escolaridad")
        estado_civil = request.form.get("estado_civil")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")
        motivo_consulta = request.form.get("motivo_consulta")

        # Generar número de historia clínica
        total_pacientes = Paciente.query.count() + 1

        numero_historia = (
            f"PAC-{total_pacientes:06d}"
        )

        nuevo = Paciente(
            numero_historia=numero_historia,
            nombre=nombre,
            apellidos=apellidos,
            documento_identidad=(
                documento_identidad or None
            ),
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            lugar_nacimiento=lugar_nacimiento,
            domicilio=domicilio,
            ocupacion=ocupacion,
            escolaridad=escolaridad,
            estado_civil=estado_civil,
            telefono=telefono,
            correo=correo,
            motivo_consulta=motivo_consulta
        )

        db.session.add(nuevo)
        db.session.commit()

        flash(
            "Paciente registrado correctamente."
        )

        return redirect(
            url_for("pacientes")
        )

    return render_template(
        "pacientes/nuevo.html"
    )


# =========================================================
# EDITAR / ACTUALIZAR PACIENTE
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar_paciente(paciente_id):

    paciente = Paciente.query.get_or_404(paciente_id)

    if request.method == "POST":

        nombre = (request.form.get("nombre") or "").strip()
        apellidos = (request.form.get("apellidos") or "").strip()
        documento_identidad = (
            request.form.get("documento_identidad") or ""
        ).strip()
        fecha_nacimiento = request.form.get("fecha_nacimiento")
        genero = (request.form.get("genero") or "").strip()
        lugar_nacimiento = (
            request.form.get("lugar_nacimiento") or ""
        ).strip()
        domicilio = (request.form.get("domicilio") or "").strip()
        ocupacion = (request.form.get("ocupacion") or "").strip()
        escolaridad = (request.form.get("escolaridad") or "").strip()
        estado_civil = (request.form.get("estado_civil") or "").strip()
        telefono = (request.form.get("telefono") or "").strip()
        correo = (request.form.get("correo") or "").strip()
        motivo_consulta = (
            request.form.get("motivo_consulta") or ""
        ).strip()
        activo = request.form.get("activo") == "on"

        if not nombre or not apellidos or not fecha_nacimiento or not genero:
            flash(
                "Nombre, apellidos, fecha de nacimiento y género son obligatorios."
            )
            return render_template(
                "pacientes/editar.html",
                paciente=paciente
            )

        if documento_identidad:
            documento_existente = Paciente.query.filter(
                Paciente.documento_identidad == documento_identidad,
                Paciente.id != paciente.id
            ).first()

            if documento_existente:
                flash(
                    "Ese documento de identidad ya está registrado en otro paciente."
                )
                return render_template(
                    "pacientes/editar.html",
                    paciente=paciente
                )

        try:
            paciente.nombre = nombre
            paciente.apellidos = apellidos
            paciente.documento_identidad = documento_identidad or None
            paciente.fecha_nacimiento = datetime.strptime(
                fecha_nacimiento,
                "%Y-%m-%d"
            ).date()
            paciente.genero = genero
            paciente.lugar_nacimiento = lugar_nacimiento or None
            paciente.domicilio = domicilio or None
            paciente.ocupacion = ocupacion or None
            paciente.escolaridad = escolaridad or None
            paciente.estado_civil = estado_civil or None
            paciente.telefono = telefono or None
            paciente.correo = correo or None
            paciente.motivo_consulta = motivo_consulta or None
            paciente.activo = activo

            db.session.commit()

            flash("Datos del paciente actualizados correctamente.")

            return redirect(
                url_for(
                    "expediente_paciente",
                    paciente_id=paciente.id
                )
            )

        except Exception:
            db.session.rollback()
            flash(
                "No fue posible actualizar los datos del paciente. Revisa la información e inténtalo nuevamente."
            )

    return render_template(
        "pacientes/editar.html",
        paciente=paciente
    )


# =========================================================
# EXPEDIENTE DE UN PACIENTE
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/expediente"
)
@login_required
def expediente_paciente(paciente_id):

    paciente = Paciente.query.get_or_404(
        paciente_id
    )

    antecedente = AntecedenteMedico.query.filter_by(
        paciente_id=paciente.id
    ).first()

    examen = ExamenClinico.query.filter_by(
        paciente_id=paciente.id
    ).first()

    odontograma = OdontogramaDetalle.query.filter_by(
        paciente_id=paciente.id
    ).all()

    tratamientos = Tratamiento.query.filter_by(
        paciente_id=paciente.id
    ).order_by(
        Tratamiento.fecha_registro.desc()
    ).all()

    citas = Cita.query.filter_by(
        paciente_id=paciente.id
    ).order_by(
        Cita.fecha.desc(),
        Cita.hora.desc()
    ).all()

    notas_evolucion = NotaEvolucion.query.filter_by(
        paciente_id=paciente.id
    ).order_by(
        NotaEvolucion.fecha.desc()
    ).all()

    consentimientos = Consentimiento.query.filter_by(
        paciente_id=paciente.id
    ).order_by(
        Consentimiento.fecha.desc()
    ).all()

    # Convertimos los datos del odontograma
    # para utilizarlos desde JavaScript.
    odontograma_datos = []

    for detalle in odontograma:

        odontograma_datos.append({
            "numero_diente": detalle.numero_diente,
            "superficie": detalle.superficie,
            "estado": detalle.estado,
            "procedimiento": detalle.procedimiento or "",
            "observaciones": detalle.observaciones or "",
            "costo": (
                float(detalle.costo)
                if detalle.costo is not None
                else None
            ),
            "prioridad": detalle.prioridad or ""
        })

    return render_template(
        "pacientes/expediente.html",
        paciente=paciente,
        antecedente=antecedente,
        examen=examen,
        odontograma=odontograma,
        odontograma_datos=odontograma_datos,
        tratamientos=tratamientos,
        citas=citas,
        notas_evolucion=notas_evolucion,
        consentimientos=consentimientos,
        consentimientos_pdf=CONSENTIMIENTOS_PDF
    )


# =========================================================
# GUARDAR / ACTUALIZAR ANTECEDENTES MÉDICOS
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/antecedentes",
    methods=["POST"]
)
@login_required
def guardar_antecedentes(paciente_id):

    paciente = Paciente.query.get_or_404(
        paciente_id
    )

    antecedente = AntecedenteMedico.query.filter_by(
        paciente_id=paciente.id
    ).first()

    if not antecedente:

        antecedente = AntecedenteMedico(
            paciente_id=paciente.id
        )

        db.session.add(antecedente)

    # HÁBITOS
    antecedente.tabaquismo = (
        request.form.get("tabaquismo") == "on"
    )

    antecedente.alcohol = (
        request.form.get("alcohol") == "on"
    )

    antecedente.otras_sustancias = (
        request.form.get("otras_sustancias") == "on"
    )

    antecedente.detalle_sustancias = (
        request.form.get("detalle_sustancias")
    )

    antecedente.habito_oral = (
        request.form.get("habito_oral")
    )

    # ESTADO MÉDICO ACTUAL
    antecedente.enfermedad_ultimo_anio = (
        request.form.get("enfermedad_ultimo_anio") == "on"
    )

    antecedente.detalle_enfermedad = (
        request.form.get("detalle_enfermedad")
    )

    antecedente.tratamiento_medico = (
        request.form.get("tratamiento_medico") == "on"
    )

    antecedente.detalle_tratamiento = (
        request.form.get("detalle_tratamiento")
    )

    antecedente.alergias = (
        request.form.get("alergias") == "on"
    )

    antecedente.detalle_alergias = (
        request.form.get("detalle_alergias")
    )

    # ANESTESIA
    antecedente.anestesia_previa = (
        request.form.get("anestesia_previa") == "on"
    )

    antecedente.reaccion_anestesia = (
        request.form.get("reaccion_anestesia") == "on"
    )

    antecedente.detalle_reaccion_anestesia = (
        request.form.get("detalle_reaccion_anestesia")
    )

    # SANGRADO
    antecedente.sangrado_excesivo = (
        request.form.get("sangrado_excesivo") == "on"
    )

    antecedente.sitio_sangrado = (
        request.form.get("sitio_sangrado")
    )

    # ANTECEDENTES PERSONALES PATOLÓGICOS
    antecedente.diabetes = (
        request.form.get("diabetes") == "on"
    )

    antecedente.hipertension = (
        request.form.get("hipertension") == "on"
    )

    antecedente.hipotension = (
        request.form.get("hipotension") == "on"
    )

    antecedente.enfermedad_venerea = (
        request.form.get("enfermedad_venerea") == "on"
    )

    antecedente.hepatitis = (
        request.form.get("hepatitis") == "on"
    )

    antecedente.asma = (
        request.form.get("asma") == "on"
    )

    antecedente.epilepsia = (
        request.form.get("epilepsia") == "on"
    )

    antecedente.artritis = (
        request.form.get("artritis") == "on"
    )

    antecedente.cancer = (
        request.form.get("cancer") == "on"
    )

    antecedente.vih_sida = (
        request.form.get("vih_sida") == "on"
    )

    antecedente.otros_padecimientos = (
        request.form.get("otros_padecimientos")
    )

    # ANTECEDENTES HEREDOFAMILIARES
    antecedente.antecedentes_heredofamiliares = (
        request.form.get(
            "antecedentes_heredofamiliares"
        )
    )

    # EMBARAZO
    antecedente.embarazada = (
        request.form.get("embarazada") == "on"
    )

    meses = request.form.get(
        "meses_embarazo"
    )

    if (
        antecedente.embarazada
        and meses
    ):
        antecedente.meses_embarazo = int(meses)

    else:
        antecedente.meses_embarazo = None

    db.session.commit()

    flash(
        "Antecedentes médicos guardados correctamente."
    )

    return redirect(
        url_for(
            "expediente_paciente",
            paciente_id=paciente.id,
            tab="antecedentes"
        )
    )


# =========================================================
# GUARDAR / ACTUALIZAR EXAMEN CLÍNICO
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/examen-clinico",
    methods=["POST"]
)
@login_required
def guardar_examen_clinico(paciente_id):

    paciente = Paciente.query.get_or_404(
        paciente_id
    )

    examen = ExamenClinico.query.filter_by(
        paciente_id=paciente.id
    ).first()

    if not examen:

        examen = ExamenClinico(
            paciente_id=paciente.id
        )

        db.session.add(examen)

    examen.cara_estado = (
        request.form.get("cara_estado")
    )

    examen.cara_observaciones = (
        request.form.get("cara_observaciones")
    )

    examen.cuello_estado = (
        request.form.get("cuello_estado")
    )

    examen.cuello_observaciones = (
        request.form.get("cuello_observaciones")
    )

    examen.labios_estado = (
        request.form.get("labios_estado")
    )

    examen.labios_observaciones = (
        request.form.get("labios_observaciones")
    )

    examen.carrillos_estado = (
        request.form.get("carrillos_estado")
    )

    examen.carrillos_observaciones = (
        request.form.get("carrillos_observaciones")
    )

    examen.paladar_blando_estado = (
        request.form.get("paladar_blando_estado")
    )

    examen.paladar_blando_observaciones = (
        request.form.get("paladar_blando_observaciones")
    )

    examen.paladar_duro_estado = (
        request.form.get("paladar_duro_estado")
    )

    examen.paladar_duro_observaciones = (
        request.form.get("paladar_duro_observaciones")
    )

    examen.lengua_estado = (
        request.form.get("lengua_estado")
    )

    examen.lengua_observaciones = (
        request.form.get("lengua_observaciones")
    )

    examen.amigdalas_estado = (
        request.form.get("amigdalas_estado")
    )

    examen.amigdalas_observaciones = (
        request.form.get("amigdalas_observaciones")
    )

    examen.piso_boca_estado = (
        request.form.get("piso_boca_estado")
    )

    examen.piso_boca_observaciones = (
        request.form.get("piso_boca_observaciones")
    )

    examen.glandulas_salivales_estado = (
        request.form.get("glandulas_salivales_estado")
    )

    examen.glandulas_salivales_observaciones = (
        request.form.get("glandulas_salivales_observaciones")
    )

    examen.atm_estado = (
        request.form.get("atm_estado")
    )

    examen.atm_observaciones = (
        request.form.get("atm_observaciones")
    )

    examen.oclusion_estado = (
        request.form.get("oclusion_estado")
    )

    examen.oclusion_observaciones = (
        request.form.get("oclusion_observaciones")
    )

    examen.observaciones_generales = (
        request.form.get("observaciones_generales")
    )

    db.session.commit()

    flash(
        "Examen clínico guardado correctamente."
    )

    return redirect(
        url_for(
            "expediente_paciente",
            paciente_id=paciente.id,
            tab="examen"
        )
    )


# =========================================================
# GUARDAR / ACTUALIZAR ODONTOGRAMA
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/odontograma",
    methods=["POST"]
)
@login_required
def guardar_odontograma(paciente_id):

    paciente = Paciente.query.get_or_404(
        paciente_id
    )

    numero_diente = request.form.get(
        "numero_diente"
    )

    superficie = request.form.get(
        "superficie"
    )

    estado = request.form.get(
        "estado"
    )

    procedimiento = request.form.get(
        "procedimiento"
    )

    observaciones = request.form.get(
        "observaciones"
    )

    costo_texto = request.form.get(
        "costo"
    )

    prioridad = request.form.get(
        "prioridad"
    )

    dientes_validos = {
        "11", "12", "13", "14",
        "15", "16", "17", "18",
        "21", "22", "23", "24",
        "25", "26", "27", "28",
        "31", "32", "33", "34",
        "35", "36", "37", "38",
        "41", "42", "43", "44",
        "45", "46", "47", "48"
    }

    superficies_validas = {
        "General",
        "Vestibular",
        "Lingual/Palatina",
        "Mesial",
        "Distal",
        "Oclusal/Incisal"
    }

    estados_validos = {
        "Sano",
        "Caries",
        "Obturado",
        "Extracción indicada",
        "Ausente",
        "Corona/Prótesis",
        "Endodoncia",
        "Sellador"
    }

    if numero_diente not in dientes_validos:

        flash(
            "El número de diente seleccionado no es válido."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="odontograma"
            )
        )

    if superficie not in superficies_validas:

        flash(
            "La superficie dental seleccionada no es válida."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="odontograma"
            )
        )

    if estado not in estados_validos:

        flash(
            "El estado dental seleccionado no es válido."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="odontograma"
            )
        )

    costo = None

    if costo_texto:

        try:

            costo = Decimal(
                costo_texto
            )

            if costo < 0:

                flash(
                    "El costo no puede ser negativo."
                )

                return redirect(
                    url_for(
                        "expediente_paciente",
                        paciente_id=paciente.id,
                        tab="odontograma"
                    )
                )

        except InvalidOperation:

            flash(
                "El costo ingresado no es válido."
            )

            return redirect(
                url_for(
                    "expediente_paciente",
                    paciente_id=paciente.id,
                    tab="odontograma"
                )
            )

    detalle = OdontogramaDetalle.query.filter_by(
        paciente_id=paciente.id,
        numero_diente=numero_diente,
        superficie=superficie
    ).first()

    if not detalle:

        detalle = OdontogramaDetalle(
            paciente_id=paciente.id,
            numero_diente=numero_diente,
            superficie=superficie,
            estado=estado,
            procedimiento=procedimiento or None,
            observaciones=observaciones or None,
            costo=costo,
            prioridad=prioridad or None
        )

        db.session.add(detalle)

        historial = OdontogramaHistorial(
            paciente_id=paciente.id,
            numero_diente=numero_diente,
            superficie=superficie,
            estado_anterior=None,
            estado_nuevo=estado,
            procedimiento=procedimiento or None,
            observaciones=observaciones or None
        )

        db.session.add(historial)

    else:

        hubo_cambio = (
            detalle.estado != estado
            or
            (detalle.procedimiento or "")
            != (procedimiento or "")
            or
            (detalle.observaciones or "")
            != (observaciones or "")
            or
            detalle.costo != costo
            or
            (detalle.prioridad or "")
            != (prioridad or "")
        )

        if hubo_cambio:

            historial = OdontogramaHistorial(
                paciente_id=paciente.id,
                numero_diente=numero_diente,
                superficie=superficie,
                estado_anterior=detalle.estado,
                estado_nuevo=estado,
                procedimiento=procedimiento or None,
                observaciones=observaciones or None
            )

            db.session.add(historial)

        detalle.estado = estado
        detalle.procedimiento = procedimiento or None
        detalle.observaciones = observaciones or None
        detalle.costo = costo
        detalle.prioridad = prioridad or None

    db.session.commit()

    flash(
        f"Diente {numero_diente} actualizado correctamente."
    )

    return redirect(
        url_for(
            "expediente_paciente",
            paciente_id=paciente.id,
            tab="odontograma"
        )
    )


# =========================================================
# GUARDAR PLAN DE TRATAMIENTO
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/tratamientos",
    methods=["POST"]
)
@login_required
def guardar_tratamiento(paciente_id):

    paciente = Paciente.query.get_or_404(
        paciente_id
    )

    numero_diente = request.form.get(
        "numero_diente"
    )

    diagnostico = request.form.get(
        "diagnostico"
    )

    procedimiento = request.form.get(
        "procedimiento"
    )

    prioridad = request.form.get(
        "prioridad"
    )

    estado = request.form.get(
        "estado"
    )

    costo_texto = request.form.get(
        "costo"
    )

    observaciones = request.form.get(
        "observaciones"
    )

    # =====================================================
    # VALIDACIONES
    # =====================================================

    if not diagnostico:

        flash(
            "Debes registrar un diagnóstico."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="tratamiento"
            )
        )

    if not procedimiento:

        flash(
            "Debes registrar un procedimiento."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="tratamiento"
            )
        )

    dientes_validos = {
        "11", "12", "13", "14",
        "15", "16", "17", "18",
        "21", "22", "23", "24",
        "25", "26", "27", "28",
        "31", "32", "33", "34",
        "35", "36", "37", "38",
        "41", "42", "43", "44",
        "45", "46", "47", "48"
    }

    if numero_diente and numero_diente not in dientes_validos:

        flash(
            "El número de diente seleccionado no es válido."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="tratamiento"
            )
        )

    prioridades_validas = {
        "",
        "Baja",
        "Media",
        "Alta",
        "Urgente"
    }

    if prioridad not in prioridades_validas:
        prioridad = ""

    estados_validos = {
        "Pendiente",
        "En proceso",
        "Completado",
        "Cancelado"
    }

    if estado not in estados_validos:
        estado = "Pendiente"

    # =====================================================
    # COSTO
    # =====================================================

    costo = None

    if costo_texto:

        try:

            costo = Decimal(
                costo_texto
            )

            if costo < 0:

                flash(
                    "El costo no puede ser negativo."
                )

                return redirect(
                    url_for(
                        "expediente_paciente",
                        paciente_id=paciente.id,
                        tab="tratamiento"
                    )
                )

        except InvalidOperation:

            flash(
                "El costo ingresado no es válido."
            )

            return redirect(
                url_for(
                    "expediente_paciente",
                    paciente_id=paciente.id,
                    tab="tratamiento"
                )
            )

    # =====================================================
    # CREAR TRATAMIENTO
    # =====================================================

    nuevo_tratamiento = Tratamiento(
        paciente_id=paciente.id,
        numero_diente=numero_diente or None,
        diagnostico=diagnostico.strip(),
        procedimiento=procedimiento.strip(),
        prioridad=prioridad or None,
        estado=estado,
        costo=costo,
        observaciones=observaciones or None
    )

    db.session.add(
        nuevo_tratamiento
    )

    db.session.commit()

    flash(
        "Tratamiento agregado correctamente."
    )

    return redirect(
        url_for(
            "expediente_paciente",
            paciente_id=paciente.id,
            tab="tratamiento"
        )
    )


# =========================================================
# ACTUALIZAR ESTADO DE TRATAMIENTO
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/tratamientos/<int:tratamiento_id>/estado",
    methods=["POST"]
)
@login_required
def actualizar_estado_tratamiento(
    paciente_id,
    tratamiento_id
):

    paciente = Paciente.query.get_or_404(
        paciente_id
    )

    tratamiento = Tratamiento.query.filter_by(
        id=tratamiento_id,
        paciente_id=paciente.id
    ).first_or_404()

    nuevo_estado = request.form.get(
        "estado"
    )

    estados_validos = {
        "Pendiente",
        "En proceso",
        "Completado",
        "Cancelado"
    }

    if nuevo_estado not in estados_validos:

        flash(
            "El estado seleccionado no es válido."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="tratamiento"
            )
        )

    tratamiento.estado = nuevo_estado

    db.session.commit()

    flash(
        "Estado del tratamiento actualizado correctamente."
    )

    return redirect(
        url_for(
            "expediente_paciente",
            paciente_id=paciente.id,
            tab="tratamiento"
        )
    )



# =========================================================
# GUARDAR NOTA DE EVOLUCIÓN
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/notas-evolucion",
    methods=["POST"]
)
@login_required
def guardar_nota_evolucion(paciente_id):

    paciente = Paciente.query.get_or_404(
        paciente_id
    )

    numero_diente = (
        request.form.get("numero_diente") or ""
    ).strip()

    procedimiento = (
        request.form.get("procedimiento") or ""
    ).strip()

    evolucion = (
        request.form.get("evolucion") or ""
    ).strip()

    indicaciones = (
        request.form.get("indicaciones") or ""
    ).strip()

    observaciones = (
        request.form.get("observaciones") or ""
    ).strip()

    if not procedimiento:

        flash(
            "Debes registrar el procedimiento realizado."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="evolucion"
            )
        )

    if not evolucion:

        flash(
            "Debes registrar la evolución clínica del paciente."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="evolucion"
            )
        )

    dientes_validos = {
        "11", "12", "13", "14",
        "15", "16", "17", "18",
        "21", "22", "23", "24",
        "25", "26", "27", "28",
        "31", "32", "33", "34",
        "35", "36", "37", "38",
        "41", "42", "43", "44",
        "45", "46", "47", "48"
    }

    if numero_diente and numero_diente not in dientes_validos:

        flash(
            "El número de diente seleccionado no es válido."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="evolucion"
            )
        )

    nueva_nota = NotaEvolucion(
        paciente_id=paciente.id,
        numero_diente=numero_diente or None,
        procedimiento=procedimiento,
        evolucion=evolucion,
        indicaciones=indicaciones or None,
        observaciones=observaciones or None
    )

    db.session.add(
        nueva_nota
    )

    db.session.commit()

    flash(
        "Nota de evolución registrada correctamente."
    )

    return redirect(
        url_for(
            "expediente_paciente",
            paciente_id=paciente.id,
            tab="evolucion"
        )
    )




# =========================================================
# CONSENTIMIENTOS PDF PRECARGADOS
# =========================================================

def _calcular_edad_paciente(fecha_nacimiento):
    if not fecha_nacimiento:
        return ""

    hoy = datetime.now().date()
    edad = hoy.year - fecha_nacimiento.year

    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1

    return max(edad, 0)


def _pagina_datos_consentimiento(documento):
    for pagina in documento:
        texto = (pagina.get_text("text") or "").upper()
        if "DATOS DEL PACIENTE" in texto:
            return pagina

    return documento[0]


def _buscar_etiqueta_pdf(pagina, variantes):
    coincidencias = []

    for variante in variantes:
        for rectangulo in pagina.search_for(variante):
            # Evita tomar textos repetidos de las declaraciones finales.
            if rectangulo.y0 < pagina.rect.height * 0.76:
                coincidencias.append(
                    (rectangulo.y0, rectangulo.x0, rectangulo)
                )

    if not coincidencias:
        return None

    coincidencias.sort(key=lambda elemento: (elemento[0], elemento[1]))
    return coincidencias[0][2]


def _lineas_subrayadas_pdf(pagina):
    lineas = []

    for palabra in pagina.get_text("words"):
        texto = palabra[4]

        if texto.count("_") >= 4:
            lineas.append(
                __import__("fitz").Rect(
                    palabra[0], palabra[1], palabra[2], palabra[3]
                )
            )

    return lineas


def _caja_campo_pdf(pagina, etiqueta, ancho_maximo=260, ancho_minimo_linea=30):
    candidatos = []
    centro_etiqueta = (etiqueta.y0 + etiqueta.y1) / 2

    for linea in _lineas_subrayadas_pdf(pagina):
        if linea.width < ancho_minimo_linea:
            continue

        centro_linea = (linea.y0 + linea.y1) / 2
        diferencia_vertical = abs(centro_linea - centro_etiqueta)

        if diferencia_vertical > 26:
            continue

        if linea.x1 < etiqueta.x0 - 5:
            continue

        separacion_horizontal = max(0, linea.x0 - etiqueta.x1)
        penalizacion_izquierda = max(0, etiqueta.x0 - linea.x0) * 0.4

        puntuacion = (
            diferencia_vertical * 5
            + separacion_horizontal * 0.12
            + penalizacion_izquierda
        )

        candidatos.append((puntuacion, linea))

    if candidatos:
        candidatos.sort(key=lambda elemento: elemento[0])
        linea = candidatos[0][1]

        return __import__("fitz").Rect(
            linea.x0 + 2,
            linea.y0 - 2,
            linea.x1 - 2,
            linea.y1 + 1
        )

    # Algunos formatos usan líneas vectoriales y no guiones bajos.
    # En esos casos escribimos justo debajo de la etiqueta.
    y_inicio = etiqueta.y1 + 5

    return __import__("fitz").Rect(
        etiqueta.x0,
        y_inicio,
        min(pagina.rect.width - 45, etiqueta.x0 + ancho_maximo),
        y_inicio + 15
    )


def _escribir_campo_pdf(
    pagina,
    variantes_etiqueta,
    valor,
    ancho_maximo=260,
    ancho_minimo_linea=30,
    tamano=8
):
    if valor is None or str(valor).strip() == "":
        return False

    etiqueta = _buscar_etiqueta_pdf(pagina, variantes_etiqueta)

    if not etiqueta:
        return False

    caja = _caja_campo_pdf(
        pagina,
        etiqueta,
        ancho_maximo=ancho_maximo,
        ancho_minimo_linea=ancho_minimo_linea
    )

    texto = str(valor).strip()
    tamano_actual = tamano

    while tamano_actual >= 6:
        resultado = pagina.insert_textbox(
            caja,
            texto,
            fontsize=tamano_actual,
            fontname="helv",
            color=(0, 0, 0),
            align=0,
            overlay=True
        )

        if resultado >= 0:
            return True

        tamano_actual -= 0.5

    pagina.insert_text(
        (caja.x0, caja.y1 - 2),
        texto[:40],
        fontsize=6,
        fontname="helv",
        color=(0, 0, 0),
        overlay=True
    )

    return True


def _escribir_fecha_pdf(pagina, fecha_texto):
    etiqueta = _buscar_etiqueta_pdf(
        pagina,
        ["FECHA:", "Fecha:"]
    )

    if not etiqueta:
        return False

    import fitz

    caja = fitz.Rect(
        etiqueta.x1 + 8,
        etiqueta.y0 - 1,
        min(pagina.rect.width - 40, etiqueta.x1 + 115),
        etiqueta.y1 + 3
    )

    pagina.insert_textbox(
        caja,
        fecha_texto,
        fontsize=8,
        fontname="helv",
        color=(0, 0, 0),
        overlay=True
    )

    return True


def _buscar_etiqueta_pdf_en_rango(pagina, variantes, y_min=0, y_max=None):
    if y_max is None:
        y_max = pagina.rect.height

    coincidencias = []

    for variante in variantes:
        for rectangulo in pagina.search_for(variante):
            if rectangulo.y0 >= y_min and rectangulo.y1 <= y_max:
                coincidencias.append((rectangulo.y0, rectangulo.x0, rectangulo))

    if not coincidencias:
        return None

    coincidencias.sort(key=lambda elemento: (elemento[0], elemento[1]))
    return coincidencias[0][2]


def _escribir_campo_pdf_en_rango(
    pagina,
    variantes_etiqueta,
    valor,
    y_min=0,
    y_max=None,
    ancho_maximo=260,
    ancho_minimo_linea=30,
    tamano=8
):
    if valor is None or str(valor).strip() == "":
        return False

    etiqueta = _buscar_etiqueta_pdf_en_rango(
        pagina,
        variantes_etiqueta,
        y_min=y_min,
        y_max=y_max
    )

    if not etiqueta:
        return False

    caja = _caja_campo_pdf(
        pagina,
        etiqueta,
        ancho_maximo=ancho_maximo,
        ancho_minimo_linea=ancho_minimo_linea
    )

    texto = str(valor).strip()
    tamano_actual = tamano

    while tamano_actual >= 6:
        resultado = pagina.insert_textbox(
            caja,
            texto,
            fontsize=tamano_actual,
            fontname="helv",
            color=(0, 0, 0),
            align=0,
            overlay=True
        )

        if resultado >= 0:
            return True

        tamano_actual -= 0.5

    pagina.insert_text(
        (caja.x0, caja.y1 - 2),
        texto[:50],
        fontsize=6,
        fontname="helv",
        color=(0, 0, 0),
        overlay=True
    )

    return True


def _escribir_datos_odontologa_pdf(pagina):
    encabezados = [
        "ODONTÓLOGO TRATANTE",
        "ODONTÓLOGO / CIRUJANO TRATANTE",
        "ORTODONCISTA TRATANTE",
        "PROFESIONAL TRATANTE",
    ]

    encabezado = _buscar_etiqueta_pdf(pagina, encabezados)

    if not encabezado:
        return

    y_min = encabezado.y1
    y_max = min(pagina.rect.height * 0.55, encabezado.y1 + 175)

    _escribir_campo_pdf_en_rango(
        pagina,
        ["Nombre:"],
        DATOS_ODONTOLOGA["nombre"],
        y_min=y_min,
        y_max=y_max,
        ancho_maximo=300,
        ancho_minimo_linea=45,
        tamano=7.5
    )

    # Solo se rellena si se configura el número real.
    _escribir_campo_pdf_en_rango(
        pagina,
        ["Registro profesional:", "Registro profesional"],
        DATOS_ODONTOLOGA["registro_profesional"],
        y_min=y_min,
        y_max=y_max,
        ancho_maximo=220,
        ancho_minimo_linea=45,
        tamano=7.5
    )


def _datos_diente_fdi(numero_diente):
    numero = str(numero_diente or "").strip()

    if len(numero) != 2 or not numero.isdigit():
        return "", ""

    cuadrante = numero[0]

    mapa = {
        "1": ("Superior", "1 - superior derecho"),
        "2": ("Superior", "2 - superior izquierdo"),
        "3": ("Inferior", "3 - inferior izquierdo"),
        "4": ("Inferior", "4 - inferior derecho"),
    }

    return mapa.get(cuadrante, ("", ""))


def _marcar_arcada_pdf(pagina, arcada):
    if not arcada:
        return False

    etiqueta_arcada = _buscar_etiqueta_pdf(pagina, ["Arcada:", "Arcada"])
    if not etiqueta_arcada:
        return False

    coincidencias = []
    for rectangulo in pagina.search_for(arcada):
        if abs(rectangulo.y0 - etiqueta_arcada.y0) <= 25 and rectangulo.x0 >= etiqueta_arcada.x0:
            coincidencias.append(rectangulo)

    if not coincidencias:
        return False

    objetivo = sorted(coincidencias, key=lambda r: r.x0)[0]
    pagina.insert_text(
        (max(8, objetivo.x0 - 12), objetivo.y1 - 2),
        "X",
        fontsize=9,
        fontname="helv",
        color=(0, 0, 0),
        overlay=True
    )
    return True


def _rellenar_observaciones_documento(documento, observaciones):
    if not observaciones or not str(observaciones).strip():
        return False

    import fitz

    texto = str(observaciones).strip()

    # Primero intenta campos cortos como "Observaciones clínicas relevantes".
    for pagina in documento:
        if _escribir_campo_pdf(
            pagina,
            [
                "Observaciones clínicas relevantes:",
                "Observaciones clínicas:",
            ],
            texto,
            ancho_maximo=360,
            ancho_minimo_linea=55,
            tamano=7
        ):
            return True

    # Después busca una sección amplia de OBSERVACIONES, comúnmente al final.
    for pagina in documento:
        encabezado = _buscar_etiqueta_pdf(
            pagina,
            ["OBSERVACIONES", "Observaciones"]
        )

        if not encabezado:
            continue

        caja = fitz.Rect(
            45,
            min(pagina.rect.height - 90, encabezado.y1 + 16),
            pagina.rect.width - 45,
            min(pagina.rect.height - 45, encabezado.y1 + 150)
        )

        pagina.insert_textbox(
            caja,
            texto,
            fontsize=8,
            fontname="helv",
            color=(0, 0, 0),
            align=0,
            overlay=True
        )
        return True

    return False


def _agregar_resumen_clinico_pdf(
    documento,
    paciente,
    numero_diente,
    procedimiento,
    diagnostico,
    observaciones
):
    import fitz

    pagina = documento.new_page(width=595, height=842)
    margen = 55

    pagina.insert_text(
        (margen, 70),
        "DATOS CLÍNICOS COMPLEMENTARIOS",
        fontsize=15,
        fontname="helv",
        color=(0, 0, 0)
    )

    pagina.insert_text(
        (margen, 98),
        "Anexo generado por el sistema para acompañar el consentimiento informado.",
        fontsize=8,
        fontname="helv",
        color=(0.25, 0.25, 0.25)
    )

    nombre_paciente = f"{paciente.nombre} {paciente.apellidos}".strip()

    campos = [
        ("Historia clínica", paciente.numero_historia or ""),
        ("Paciente", nombre_paciente),
        ("Odontóloga responsable", DATOS_ODONTOLOGA["nombre"]),
        ("Registro profesional", DATOS_ODONTOLOGA["registro_profesional"]),
        ("Pieza dental", numero_diente or ""),
        ("Procedimiento", procedimiento or ""),
        ("Diagnóstico / hallazgo", diagnostico or ""),
        ("Observaciones", observaciones or ""),
    ]

    y = 140
    for etiqueta, valor in campos:
        if not str(valor or "").strip():
            continue

        pagina.insert_text(
            (margen, y),
            etiqueta + ":",
            fontsize=9,
            fontname="hebo",
            color=(0, 0, 0)
        )

        caja = fitz.Rect(margen, y + 8, 540, y + 70)
        pagina.insert_textbox(
            caja,
            str(valor).strip(),
            fontsize=9,
            fontname="helv",
            color=(0, 0, 0),
            align=0
        )
        y += 72 if etiqueta in {"Diagnóstico / hallazgo", "Observaciones"} else 45

        if y > 760:
            break

    return pagina


def _obtener_datos_clinicos_consentimiento(
    paciente,
    numero_diente="",
    procedimiento="",
    diagnostico="",
    observaciones=""
):
    procedimiento = (procedimiento or "").strip()
    diagnostico = (diagnostico or "").strip()
    observaciones = (observaciones or "").strip()
    numero_diente = (numero_diente or "").strip()

    if numero_diente:
        tratamiento = (
            Tratamiento.query
            .filter_by(
                paciente_id=paciente.id,
                numero_diente=numero_diente
            )
            .order_by(Tratamiento.fecha_registro.desc())
            .first()
        )

        if tratamiento:
            if not procedimiento:
                procedimiento = tratamiento.procedimiento or ""
            if not diagnostico:
                diagnostico = tratamiento.diagnostico or ""
            if not observaciones:
                observaciones = tratamiento.observaciones or ""

        if not procedimiento or not diagnostico or not observaciones:
            detalles = (
                OdontogramaDetalle.query
                .filter_by(
                    paciente_id=paciente.id,
                    numero_diente=numero_diente
                )
                .order_by(OdontogramaDetalle.fecha_actualizacion.desc())
                .all()
            )

            for detalle in detalles:
                if not procedimiento and detalle.procedimiento:
                    procedimiento = detalle.procedimiento

                if not diagnostico and detalle.estado and detalle.estado != "Sano":
                    sufijo = ""
                    if detalle.superficie and detalle.superficie != "General":
                        sufijo = f" - {detalle.superficie}"
                    diagnostico = f"{detalle.estado}{sufijo}"

                if not observaciones and detalle.observaciones:
                    observaciones = detalle.observaciones

                if procedimiento and diagnostico and observaciones:
                    break

    if not diagnostico:
        diagnostico = (paciente.motivo_consulta or "").strip()

    return {
        "numero_diente": numero_diente,
        "procedimiento": procedimiento,
        "diagnostico": diagnostico,
        "observaciones": observaciones,
    }


def _generar_consentimiento_precargado(
    ruta_pdf,
    paciente,
    numero_diente="",
    procedimiento="",
    diagnostico="",
    observaciones=""
):
    import fitz

    datos_clinicos = _obtener_datos_clinicos_consentimiento(
        paciente,
        numero_diente=numero_diente,
        procedimiento=procedimiento,
        diagnostico=diagnostico,
        observaciones=observaciones
    )

    numero_diente = datos_clinicos["numero_diente"]
    procedimiento = datos_clinicos["procedimiento"]
    diagnostico = datos_clinicos["diagnostico"]
    observaciones = datos_clinicos["observaciones"]

    documento = fitz.open(str(ruta_pdf))
    pagina = _pagina_datos_consentimiento(documento)

    nombre_completo = f"{paciente.nombre} {paciente.apellidos}".strip()
    edad = _calcular_edad_paciente(paciente.fecha_nacimiento)

    _escribir_campo_pdf(
        pagina,
        [
            "HISTORIA CLÍNICA N.°:",
            "HISTORIA CLÍNICA N.°",
            "HISTORIA CLÍNICA",
            "Historia Clínica N.°:"
        ],
        paciente.numero_historia,
        ancho_maximo=160,
        ancho_minimo_linea=20
    )

    _escribir_fecha_pdf(
        pagina,
        datetime.now().strftime("%d/%m/%Y")
    )

    _escribir_campo_pdf(
        pagina,
        ["Nombre completo:"],
        nombre_completo,
        ancho_maximo=320,
        ancho_minimo_linea=50
    )

    _escribir_campo_pdf(
        pagina,
        ["Documento de identidad:", "ntidad:"],
        paciente.documento_identidad or "",
        ancho_maximo=200,
        ancho_minimo_linea=50
    )

    if paciente.fecha_nacimiento:
        _escribir_campo_pdf(
            pagina,
            ["Fecha de nacimiento:"],
            paciente.fecha_nacimiento.strftime("%d/%m/%Y"),
            ancho_maximo=180,
            ancho_minimo_linea=50
        )

    _escribir_campo_pdf(
        pagina,
        ["Edad:"],
        f"{edad} años" if edad != "" else "",
        ancho_maximo=100,
        ancho_minimo_linea=30
    )

    _escribir_campo_pdf(
        pagina,
        ["Sexo:", "Género:", "Genero:"],
        paciente.genero or "",
        ancho_maximo=150,
        ancho_minimo_linea=40
    )

    _escribir_campo_pdf(
        pagina,
        ["Teléfono:"],
        paciente.telefono or "",
        ancho_maximo=210,
        ancho_minimo_linea=50
    )

    _escribir_campo_pdf(
        pagina,
        ["Dirección:", "Domicilio:"],
        paciente.domicilio or "",
        ancho_maximo=320,
        ancho_minimo_linea=60
    )

    # Datos de la responsable del consultorio.
    _escribir_datos_odontologa_pdf(pagina)

    diente_insertado = False
    diagnostico_insertado = False
    procedimiento_insertado = False

    if numero_diente:
        diente_insertado = _escribir_campo_pdf(
            pagina,
            [
                "Diente(s) o zona(s) a intervenir:",
                "Diente(s) a tratar:",
                "Dientes a tratar:",
                "Dientes a intervenir:",
                "Dientes comprometidos:",
                "Diente(s) pilar(es):",
                "Dientes pilares:",
                "Zona(s) a intervenir:",
                "Zona(s):",
                "Diente(s):",
                "Diente:"
            ],
            numero_diente,
            ancho_maximo=180,
            ancho_minimo_linea=45
        )

        arcada, cuadrante = _datos_diente_fdi(numero_diente)

        _escribir_campo_pdf(
            pagina,
            ["Cuadrante:"],
            cuadrante,
            ancho_maximo=190,
            ancho_minimo_linea=35,
            tamano=7
        )

        _marcar_arcada_pdf(pagina, arcada)

        # En el consentimiento de terceros molares los números 18, 28,
        # 38 y 48 ya están impresos. Marcamos la pieza elegida.
        if ruta_pdf.name == "10_exodoncia_terceros_molares.pdf":
            coincidencias = pagina.search_for(str(numero_diente))

            if coincidencias:
                pieza = coincidencias[0]
                margen = 4

                pagina.draw_rect(
                    fitz.Rect(
                        pieza.x0 - margen,
                        pieza.y0 - margen,
                        pieza.x1 + margen,
                        pieza.y1 + margen
                    ),
                    color=(0, 0, 0),
                    width=1.5,
                    overlay=True
                )

    if diagnostico:
        diagnostico_insertado = _escribir_campo_pdf(
            pagina,
            [
                "Diagnóstico clínico:",
                "DIAGNÓSTICO CLÍNICO",
                "Diagnóstico:",
                "Diagnóstico periodontal:",
                "Diagnóstico ortodóncico:",
                "Diagnóstico estético y funcional:",
                "Diagnóstico pulpar:"
            ],
            diagnostico,
            ancho_maximo=340,
            ancho_minimo_linea=50,
            tamano=7
        )

    if procedimiento:
        procedimiento_insertado = _escribir_campo_pdf(
            pagina,
            [
                "Tratamiento odontológico asociado:",
                "Descripción del procedimiento:",
                "Otro procedimiento:",
                "MOTIVO DE ATENCIÓN",
                "Motivo de atención:"
            ],
            procedimiento,
            ancho_maximo=360,
            ancho_minimo_linea=45,
            tamano=7
        )

    # En exodoncia el motivo suele corresponder mejor al diagnóstico/observación.
    motivo = observaciones or diagnostico
    if motivo:
        _escribir_campo_pdf(
            pagina,
            ["Motivo de la exodoncia:", "Motivo de la extracción:"],
            motivo,
            ancho_maximo=340,
            ancho_minimo_linea=50,
            tamano=7
        )

    observaciones_insertadas = _rellenar_observaciones_documento(
        documento,
        observaciones
    )

    faltan_datos_clinicos = (
        (numero_diente and not diente_insertado)
        or (procedimiento and not procedimiento_insertado)
        or (diagnostico and not diagnostico_insertado)
        or (observaciones and not observaciones_insertadas)
    )

    if faltan_datos_clinicos:
        _agregar_resumen_clinico_pdf(
            documento,
            paciente,
            numero_diente,
            procedimiento,
            diagnostico,
            observaciones
        )

    salida = BytesIO()

    documento.save(
        salida,
        garbage=4,
        deflate=True
    )

    documento.close()
    salida.seek(0)

    return salida


@app.route("/pacientes/<int:paciente_id>/consentimientos/pdf")
@login_required
def consentimiento_pdf_precargado(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)

    tipo = (request.args.get("tipo") or "").strip()
    numero_diente = (request.args.get("diente") or "").strip()
    procedimiento = (request.args.get("procedimiento") or "").strip()
    diagnostico = (request.args.get("diagnostico") or "").strip()
    observaciones = (request.args.get("observaciones") or "").strip()

    archivo_pdf = CONSENTIMIENTOS_PDF.get(tipo)

    if not archivo_pdf:
        abort(404)

    ruta_pdf = (
        Path(app.root_path)
        / "static"
        / "consentimientos"
        / archivo_pdf
    )

    if not ruta_pdf.exists():
        abort(404)

    try:
        pdf_precargado = _generar_consentimiento_precargado(
            ruta_pdf,
            paciente,
            numero_diente=numero_diente,
            procedimiento=procedimiento,
            diagnostico=diagnostico,
            observaciones=observaciones
        )
    except ImportError:
        return (
            "Falta instalar PyMuPDF. En la terminal del proyecto ejecuta: "
            "pip install PyMuPDF",
            500
        )

    nombre_salida = (
        f"consentimiento_{paciente.numero_historia}_{archivo_pdf}"
    )

    return send_file(
        pdf_precargado,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=nombre_salida,
        max_age=0
    )


# =========================================================
# GUARDAR CONSENTIMIENTO INFORMADO
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/consentimientos",
    methods=["POST"]
)
@login_required
def guardar_consentimiento(paciente_id):

    paciente = Paciente.query.get_or_404(
        paciente_id
    )

    tipo = (
        request.form.get("tipo") or ""
    ).strip()

    procedimiento = (
        request.form.get("procedimiento") or ""
    ).strip()

    firmado_paciente = (
        request.form.get("firmado_paciente") == "on"
    )

    firma_paciente = (
        request.form.get("firma_paciente") or ""
    ).strip()

    if firma_paciente:
        if (
            not firma_paciente.startswith("data:image/png;base64,")
            or len(firma_paciente) > 2000000
        ):
            flash(
                "La firma capturada no es válida. Intenta firmar nuevamente."
            )

            return redirect(
                url_for(
                    "expediente_paciente",
                    paciente_id=paciente.id,
                    tab="consentimientos"
                )
            )

        firmado_paciente = True

    observaciones = (
        request.form.get("observaciones") or ""
    ).strip()

    archivo_pdf = CONSENTIMIENTOS_PDF.get(tipo)

    if not archivo_pdf:

        flash(
            "Selecciona uno de los consentimientos oficiales de la clínica."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="consentimientos"
            )
        )

    nombre_paciente = (
        f"{paciente.nombre} {paciente.apellidos}"
    ).strip()

    nuevo_consentimiento = Consentimiento(
        paciente_id=paciente.id,
        tipo=tipo,
        procedimiento=procedimiento or None,
        contenido=f"PDF oficial utilizado: {archivo_pdf}",
        firmado_paciente=firmado_paciente,
        nombre_paciente=nombre_paciente,
        firma_paciente=firma_paciente or None,
        observaciones=observaciones or None
    )

    db.session.add(
        nuevo_consentimiento
    )

    db.session.commit()

    flash(
        "Consentimiento oficial registrado correctamente."
    )

    return redirect(
        url_for(
            "expediente_paciente",
            paciente_id=paciente.id,
            tab="consentimientos"
        )
    )


# =========================================================
# AGENDA GENERAL DE CITAS
# =========================================================

@app.route("/citas")
@login_required
def agenda_citas():

    fecha_filtro = (
        request.args.get("fecha") or ""
    ).strip()

    estado_filtro = (
        request.args.get("estado") or ""
    ).strip()

    busqueda = (
        request.args.get("q") or ""
    ).strip()

    consulta = Cita.query

    if fecha_filtro:

        try:

            fecha_consulta = datetime.strptime(
                fecha_filtro,
                "%Y-%m-%d"
            ).date()

            consulta = consulta.filter(
                Cita.fecha == fecha_consulta
            )

        except ValueError:

            flash(
                "La fecha utilizada para filtrar no es válida."
            )

            fecha_filtro = ""

    estados_validos = {
        "Programada",
        "Confirmada",
        "En atención",
        "Atendida",
        "Cancelada",
        "No asistió"
    }

    if estado_filtro in estados_validos:

        consulta = consulta.filter(
            Cita.estado == estado_filtro
        )

    elif estado_filtro:

        estado_filtro = ""

    lista_citas = consulta.order_by(
        Cita.fecha.asc(),
        Cita.hora.asc()
    ).all()

    if busqueda:

        termino = busqueda.casefold()

        lista_citas = [
            cita
            for cita in lista_citas
            if (
                termino in (
                    f"{cita.paciente.nombre} "
                    f"{cita.paciente.apellidos}"
                ).casefold()
                or termino in (
                    cita.motivo or ""
                ).casefold()
                or termino in (
                    cita.odontologo or ""
                ).casefold()
            )
        ]

    hoy = datetime.now().date()

    total_citas = Cita.query.count()

    citas_hoy = Cita.query.filter(
        Cita.fecha == hoy
    ).count()

    citas_pendientes = Cita.query.filter(
        Cita.fecha >= hoy,
        Cita.estado.in_(
            ["Programada", "Confirmada"]
        )
    ).count()

    citas_atendidas = Cita.query.filter(
        Cita.estado == "Atendida"
    ).count()

    return render_template(
        "citas/index.html",
        citas=lista_citas,
        fecha_filtro=fecha_filtro,
        estado_filtro=estado_filtro,
        busqueda=busqueda,
        total_citas=total_citas,
        citas_hoy=citas_hoy,
        citas_pendientes=citas_pendientes,
        citas_atendidas=citas_atendidas
    )


# =========================================================
# ACTUALIZAR ESTADO DE UNA CITA
# =========================================================

@app.route(
    "/citas/<int:cita_id>/estado",
    methods=["POST"]
)
@login_required
def actualizar_estado_cita(cita_id):

    cita = Cita.query.get_or_404(
        cita_id
    )

    nuevo_estado = (
        request.form.get("estado") or ""
    ).strip()

    estados_validos = {
        "Programada",
        "Confirmada",
        "En atención",
        "Atendida",
        "Cancelada",
        "No asistió"
    }

    if nuevo_estado not in estados_validos:

        flash(
            "El estado seleccionado para la cita no es válido."
        )

        return redirect(
            request.referrer
            or url_for("agenda_citas")
        )

    cita.estado = nuevo_estado

    db.session.commit()

    flash(
        "Estado de la cita actualizado correctamente."
    )

    return redirect(
        request.referrer
        or url_for("agenda_citas")
    )


# =========================================================
# GUARDAR CITA
# =========================================================

@app.route(
    "/pacientes/<int:paciente_id>/citas",
    methods=["POST"]
)
@login_required
def guardar_cita(paciente_id):

    paciente = Paciente.query.get_or_404(
        paciente_id
    )

    tratamiento_id = request.form.get(
        "tratamiento_id"
    )

    fecha_texto = request.form.get(
        "fecha"
    )

    hora_texto = request.form.get(
        "hora"
    )

    motivo = request.form.get(
        "motivo"
    )

    odontologo = request.form.get(
        "odontologo"
    )

    estado = request.form.get(
        "estado"
    )

    observaciones = request.form.get(
        "observaciones"
    )

    # =====================================================
    # VALIDACIONES BÁSICAS
    # =====================================================

    if not fecha_texto or not hora_texto or not motivo:

        flash(
            "Fecha, hora y motivo son obligatorios."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="citas"
            )
        )

    # Convertir fecha y hora del formulario
    try:

        fecha = datetime.strptime(
            fecha_texto,
            "%Y-%m-%d"
        ).date()

        hora = datetime.strptime(
            hora_texto,
            "%H:%M"
        ).time()

    except ValueError:

        flash(
            "La fecha o la hora ingresada no es válida."
        )

        return redirect(
            url_for(
                "expediente_paciente",
                paciente_id=paciente.id,
                tab="citas"
            )
        )

    estados_validos = {
        "Programada",
        "Confirmada",
        "En atención",
        "Atendida",
        "Cancelada",
        "No asistió"
    }

    if estado not in estados_validos:
        estado = "Programada"

    # =====================================================
    # VALIDAR TRATAMIENTO ASOCIADO
    # =====================================================

    tratamiento = None

    if tratamiento_id:

        try:
            tratamiento_id = int(
                tratamiento_id
            )
        except ValueError:

            flash(
                "El tratamiento seleccionado no es válido."
            )

            return redirect(
                url_for(
                    "expediente_paciente",
                    paciente_id=paciente.id,
                    tab="citas"
                )
            )

        tratamiento = Tratamiento.query.filter_by(
            id=tratamiento_id,
            paciente_id=paciente.id
        ).first()

        if not tratamiento:

            flash(
                "El tratamiento seleccionado no pertenece a este paciente."
            )

            return redirect(
                url_for(
                    "expediente_paciente",
                    paciente_id=paciente.id,
                    tab="citas"
                )
            )

    # =====================================================
    # CREAR CITA
    # =====================================================

    nueva_cita = Cita(
        paciente_id=paciente.id,
        tratamiento_id=(
            tratamiento.id
            if tratamiento
            else None
        ),
        fecha=fecha,
        hora=hora,
        motivo=motivo.strip(),
        odontologo=(
            odontologo.strip()
            if odontologo
            else None
        ),
        estado=estado,
        observaciones=(
            observaciones.strip()
            if observaciones
            else None
        )
    )

    db.session.add(
        nueva_cita
    )

    db.session.commit()

    flash(
        "Cita registrada correctamente."
    )

    return redirect(
        url_for(
            "expediente_paciente",
            paciente_id=paciente.id,
            tab="citas"
        )
    )



# =========================================================
# REPORTES
# =========================================================

def _parsear_fecha_reporte(valor):
    """Convierte YYYY-MM-DD a date. Si no es válida, devuelve None."""
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _fecha_en_rango(fecha_valor, fecha_inicio=None, fecha_fin=None):
    """Comprueba si una fecha/date-time se encuentra dentro del rango indicado."""
    if fecha_valor is None:
        return False

    if hasattr(fecha_valor, "date"):
        fecha_comparable = fecha_valor.date()
    else:
        fecha_comparable = fecha_valor

    if fecha_inicio and fecha_comparable < fecha_inicio:
        return False
    if fecha_fin and fecha_comparable > fecha_fin:
        return False
    return True


@app.route("/reportes")
@login_required
def reportes():
    fecha_inicio_txt = request.args.get("fecha_inicio", "").strip()
    fecha_fin_txt = request.args.get("fecha_fin", "").strip()

    fecha_inicio = _parsear_fecha_reporte(fecha_inicio_txt)
    fecha_fin = _parsear_fecha_reporte(fecha_fin_txt)

    # Si el usuario escribe el rango al revés, lo corregimos para no fallar.
    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        fecha_inicio, fecha_fin = fecha_fin, fecha_inicio
        fecha_inicio_txt = fecha_inicio.isoformat()
        fecha_fin_txt = fecha_fin.isoformat()

    pacientes_activos = Paciente.query.filter_by(activo=True).order_by(
        Paciente.apellidos.asc(), Paciente.nombre.asc()
    ).all()

    citas = Cita.query.order_by(Cita.fecha.desc(), Cita.hora.desc()).all()
    tratamientos = Tratamiento.query.order_by(Tratamiento.fecha_registro.desc()).all()
    notas = NotaEvolucion.query.order_by(NotaEvolucion.fecha.desc()).all()
    consentimientos = Consentimiento.query.order_by(Consentimiento.fecha.desc()).all()

    if fecha_inicio or fecha_fin:
        citas = [
            c for c in citas
            if _fecha_en_rango(c.fecha, fecha_inicio, fecha_fin)
        ]
        tratamientos = [
            t for t in tratamientos
            if _fecha_en_rango(t.fecha_registro, fecha_inicio, fecha_fin)
        ]
        notas = [
            n for n in notas
            if _fecha_en_rango(n.fecha, fecha_inicio, fecha_fin)
        ]
        consentimientos = [
            c for c in consentimientos
            if _fecha_en_rango(c.fecha, fecha_inicio, fecha_fin)
        ]

    estados_citas_orden = [
        "Programada", "Confirmada", "En atención", "Atendida", "Cancelada", "No asistió"
    ]
    estados_tratamientos_orden = [
        "Pendiente", "En proceso", "Completado", "Cancelado"
    ]

    citas_por_estado = {
        estado: sum(1 for cita in citas if cita.estado == estado)
        for estado in estados_citas_orden
    }

    tratamientos_por_estado = {
        estado: sum(1 for t in tratamientos if t.estado == estado)
        for estado in estados_tratamientos_orden
    }

    # Procedimientos más frecuentes, sin depender de librerías extra.
    conteo_procedimientos = {}
    for tratamiento in tratamientos:
        nombre = (tratamiento.procedimiento or "Sin especificar").strip() or "Sin especificar"
        conteo_procedimientos[nombre] = conteo_procedimientos.get(nombre, 0) + 1

    procedimientos_frecuentes = sorted(
        conteo_procedimientos.items(),
        key=lambda item: (-item[1], item[0].lower())
    )[:8]

    consentimientos_firmados = sum(
        1 for consentimiento in consentimientos
        if consentimiento.firmado_paciente
    )

    resumen = {
        "pacientes_activos": len(pacientes_activos),
        "citas": len(citas),
        "tratamientos": len(tratamientos),
        "tratamientos_completados": sum(
            1 for t in tratamientos if t.estado == "Completado"
        ),
        "notas": len(notas),
        "consentimientos": len(consentimientos),
        "consentimientos_firmados": consentimientos_firmados,
    }

    return render_template(
        "reportes/index.html",
        pacientes=pacientes_activos,
        citas=citas[:12],
        tratamientos=tratamientos[:12],
        resumen=resumen,
        citas_por_estado=citas_por_estado,
        tratamientos_por_estado=tratamientos_por_estado,
        procedimientos_frecuentes=procedimientos_frecuentes,
        fecha_inicio=fecha_inicio_txt,
        fecha_fin=fecha_fin_txt,
    )


@app.route("/reportes/paciente/<int:paciente_id>")
@login_required
def reporte_paciente(paciente_id):
    paciente = db.get_or_404(Paciente, paciente_id)

    antecedentes = AntecedenteMedico.query.filter_by(
        paciente_id=paciente.id
    ).first()

    examen = ExamenClinico.query.filter_by(
        paciente_id=paciente.id
    ).first()

    tratamientos = Tratamiento.query.filter_by(
        paciente_id=paciente.id
    ).order_by(Tratamiento.fecha_registro.desc()).all()

    citas = Cita.query.filter_by(
        paciente_id=paciente.id
    ).order_by(Cita.fecha.desc(), Cita.hora.desc()).all()

    notas = NotaEvolucion.query.filter_by(
        paciente_id=paciente.id
    ).order_by(NotaEvolucion.fecha.desc()).all()

    consentimientos = Consentimiento.query.filter_by(
        paciente_id=paciente.id
    ).order_by(Consentimiento.fecha.desc()).all()

    odontograma = OdontogramaDetalle.query.filter_by(
        paciente_id=paciente.id
    ).order_by(OdontogramaDetalle.numero_diente.asc()).all()

    # Mostrar solamente hallazgos relevantes del odontograma en el reporte.
    odontograma_relevante = [
        item for item in odontograma
        if (item.estado and item.estado != "Sano")
        or (item.procedimiento and item.procedimiento.strip())
        or (item.observaciones and item.observaciones.strip())
    ]

    edad = None
    if paciente.fecha_nacimiento:
        hoy = datetime.now().date()
        edad = hoy.year - paciente.fecha_nacimiento.year - (
            (hoy.month, hoy.day)
            < (paciente.fecha_nacimiento.month, paciente.fecha_nacimiento.day)
        )

    return render_template(
        "reportes/paciente.html",
        paciente=paciente,
        edad=edad,
        antecedentes=antecedentes,
        examen=examen,
        tratamientos=tratamientos,
        citas=citas,
        notas=notas,
        consentimientos=consentimientos,
        odontograma=odontograma_relevante,
        fecha_emision=datetime.now(),
        datos_odontologa=DATOS_ODONTOLOGA,
    )


# =========================================================
# CONFIGURACIÓN
# =========================================================

@app.route("/configuracion")
@login_required
def configuracion():
    return render_template(
        "configuracion/index.html",
        datos_odontologa=DATOS_ODONTOLOGA,
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


# =========================================================
# EJECUTAR APLICACIÓN
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
