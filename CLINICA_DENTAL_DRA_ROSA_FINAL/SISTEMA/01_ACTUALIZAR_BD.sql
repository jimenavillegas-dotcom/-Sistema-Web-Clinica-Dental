USE consultorio_dental;

ALTER TABLE consentimientos
ADD COLUMN firma_paciente LONGTEXT NULL
AFTER nombre_paciente;

DESCRIBE consentimientos;
