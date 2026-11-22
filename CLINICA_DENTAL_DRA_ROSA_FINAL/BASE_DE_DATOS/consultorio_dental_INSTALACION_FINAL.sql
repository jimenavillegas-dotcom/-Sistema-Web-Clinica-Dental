-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: consultorio_dental
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `antecedentes_medicos`
--

DROP TABLE IF EXISTS `antecedentes_medicos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `antecedentes_medicos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paciente_id` int NOT NULL,
  `tabaquismo` tinyint(1) DEFAULT NULL,
  `alcohol` tinyint(1) DEFAULT NULL,
  `otras_sustancias` tinyint(1) DEFAULT NULL,
  `detalle_sustancias` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `habito_oral` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enfermedad_ultimo_anio` tinyint(1) DEFAULT NULL,
  `detalle_enfermedad` text COLLATE utf8mb4_unicode_ci,
  `tratamiento_medico` tinyint(1) DEFAULT NULL,
  `detalle_tratamiento` text COLLATE utf8mb4_unicode_ci,
  `alergias` tinyint(1) DEFAULT NULL,
  `detalle_alergias` text COLLATE utf8mb4_unicode_ci,
  `anestesia_previa` tinyint(1) DEFAULT NULL,
  `reaccion_anestesia` tinyint(1) DEFAULT NULL,
  `detalle_reaccion_anestesia` text COLLATE utf8mb4_unicode_ci,
  `sangrado_excesivo` tinyint(1) DEFAULT NULL,
  `sitio_sangrado` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `diabetes` tinyint(1) DEFAULT NULL,
  `hipertension` tinyint(1) DEFAULT NULL,
  `hipotension` tinyint(1) DEFAULT NULL,
  `enfermedad_venerea` tinyint(1) DEFAULT NULL,
  `hepatitis` tinyint(1) DEFAULT NULL,
  `asma` tinyint(1) DEFAULT NULL,
  `epilepsia` tinyint(1) DEFAULT NULL,
  `artritis` tinyint(1) DEFAULT NULL,
  `cancer` tinyint(1) DEFAULT NULL,
  `vih_sida` tinyint(1) DEFAULT NULL,
  `otros_padecimientos` text COLLATE utf8mb4_unicode_ci,
  `antecedentes_heredofamiliares` text COLLATE utf8mb4_unicode_ci,
  `embarazada` tinyint(1) DEFAULT NULL,
  `meses_embarazo` int DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `paciente_id` (`paciente_id`),
  CONSTRAINT `antecedentes_medicos_ibfk_1` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `antecedentes_medicos`
--

