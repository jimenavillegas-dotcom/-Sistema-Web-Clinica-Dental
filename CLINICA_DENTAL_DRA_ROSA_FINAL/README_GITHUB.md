# Sistema Web de la Clinica Dental Dra. Rosa Elisa Arriaga

Proyecto academico de JN TAPIA INNOVATIONS.

## Preparacion
1. Instalar Python y MySQL.
2. Importar BASE_DE_DATOS/consultorio_dental_INSTALACION_FINAL.sql (sin datos iniciales de usuario).
3. En SISTEMA, copiar .env.example a .env y sustituir los valores de ejemplo, incluida SECRET_KEY por una clave aleatoria segura. **No subir .env a GitHub.**
4. Crear el entorno virtual e instalar dependencias desde SISTEMA:
   ```powershell
   python -m venv venv
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
5. Ejecutar, si es necesario, `datos_iniciales.py` para preparar los roles:
   ```powershell
   .\venv\Scripts\python.exe datos_iniciales.py
   ```
6. Para crear el administrador, primero establecer las variables de entorno ADMIN_EMAIL, ADMIN_PASSWORD y opcionalmente ADMIN_NOMBRE; luego ejecutar `crear_admin.py`. No usar contrasenas publicas o predeterminadas.
7. Iniciar el servidor en entorno local con `python app.py`. **Antes de desplegarlo para uso real, desactivar el modo debug y realizar una revision completa de seguridad y privacidad.**

Este repositorio no debe incluir datos reales de pacientes ni secretos.