LOCK TABLES `antecedentes_medicos` WRITE;
/*!40000 ALTER TABLE `antecedentes_medicos` DISABLE KEYS */;
/*!40000 ALTER TABLE `antecedentes_medicos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `citas`
--

DROP TABLE IF EXISTS `citas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `citas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paciente_id` int NOT NULL,
  `tratamiento_id` int DEFAULT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `motivo` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `odontologo` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `fecha_registro` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `paciente_id` (`paciente_id`),
  KEY `tratamiento_id` (`tratamiento_id`),
  CONSTRAINT `citas_ibfk_1` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`),
  CONSTRAINT `citas_ibfk_2` FOREIGN KEY (`tratamiento_id`) REFERENCES `tratamientos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `citas`
--

LOCK TABLES `citas` WRITE;
/*!40000 ALTER TABLE `citas` DISABLE KEYS */;
/*!40000 ALTER TABLE `citas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consentimientos`
--

DROP TABLE IF EXISTS `consentimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consentimientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paciente_id` int NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tipo` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `procedimiento` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contenido` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `firmado_paciente` tinyint(1) NOT NULL DEFAULT '0',
  `nombre_paciente` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `firma_paciente` longtext COLLATE utf8mb4_unicode_ci,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `fk_consentimiento_paciente` (`paciente_id`),
  CONSTRAINT `fk_consentimiento_paciente` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consentimientos`
--

LOCK TABLES `consentimientos` WRITE;
/*!40000 ALTER TABLE `consentimientos` DISABLE KEYS */;
/*!40000 ALTER TABLE `consentimientos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `examenes_clinicos`
--

DROP TABLE IF EXISTS `examenes_clinicos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `examenes_clinicos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paciente_id` int NOT NULL,
  `cara_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cara_observaciones` text COLLATE utf8mb4_unicode_ci,
  `cuello_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cuello_observaciones` text COLLATE utf8mb4_unicode_ci,
  `labios_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `labios_observaciones` text COLLATE utf8mb4_unicode_ci,
  `carrillos_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `carrillos_observaciones` text COLLATE utf8mb4_unicode_ci,
  `paladar_blando_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `paladar_blando_observaciones` text COLLATE utf8mb4_unicode_ci,
  `paladar_duro_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `paladar_duro_observaciones` text COLLATE utf8mb4_unicode_ci,
  `lengua_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lengua_observaciones` text COLLATE utf8mb4_unicode_ci,
  `amigdalas_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `amigdalas_observaciones` text COLLATE utf8mb4_unicode_ci,
  `piso_boca_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `piso_boca_observaciones` text COLLATE utf8mb4_unicode_ci,
  `glandulas_salivales_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `glandulas_salivales_observaciones` text COLLATE utf8mb4_unicode_ci,
  `atm_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `atm_observaciones` text COLLATE utf8mb4_unicode_ci,
  `oclusion_estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `oclusion_observaciones` text COLLATE utf8mb4_unicode_ci,
  `observaciones_generales` text COLLATE utf8mb4_unicode_ci,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `paciente_id` (`paciente_id`),
  CONSTRAINT `examenes_clinicos_ibfk_1` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `examenes_clinicos`
--

LOCK TABLES `examenes_clinicos` WRITE;
/*!40000 ALTER TABLE `examenes_clinicos` DISABLE KEYS */;
/*!40000 ALTER TABLE `examenes_clinicos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notas_evolucion`
--

DROP TABLE IF EXISTS `notas_evolucion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notas_evolucion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paciente_id` int NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `numero_diente` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `procedimiento` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `evolucion` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `indicaciones` text COLLATE utf8mb4_unicode_ci,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `fk_nota_evolucion_paciente` (`paciente_id`),
  CONSTRAINT `fk_nota_evolucion_paciente` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notas_evolucion`
--

LOCK TABLES `notas_evolucion` WRITE;
/*!40000 ALTER TABLE `notas_evolucion` DISABLE KEYS */;
/*!40000 ALTER TABLE `notas_evolucion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `odontograma_detalles`
--

DROP TABLE IF EXISTS `odontograma_detalles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `odontograma_detalles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paciente_id` int NOT NULL,
  `numero_diente` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `superficie` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `procedimiento` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `costo` decimal(10,2) DEFAULT NULL,
  `prioridad` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_paciente_diente_superficie` (`paciente_id`,`numero_diente`,`superficie`),
  CONSTRAINT `odontograma_detalles_ibfk_1` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `odontograma_detalles`
--

LOCK TABLES `odontograma_detalles` WRITE;
/*!40000 ALTER TABLE `odontograma_detalles` DISABLE KEYS */;
/*!40000 ALTER TABLE `odontograma_detalles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `odontograma_historial`
--

DROP TABLE IF EXISTS `odontograma_historial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `odontograma_historial` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paciente_id` int NOT NULL,
  `numero_diente` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `superficie` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado_anterior` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado_nuevo` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `procedimiento` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `fecha` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `paciente_id` (`paciente_id`),
  CONSTRAINT `odontograma_historial_ibfk_1` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `odontograma_historial`
--

LOCK TABLES `odontograma_historial` WRITE;
/*!40000 ALTER TABLE `odontograma_historial` DISABLE KEYS */;
/*!40000 ALTER TABLE `odontograma_historial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pacientes`
--

DROP TABLE IF EXISTS `pacientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pacientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero_historia` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellidos` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `documento_identidad` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lugar_nacimiento` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `domicilio` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ocupacion` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `escolaridad` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado_civil` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `correo` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `motivo_consulta` text COLLATE utf8mb4_unicode_ci,
  `activo` tinyint(1) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_historia` (`numero_historia`),
  UNIQUE KEY `documento_identidad` (`documento_identidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pacientes`
--

LOCK TABLES `pacientes` WRITE;
/*!40000 ALTER TABLE `pacientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `pacientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrador','Acceso completo al sistema'),(2,'Dentista','Acceso a funciones clínicas y tratamientos'),(3,'Recepcionista','Acceso a pacientes, citas y pagos');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tratamientos`
--

DROP TABLE IF EXISTS `tratamientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tratamientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paciente_id` int NOT NULL,
  `numero_diente` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `diagnostico` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `procedimiento` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prioridad` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `costo` decimal(10,2) DEFAULT NULL,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `fecha_registro` datetime DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `paciente_id` (`paciente_id`),
  CONSTRAINT `tratamientos_ibfk_1` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tratamientos`
--

LOCK TABLES `tratamientos` WRITE;
/*!40000 ALTER TABLE `tratamientos` DISABLE KEYS */;
/*!40000 ALTER TABLE `tratamientos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellidos` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `correo` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  `rol_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-20  4:32:38
