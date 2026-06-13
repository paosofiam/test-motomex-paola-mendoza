-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1:3306
-- Tiempo de generación: 13-06-2026 a las 03:51:05
-- Versión del servidor: 11.8.6-MariaDB-log
-- Versión de PHP: 7.2.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `u330975583_motomex`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('0019_estados_abreviacion');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `categoria` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id`, `created_at`, `updated_at`, `deleted_at`, `categoria`) VALUES
(24, '2026-06-08 18:03:04', '2026-06-08 18:03:04', NULL, 'bateria'),
(26, '2026-06-08 18:06:58', '2026-06-08 18:06:58', NULL, 'frenos'),
(29, '2026-06-08 18:06:58', '2026-06-08 18:06:58', NULL, 'balatas'),
(32, '2026-06-08 18:06:58', '2026-06-08 18:06:58', NULL, 'automotriz'),
(35, '2026-06-08 18:06:59', '2026-06-08 18:06:59', NULL, 'sistema electrico'),
(36, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'bomba de agua'),
(37, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'sistema de enfriamiento'),
(38, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'filtros'),
(40, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'motor'),
(41, '2026-06-08 18:07:24', '2026-06-08 18:07:24', NULL, 'filtro de aceite'),
(43, '2026-06-08 18:07:24', '2026-06-08 18:07:24', NULL, 'mantenimiento'),
(44, '2026-06-08 19:24:19', '2026-06-08 19:24:19', NULL, 'electrico'),
(45, '2026-06-08 19:27:09', '2026-06-08 19:27:09', NULL, 'suspension'),
(46, '2026-06-08 19:27:09', '2026-06-08 19:27:09', NULL, 'amortiguador'),
(47, '2026-06-08 19:27:22', '2026-06-08 19:27:22', NULL, 'banda de distribucion'),
(48, '2026-06-08 19:27:28', '2026-06-08 19:27:28', NULL, 'refrigeracion'),
(49, '2026-06-08 23:24:11', '2026-06-08 23:24:11', NULL, 'aceite'),
(50, '2026-06-08 23:24:13', '2026-06-08 23:24:13', NULL, 'bandas');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `chats`
--

CREATE TABLE `chats` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `lead_id` int(11) NOT NULL,
  `chat_whatsapp_id` varchar(255) NOT NULL,
  `chat_status_id` int(11) NOT NULL,
  `resumen` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `chats`
--

INSERT INTO `chats` (`id`, `created_at`, `updated_at`, `deleted_at`, `lead_id`, `chat_whatsapp_id`, `chat_status_id`, `resumen`) VALUES
(1, '2026-06-12 22:58:18', '2026-06-12 22:58:18', '2026-06-12 23:00:26', 1, '6771465876', 1, 'Conversacion iniciada desde Telegram'),
(2, '2026-06-12 23:03:20', '2026-06-12 23:11:37', '2026-06-12 23:21:15', 1, '6771465876', 1, 'Conversación retomada'),
(3, '2026-06-12 23:08:11', '2026-06-12 23:24:27', '2026-06-12 23:26:22', 2, '716082462', 5, 'Venta cerrada. compra confirmada'),
(4, '2026-06-12 23:21:29', '2026-06-12 23:55:32', '2026-06-13 00:19:39', 1, '6771465876', 5, 'Venta cerrada. compra confirmada'),
(5, '2026-06-12 23:27:24', '2026-06-12 23:27:24', NULL, 2, '716082462', 1, 'Conversacion iniciada desde Telegram'),
(6, '2026-06-13 00:21:17', '2026-06-13 00:41:22', '2026-06-12 18:49:41', 1, '6771465876', 5, 'Venta cerrada. compra confirmada'),
(7, '2026-06-13 00:50:21', '2026-06-13 00:55:46', '2026-06-13 00:55:47', 1, '6771465876', 5, 'Venta cerrada. compra confirmada'),
(8, '2026-06-13 01:07:43', '2026-06-13 01:18:16', '2026-06-13 01:20:17', 3, '6771465876', 5, 'Venta cerrada. compra confirmada'),
(9, '2026-06-13 03:31:11', '2026-06-13 03:44:01', NULL, 3, '6771465876', 2, 'Venta cerrada. compra confirmada');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `chat_statuses`
--

CREATE TABLE `chat_statuses` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `chat_statuses`
--

INSERT INTO `chat_statuses` (`id`, `created_at`, `updated_at`, `deleted_at`, `status`) VALUES
(1, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'activo'),
(2, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'en revisión'),
(3, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'en espera'),
(4, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'con cliente'),
(5, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'cerrado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ciudades`
--

CREATE TABLE `ciudades` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `ciudad` varchar(255) NOT NULL,
  `estado_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `ciudades`
--

INSERT INTO `ciudades` (`id`, `created_at`, `updated_at`, `deleted_at`, `ciudad`, `estado_id`) VALUES
(1, '2026-06-08 18:03:04', '2026-06-08 18:03:04', NULL, 'monterrey', 19),
(2, '2026-06-08 18:06:58', '2026-06-08 18:06:58', NULL, 'guadalajara', 15),
(3, '2026-06-08 18:07:24', '2026-06-08 18:07:24', NULL, 'leon', 12),
(4, '2026-06-08 18:07:25', '2026-06-08 18:07:25', NULL, 'ciudad de mexico', 7),
(5, '2026-06-08 19:27:09', '2026-06-08 19:27:09', NULL, 'puebla', 21),
(6, '2026-06-08 19:27:22', '2026-06-08 19:27:22', NULL, 'queretaro', 22),
(7, '2026-06-12 23:24:18', '2026-06-12 23:24:18', NULL, 'san nicolas de los garza', 19),
(8, '2026-06-13 03:43:54', '2026-06-13 03:43:54', NULL, 'tlalnepantla', 7);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estados`
--

CREATE TABLE `estados` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `estado` varchar(255) NOT NULL,
  `abreviacion` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `estados`
--

INSERT INTO `estados` (`id`, `created_at`, `updated_at`, `deleted_at`, `estado`, `abreviacion`) VALUES
(1, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Aguascalientes', 'AGS'),
(2, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Baja California', 'BC'),
(3, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Baja California Sur', 'BCS'),
(4, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Campeche', 'CAMP'),
(5, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Chiapas', 'CHIS'),
(6, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Chihuahua', 'CHIH'),
(7, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Ciudad de México', 'CDMX'),
(8, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Coahuila', 'COAH'),
(9, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Colima', 'COL'),
(10, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Durango', 'DGO'),
(11, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Estado de México', 'EDOMEX'),
(12, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Guanajuato', 'GTO'),
(13, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Guerrero', 'GRO'),
(14, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Hidalgo', 'HGO'),
(15, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Jalisco', 'JAL'),
(16, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Michoacán', 'MICH'),
(17, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Morelos', 'MOR'),
(18, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Nayarit', 'NAY'),
(19, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Nuevo León', 'NL'),
(20, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Oaxaca', 'OAX'),
(21, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Puebla', 'PUE'),
(22, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Querétaro', 'QRO'),
(23, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Quintana Roo', 'QROO'),
(24, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'San Luis Potosí', 'SLP'),
(25, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Sinaloa', 'SIN'),
(26, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Sonora', 'SON'),
(27, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Tabasco', 'TAB'),
(28, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Tamaulipas', 'TAMPS'),
(29, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Tlaxcala', 'TLAX'),
(30, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Veracruz', 'VER'),
(31, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Yucatán', 'YUC'),
(32, '2026-06-08 17:34:55', '2026-06-08 17:34:55', NULL, 'Zacatecas', 'ZAC');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `intenciones_de_compra_de_leads`
--

CREATE TABLE `intenciones_de_compra_de_leads` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `tipo` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `intenciones_de_compra_de_leads`
--

INSERT INTO `intenciones_de_compra_de_leads` (`id`, `created_at`, `updated_at`, `deleted_at`, `tipo`) VALUES
(1, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'baja'),
(2, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'media'),
(3, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'alta'),
(4, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'completa');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `leads`
--

CREATE TABLE `leads` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `chat_whatsapp_id` varchar(255) NOT NULL,
  `nombre_whatsapp` varchar(255) NOT NULL,
  `telefono` varchar(15) NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `ciudad_id` int(11) DEFAULT NULL,
  `direccion_envio` varchar(512) DEFAULT NULL,
  `intencion_de_compra_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `leads`
--

INSERT INTO `leads` (`id`, `created_at`, `updated_at`, `deleted_at`, `chat_whatsapp_id`, `nombre_whatsapp`, `telefono`, `nombre`, `ciudad_id`, `direccion_envio`, `intencion_de_compra_id`) VALUES
(1, '2026-06-12 22:58:17', '2026-06-13 00:55:40', NULL, '6778465875', ' ', '+520000000000', 'Paola Sofía Mendoza', 5, 'calle Roma #400 Col Fomerrey, CP 55511', 4),
(2, '2026-06-12 23:08:11', '2026-06-12 23:27:52', NULL, '716082462', ' ', '+520000000000', 'Andree Malerva', 7, 'Av. Diego Díaz 400, colonia pedregal Santo Domingo', 3),
(3, '2026-06-13 01:07:42', '2026-06-13 03:43:54', NULL, '6771465876', ' ', '+520000000000', 'Paola Sofía Mendoza', 8, 'calle xicotencatl #8625, Colonia Cuahutemoc, CP 15159', 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `leads_productos`
--

CREATE TABLE `leads_productos` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `lead_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `leads_vehiculos`
--

CREATE TABLE `leads_vehiculos` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `lead_id` int(11) NOT NULL,
  `vehiculo_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `marcas`
--

CREATE TABLE `marcas` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `marca` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `marcas`
--

INSERT INTO `marcas` (`id`, `created_at`, `updated_at`, `deleted_at`, `marca`) VALUES
(42, '2026-06-08 18:03:04', '2026-06-08 18:03:04', NULL, 'lth'),
(43, '2026-06-08 18:03:04', '2026-06-08 18:03:04', NULL, 'nissan'),
(45, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 'bosch'),
(52, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 'chevrolet'),
(53, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 'renault'),
(57, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 'volkswagen'),
(60, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 'gmb'),
(61, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'fram'),
(64, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'toyota'),
(66, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'honda'),
(69, '2026-06-08 18:24:53', '2026-06-08 18:24:53', NULL, 'testn8n'),
(75, '2026-06-08 18:26:10', '2026-06-08 18:26:10', NULL, 'testn8n2'),
(76, '2026-06-08 18:26:54', '2026-06-08 18:26:54', NULL, 'testn8n3'),
(77, '2026-06-08 18:28:57', '2026-06-08 18:28:57', NULL, 'testchunked'),
(78, '2026-06-08 18:29:29', '2026-06-08 18:29:29', NULL, 'testrepeat1'),
(79, '2026-06-08 18:29:30', '2026-06-08 18:29:30', NULL, 'testrepeat2'),
(80, '2026-06-08 18:29:32', '2026-06-08 18:29:32', NULL, 'testrepeat3'),
(82, '2026-06-08 18:45:55', '2026-06-08 18:45:55', NULL, 'marcaracetest'),
(87, '2026-06-08 19:27:08', '2026-06-08 19:27:08', NULL, 'monroe'),
(88, '2026-06-08 19:27:21', '2026-06-08 19:27:21', NULL, 'gates');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `monedas`
--

CREATE TABLE `monedas` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `moneda` varchar(255) NOT NULL,
  `abreviacion` varchar(10) NOT NULL,
  `tipo_de_cambio` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `monedas`
--

INSERT INTO `monedas` (`id`, `created_at`, `updated_at`, `deleted_at`, `moneda`, `abreviacion`, `tipo_de_cambio`) VALUES
(1, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'Pesos Mexicanos', 'MXN', 100),
(2, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'Dólares', 'USD', 1700),
(3, '2026-06-02 00:00:04', '2026-06-02 00:00:04', NULL, 'Euros', 'EUR', 2300);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pre_ordenes`
--

CREATE TABLE `pre_ordenes` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `lead_id` int(11) NOT NULL,
  `total` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `pre_ordenes`
--

INSERT INTO `pre_ordenes` (`id`, `created_at`, `updated_at`, `deleted_at`, `lead_id`, `total`) VALUES
(1, '2026-06-13 01:18:16', '2026-06-13 01:18:16', NULL, 3, 1),
(2, '2026-06-13 03:44:00', '2026-06-13 03:44:00', NULL, 3, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pre_ordenes_productos`
--

CREATE TABLE `pre_ordenes_productos` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `pre_orden_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `pre_ordenes_productos`
--

INSERT INTO `pre_ordenes_productos` (`id`, `created_at`, `updated_at`, `deleted_at`, `pre_orden_id`, `producto_id`, `cantidad`) VALUES
(1, '2026-06-13 01:18:16', '2026-06-13 01:18:16', NULL, 1, 53, 3),
(2, '2026-06-13 03:44:00', '2026-06-13 03:44:00', NULL, 2, 52, 10);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `marca_id` int(11) NOT NULL,
  `modelo` varchar(255) NOT NULL,
  `precio` int(11) NOT NULL,
  `moneda_id` int(11) NOT NULL,
  `stock` int(11) NOT NULL,
  `especificaciones` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`especificaciones`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id`, `created_at`, `updated_at`, `deleted_at`, `marca_id`, `modelo`, `precio`, `moneda_id`, `stock`, `especificaciones`) VALUES
(14, '2026-06-08 18:03:04', '2026-06-08 18:03:04', '2026-06-08 17:01:18', 42, 'L-47-650', 245000, 1, 8, '{\"tipo\": \"bateria automotriz\", \"voltaje\": \"12V\"}'),
(15, '2026-06-08 18:06:57', '2026-06-08 18:06:57', '2026-06-08 17:01:41', 42, 'L-47-650', 245000, 1, 8, '{\"tipo\": \"bater\\u00eda automotriz\", \"capacidad_arranque_en_frio\": \"650A\", \"voltaje\": \"12V\", \"aplicacion\": \"veh\\u00edculos compactos y sedanes medianos\"}'),
(17, '2026-06-08 18:06:57', '2026-06-08 18:06:57', '2026-06-08 17:01:52', 45, 'BP-1290', 78000, 1, 15, '{\"tipo\": \"balatas delanteras\", \"aplicacion\": \"veh\\u00edculos tipo sed\\u00e1n de uso urbano\", \"material\": \"cer\\u00e1mico\", \"caracteristica\": \"baja generaci\\u00f3n de ruido, recomendadas para conducci\\u00f3n diaria en ciudad\"}'),
(21, '2026-06-08 18:07:22', '2026-06-08 18:07:22', '2026-06-08 17:02:18', 60, 'GWH-780', 95000, 1, 5, '{\"tipo\": \"bomba de agua\", \"sistema\": \"refrigeraci\\u00f3n del motor\", \"motor\": \"GA16\"}'),
(22, '2026-06-08 18:07:23', '2026-06-08 18:07:23', '2026-06-08 17:02:30', 45, 'BP-1290', 78000, 1, 15, '{\"tipo\": \"balatas delanteras\", \"aplicacion\": \"veh\\u00edculos tipo sed\\u00e1n de uso urbano\", \"material\": \"cer\\u00e1mico\", \"caracteristica\": \"baja generaci\\u00f3n de ruido, recomendadas para conducci\\u00f3n diaria en ciudad\"}'),
(23, '2026-06-08 18:07:23', '2026-06-08 18:07:23', '2026-06-08 17:02:42', 61, 'PH-6607', 18500, 1, 42, '{\"tipo\": \"filtro de aceite\", \"aplicacion\": \"motores de 4 cilindros de cilindrada mediana\", \"mantenimiento\": \"preventivo\"}'),
(25, '2026-06-08 18:07:23', '2026-06-08 18:07:23', '2026-06-08 17:02:51', 42, 'L-47-650', 245000, 1, 8, '{\"tipo\": \"bater\\u00eda automotriz\", \"capacidad_arranque_en_frio\": \"650A\", \"voltaje\": \"12V\", \"aplicacion\": \"veh\\u00edculos compactos y sedanes medianos\"}'),
(27, '2026-06-08 18:08:52', '2026-06-08 18:08:52', '2026-06-08 17:03:41', 42, 'L-47-650-test500', 245000, 1, 8, '{}'),
(28, '2026-06-08 18:10:02', '2026-06-08 18:10:02', '2026-06-08 17:03:52', 42, 'L-47-650-v2', 245000, 1, 8, '{\"tipo\": \"bateria automotriz\", \"capacidad_arranque_en_frio\": \"650A\", \"voltaje\": \"12V\", \"aplicacion\": \"vehiculos compactos\"}'),
(29, '2026-06-08 18:13:01', '2026-06-08 18:13:01', '2026-06-08 17:04:04', 42, 'L-47-650-acentos', 245000, 1, 8, '{\"tipo\": \"bater\\u00eda automotriz\", \"capacidad_arranque_en_frio\": \"650A\", \"voltaje\": \"12V\", \"aplicacion\": \"veh\\u00edculos compactos y sedanes medianos\"}'),
(30, '2026-06-08 18:16:00', '2026-06-08 18:16:00', '2026-06-08 17:04:17', 42, 'L-47-650', 245000, 1, 8, '{\"tipo\": \"bater\\u00eda automotriz\", \"capacidad_arranque_en_frio\": \"650A\", \"voltaje\": \"12V\", \"aplicacion\": \"veh\\u00edculos compactos y sedanes medianos\"}'),
(31, '2026-06-08 18:24:53', '2026-06-08 18:24:53', '2026-06-08 17:04:40', 69, 'Test-Directo', 10000, 1, 0, 'null'),
(32, '2026-06-08 18:25:42', '2026-06-08 18:25:42', '2026-06-08 17:04:53', 69, 'Test-Directo', 10000, 1, 0, 'null'),
(33, '2026-06-08 18:26:10', '2026-06-08 18:26:10', '2026-06-08 17:05:04', 75, 'Test-GzipHeader', 10000, 1, 0, 'null'),
(34, '2026-06-08 18:26:54', '2026-06-08 18:26:54', '2026-06-08 17:05:14', 76, 'Test-Ahora', 5000, 1, 0, 'null'),
(35, '2026-06-08 18:28:57', '2026-06-08 18:28:57', '2026-06-08 17:05:28', 77, 'Test-Chunked', 5000, 1, 0, 'null'),
(36, '2026-06-08 18:29:29', '2026-06-08 18:29:29', '2026-06-08 17:05:39', 78, 'Test-Loop-1', 1000, 1, 0, 'null'),
(37, '2026-06-08 18:29:30', '2026-06-08 18:29:30', '2026-06-08 17:05:49', 79, 'Test-Loop-2', 1000, 1, 0, 'null'),
(38, '2026-06-08 18:29:32', '2026-06-08 18:29:32', '2026-06-08 17:05:59', 80, 'Test-Loop-3', 1000, 1, 0, 'null'),
(39, '2026-06-08 18:44:11', '2026-06-08 18:44:11', '2026-06-08 17:06:12', 69, 'Test-Directo', 10000, 1, 0, 'null'),
(40, '2026-06-08 18:45:55', '2026-06-08 18:45:55', '2026-06-08 17:06:26', 82, 'ModeloRace', 1000, 1, 0, 'null'),
(41, '2026-06-08 18:57:11', '2026-06-08 18:57:11', '2026-06-08 17:06:41', 69, 'Test-Directo', 10000, 1, 0, 'null'),
(42, '2026-06-08 19:24:19', '2026-06-08 19:24:19', '2026-06-08 17:06:50', 42, 'L-47-650', 245000, 1, 8, '{\"tipo\": \"bater\\u00eda automotriz\", \"capacidad_arranque_en_frio\": \"650A\", \"voltaje\": \"12V\"}'),
(43, '2026-06-08 19:26:56', '2026-06-08 19:26:56', '2026-06-08 17:07:01', 42, 'L-47-650', 245000, 1, 8, '{\"tipo\": \"bater\\u00eda automotriz\", \"capacidad_arranque_en_frio\": \"650A\", \"voltaje\": \"12V\"}'),
(44, '2026-06-08 19:27:02', '2026-06-08 19:27:02', '2026-06-08 17:07:13', 45, 'BP-1290', 78000, 1, 15, '{\"tipo\": \"balatas delanteras\", \"material\": \"cer\\u00e1mico\", \"uso_recomendado\": \"conducci\\u00f3n diaria en ciudad\"}'),
(45, '2026-06-08 19:27:09', '2026-06-08 19:27:09', '2026-06-08 16:59:26', 87, 'M-3245', 135000, 1, 6, '{\"tipo\": \"amortiguador\", \"posicion\": \"suspensi\\u00f3n delantera\", \"aplicacion\": \"SUVs compactas\", \"unidad_venta\": \"por pieza\"}'),
(46, '2026-06-08 19:27:15', '2026-06-08 19:27:15', '2026-06-08 17:00:11', 61, 'PH-6607', 18500, 1, 42, '{\"tipo\": \"filtro de aceite\", \"aplicacion\": \"motores 4 cilindros de cilindrada mediana\"}'),
(47, '2026-06-08 19:27:21', '2026-06-08 19:27:21', '2026-06-08 17:00:23', 88, 'T-186', 62000, 1, 11, '{\"tipo\": \"banda de distribuci\\u00f3n\", \"sistema\": \"distribuci\\u00f3n del motor\", \"motor\": \"1.6 litros\"}'),
(48, '2026-06-08 19:27:28', '2026-06-08 19:27:28', '2026-06-08 17:00:42', 60, 'GWH-780', 95000, 1, 5, '{\"tipo\": \"bomba de agua\", \"sistema\": \"refrigeraci\\u00f3n del motor\"}'),
(49, '2026-06-08 23:24:05', '2026-06-08 23:24:05', NULL, 42, 'L-47-650', 245000, 1, 8, '{\"tipo\": \"bater\\u00eda automotriz\", \"capacidad_arranque_en_frio\": \"650A\", \"voltaje\": \"12V\"}'),
(50, '2026-06-08 23:24:07', '2026-06-08 23:24:07', NULL, 45, 'BP-1290', 78000, 1, 15, '{\"tipo\": \"balatas delanteras\", \"material\": \"cer\\u00e1mico\", \"uso\": \"conducci\\u00f3n diaria en ciudad\"}'),
(51, '2026-06-08 23:24:09', '2026-06-08 23:24:09', NULL, 87, 'M-3245', 135000, 1, 6, '{\"tipo\": \"amortiguador\", \"posicion\": \"suspensi\\u00f3n delantera\", \"aplicacion\": \"SUVs compactas\"}'),
(52, '2026-06-08 23:24:10', '2026-06-08 23:24:10', NULL, 61, 'PH-6607', 18500, 1, 42, '{\"tipo\": \"filtro de aceite\", \"aplicacion\": \"motores 4 cilindros\", \"mantenimiento\": \"preventivo\"}'),
(53, '2026-06-08 23:24:12', '2026-06-08 23:24:12', NULL, 88, 'T-186', 62000, 1, 11, '{\"tipo\": \"banda de distribuci\\u00f3n\", \"sistema\": \"distribuci\\u00f3n del motor\", \"motor\": \"1.6L\"}'),
(54, '2026-06-08 23:24:14', '2026-06-08 23:24:14', NULL, 60, 'GWH-780', 95000, 1, 5, '{\"tipo\": \"bomba de agua\", \"sistema\": \"refrigeraci\\u00f3n del motor\"}');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos_categorias`
--

CREATE TABLE `productos_categorias` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `producto_id` int(11) NOT NULL,
  `categoria_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `productos_categorias`
--

INSERT INTO `productos_categorias` (`id`, `created_at`, `updated_at`, `deleted_at`, `producto_id`, `categoria_id`) VALUES
(17, '2026-06-08 18:03:04', '2026-06-08 18:03:04', NULL, 14, 24),
(19, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 17, 26),
(22, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 17, 29),
(23, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 17, 32),
(24, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 15, 24),
(25, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 15, 35),
(26, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 15, 32),
(27, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 22, 26),
(28, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 22, 29),
(29, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 22, 32),
(30, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 21, 36),
(31, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 25, 24),
(32, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 25, 35),
(33, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 25, 32),
(34, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 21, 37),
(35, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 23, 38),
(36, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 21, 40),
(37, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 21, 32),
(38, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 23, 41),
(39, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 23, 43),
(40, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 23, 32),
(41, '2026-06-08 18:10:02', '2026-06-08 18:10:02', NULL, 28, 24),
(42, '2026-06-08 18:10:02', '2026-06-08 18:10:02', NULL, 28, 35),
(43, '2026-06-08 18:10:02', '2026-06-08 18:10:02', NULL, 28, 32),
(44, '2026-06-08 18:13:01', '2026-06-08 18:13:01', NULL, 29, 24),
(45, '2026-06-08 18:13:01', '2026-06-08 18:13:01', NULL, 29, 35),
(46, '2026-06-08 18:13:01', '2026-06-08 18:13:01', NULL, 29, 32),
(47, '2026-06-08 18:16:00', '2026-06-08 18:16:00', NULL, 30, 24),
(48, '2026-06-08 18:16:00', '2026-06-08 18:16:00', NULL, 30, 35),
(49, '2026-06-08 18:16:00', '2026-06-08 18:16:00', NULL, 30, 32),
(50, '2026-06-08 19:24:19', '2026-06-08 19:24:19', NULL, 42, 24),
(51, '2026-06-08 19:24:19', '2026-06-08 19:24:19', NULL, 42, 44),
(52, '2026-06-08 19:24:19', '2026-06-08 19:24:19', NULL, 42, 32),
(53, '2026-06-08 19:26:56', '2026-06-08 19:26:56', NULL, 43, 24),
(54, '2026-06-08 19:26:56', '2026-06-08 19:26:56', NULL, 43, 44),
(55, '2026-06-08 19:27:02', '2026-06-08 19:27:02', NULL, 44, 26),
(56, '2026-06-08 19:27:02', '2026-06-08 19:27:02', NULL, 44, 29),
(57, '2026-06-08 19:27:09', '2026-06-08 19:27:09', NULL, 45, 45),
(58, '2026-06-08 19:27:09', '2026-06-08 19:27:09', NULL, 45, 46),
(59, '2026-06-08 19:27:15', '2026-06-08 19:27:15', NULL, 46, 38),
(60, '2026-06-08 19:27:15', '2026-06-08 19:27:15', NULL, 46, 43),
(61, '2026-06-08 19:27:21', '2026-06-08 19:27:21', NULL, 47, 47),
(62, '2026-06-08 19:27:21', '2026-06-08 19:27:21', NULL, 47, 40),
(63, '2026-06-08 19:27:28', '2026-06-08 19:27:28', NULL, 48, 36),
(64, '2026-06-08 19:27:28', '2026-06-08 19:27:28', NULL, 48, 48),
(65, '2026-06-08 23:24:05', '2026-06-08 23:24:05', NULL, 49, 24),
(66, '2026-06-08 23:24:05', '2026-06-08 23:24:05', NULL, 49, 44),
(67, '2026-06-08 23:24:05', '2026-06-08 23:24:05', NULL, 49, 32),
(68, '2026-06-08 23:24:07', '2026-06-08 23:24:07', NULL, 50, 26),
(69, '2026-06-08 23:24:07', '2026-06-08 23:24:07', NULL, 50, 29),
(70, '2026-06-08 23:24:07', '2026-06-08 23:24:07', NULL, 50, 32),
(71, '2026-06-08 23:24:09', '2026-06-08 23:24:09', NULL, 51, 45),
(72, '2026-06-08 23:24:09', '2026-06-08 23:24:09', NULL, 51, 46),
(73, '2026-06-08 23:24:09', '2026-06-08 23:24:09', NULL, 51, 32),
(74, '2026-06-08 23:24:10', '2026-06-08 23:24:10', NULL, 52, 38),
(75, '2026-06-08 23:24:10', '2026-06-08 23:24:10', NULL, 52, 49),
(76, '2026-06-08 23:24:10', '2026-06-08 23:24:10', NULL, 52, 43),
(77, '2026-06-08 23:24:10', '2026-06-08 23:24:10', NULL, 52, 32),
(78, '2026-06-08 23:24:12', '2026-06-08 23:24:12', NULL, 53, 50),
(79, '2026-06-08 23:24:12', '2026-06-08 23:24:12', NULL, 53, 40),
(80, '2026-06-08 23:24:12', '2026-06-08 23:24:12', NULL, 53, 32),
(81, '2026-06-08 23:24:14', '2026-06-08 23:24:14', NULL, 54, 36),
(82, '2026-06-08 23:24:14', '2026-06-08 23:24:14', NULL, 54, 48),
(83, '2026-06-08 23:24:14', '2026-06-08 23:24:14', NULL, 54, 40),
(84, '2026-06-08 23:24:14', '2026-06-08 23:24:14', NULL, 54, 32);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos_ciudades`
--

CREATE TABLE `productos_ciudades` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `producto_id` int(11) NOT NULL,
  `ciudad_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `productos_ciudades`
--

INSERT INTO `productos_ciudades` (`id`, `created_at`, `updated_at`, `deleted_at`, `producto_id`, `ciudad_id`) VALUES
(1, '2026-06-08 18:03:04', '2026-06-08 18:03:04', NULL, 14, 1),
(2, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 17, 2),
(3, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 15, 1),
(4, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 22, 2),
(5, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 25, 1),
(6, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 21, 3),
(7, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 23, 4),
(8, '2026-06-08 18:10:02', '2026-06-08 18:10:02', NULL, 28, 1),
(9, '2026-06-08 18:13:01', '2026-06-08 18:13:01', NULL, 29, 1),
(10, '2026-06-08 18:16:00', '2026-06-08 18:16:00', NULL, 30, 1),
(11, '2026-06-08 19:24:19', '2026-06-08 19:24:19', NULL, 42, 1),
(12, '2026-06-08 19:26:56', '2026-06-08 19:26:56', NULL, 43, 1),
(13, '2026-06-08 19:27:02', '2026-06-08 19:27:02', NULL, 44, 2),
(14, '2026-06-08 19:27:09', '2026-06-08 19:27:09', NULL, 45, 5),
(15, '2026-06-08 19:27:15', '2026-06-08 19:27:15', NULL, 46, 4),
(16, '2026-06-08 19:27:21', '2026-06-08 19:27:21', NULL, 47, 6),
(17, '2026-06-08 19:27:28', '2026-06-08 19:27:28', NULL, 48, 3),
(18, '2026-06-08 23:24:05', '2026-06-08 23:24:05', NULL, 49, 1),
(19, '2026-06-08 23:24:07', '2026-06-08 23:24:07', NULL, 50, 2),
(20, '2026-06-08 23:24:09', '2026-06-08 23:24:09', NULL, 51, 5),
(21, '2026-06-08 23:24:10', '2026-06-08 23:24:10', NULL, 52, 4),
(22, '2026-06-08 23:24:12', '2026-06-08 23:24:12', NULL, 53, 6),
(23, '2026-06-08 23:24:14', '2026-06-08 23:24:14', NULL, 54, 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos_vehiculos`
--

CREATE TABLE `productos_vehiculos` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `producto_id` int(11) NOT NULL,
  `vehiculo_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `productos_vehiculos`
--

INSERT INTO `productos_vehiculos` (`id`, `created_at`, `updated_at`, `deleted_at`, `producto_id`, `vehiculo_id`) VALUES
(23, '2026-06-08 18:03:04', '2026-06-08 18:03:04', NULL, 14, 26),
(24, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 15, 27),
(25, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 17, 28),
(30, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 17, 35),
(33, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 17, 39),
(35, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 15, 33),
(36, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 15, 41),
(37, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 21, 42),
(38, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 21, 43),
(39, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 23, 44),
(41, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 21, 47),
(42, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 22, 28),
(43, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 22, 35),
(44, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 22, 39),
(45, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 23, 48),
(46, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 23, 28),
(49, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 25, 27),
(50, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 25, 33),
(51, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 25, 41),
(52, '2026-06-08 18:08:52', '2026-06-08 18:08:52', NULL, 27, 27),
(53, '2026-06-08 18:10:02', '2026-06-08 18:10:02', NULL, 28, 27),
(54, '2026-06-08 18:10:02', '2026-06-08 18:10:02', NULL, 28, 33),
(55, '2026-06-08 18:10:02', '2026-06-08 18:10:02', NULL, 28, 41),
(56, '2026-06-08 18:13:01', '2026-06-08 18:13:01', NULL, 29, 27),
(57, '2026-06-08 18:13:01', '2026-06-08 18:13:01', NULL, 29, 33),
(58, '2026-06-08 18:13:01', '2026-06-08 18:13:01', NULL, 29, 41),
(59, '2026-06-08 18:16:00', '2026-06-08 18:16:00', NULL, 30, 27),
(60, '2026-06-08 18:16:00', '2026-06-08 18:16:00', NULL, 30, 33),
(61, '2026-06-08 18:16:00', '2026-06-08 18:16:00', NULL, 30, 41);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vehiculos`
--

CREATE TABLE `vehiculos` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `modelo` varchar(255) NOT NULL,
  `marca_id` int(11) NOT NULL,
  `anio` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `vehiculos`
--

INSERT INTO `vehiculos` (`id`, `created_at`, `updated_at`, `deleted_at`, `modelo`, `marca_id`, `anio`) VALUES
(26, '2026-06-08 18:03:04', '2026-06-08 18:03:04', NULL, 'versa', 43, 2020),
(27, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 'versa', 43, 0),
(28, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 'sentra', 43, 0),
(33, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 'aveo', 52, 0),
(35, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 'fluence', 53, 0),
(39, '2026-06-08 18:06:57', '2026-06-08 18:06:57', NULL, 'tiida', 43, 0),
(41, '2026-06-08 18:06:59', '2026-06-08 18:06:59', NULL, 'jetta', 57, 0),
(42, '2026-06-08 18:07:22', '2026-06-08 18:07:22', NULL, 'tsuru', 43, 0),
(43, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'sentra b13', 43, 0),
(44, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'corolla', 64, 0),
(47, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'platina', 43, 0),
(48, '2026-06-08 18:07:23', '2026-06-08 18:07:23', NULL, 'civic', 66, 0);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_categorias_categoria` (`categoria`);

--
-- Indices de la tabla `chats`
--
ALTER TABLE `chats`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chat_status_id` (`chat_status_id`),
  ADD KEY `ix_chats_chat_whatsapp_id` (`chat_whatsapp_id`),
  ADD KEY `ix_chats_lead_id_created_at` (`lead_id`,`created_at`);

--
-- Indices de la tabla `chat_statuses`
--
ALTER TABLE `chat_statuses`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `ciudades`
--
ALTER TABLE `ciudades`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_ciudades_ciudad` (`ciudad`),
  ADD KEY `estado_id` (`estado_id`);

--
-- Indices de la tabla `estados`
--
ALTER TABLE `estados`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_estados_estado` (`estado`);

--
-- Indices de la tabla `intenciones_de_compra_de_leads`
--
ALTER TABLE `intenciones_de_compra_de_leads`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `leads`
--
ALTER TABLE `leads`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ciudad_id` (`ciudad_id`),
  ADD KEY `intencion_de_compra_id` (`intencion_de_compra_id`),
  ADD KEY `ix_leads_chat_whatsapp_id` (`chat_whatsapp_id`);

--
-- Indices de la tabla `leads_productos`
--
ALTER TABLE `leads_productos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_leads_productos` (`lead_id`,`producto_id`),
  ADD KEY `producto_id` (`producto_id`);

--
-- Indices de la tabla `leads_vehiculos`
--
ALTER TABLE `leads_vehiculos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_leads_vehiculos` (`lead_id`,`vehiculo_id`),
  ADD KEY `vehiculo_id` (`vehiculo_id`);

--
-- Indices de la tabla `marcas`
--
ALTER TABLE `marcas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_marcas_marca` (`marca`);

--
-- Indices de la tabla `monedas`
--
ALTER TABLE `monedas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_monedas_abreviacion` (`abreviacion`);

--
-- Indices de la tabla `pre_ordenes`
--
ALTER TABLE `pre_ordenes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `lead_id` (`lead_id`);

--
-- Indices de la tabla `pre_ordenes_productos`
--
ALTER TABLE `pre_ordenes_productos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_pre_ordenes_productos` (`pre_orden_id`,`producto_id`),
  ADD KEY `producto_id` (`producto_id`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `marca_id` (`marca_id`),
  ADD KEY `moneda_id` (`moneda_id`);

--
-- Indices de la tabla `productos_categorias`
--
ALTER TABLE `productos_categorias`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_productos_categorias` (`producto_id`,`categoria_id`),
  ADD KEY `categoria_id` (`categoria_id`);

--
-- Indices de la tabla `productos_ciudades`
--
ALTER TABLE `productos_ciudades`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_productos_ciudades` (`producto_id`,`ciudad_id`),
  ADD KEY `ciudad_id` (`ciudad_id`);

--
-- Indices de la tabla `productos_vehiculos`
--
ALTER TABLE `productos_vehiculos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_productos_vehiculos` (`producto_id`,`vehiculo_id`),
  ADD KEY `vehiculo_id` (`vehiculo_id`);

--
-- Indices de la tabla `vehiculos`
--
ALTER TABLE `vehiculos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_vehiculos_modelo_marca_anio` (`modelo`,`marca_id`,`anio`),
  ADD KEY `marca_id` (`marca_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT de la tabla `chats`
--
ALTER TABLE `chats`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `chat_statuses`
--
ALTER TABLE `chat_statuses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `ciudades`
--
ALTER TABLE `ciudades`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `estados`
--
ALTER TABLE `estados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT de la tabla `intenciones_de_compra_de_leads`
--
ALTER TABLE `intenciones_de_compra_de_leads`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `leads`
--
ALTER TABLE `leads`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `leads_productos`
--
ALTER TABLE `leads_productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `leads_vehiculos`
--
ALTER TABLE `leads_vehiculos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `marcas`
--
ALTER TABLE `marcas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=89;

--
-- AUTO_INCREMENT de la tabla `monedas`
--
ALTER TABLE `monedas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `pre_ordenes`
--
ALTER TABLE `pre_ordenes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `pre_ordenes_productos`
--
ALTER TABLE `pre_ordenes_productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=55;

--
-- AUTO_INCREMENT de la tabla `productos_categorias`
--
ALTER TABLE `productos_categorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=85;

--
-- AUTO_INCREMENT de la tabla `productos_ciudades`
--
ALTER TABLE `productos_ciudades`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT de la tabla `productos_vehiculos`
--
ALTER TABLE `productos_vehiculos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

--
-- AUTO_INCREMENT de la tabla `vehiculos`
--
ALTER TABLE `vehiculos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `chats`
--
ALTER TABLE `chats`
  ADD CONSTRAINT `chats_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`),
  ADD CONSTRAINT `chats_ibfk_2` FOREIGN KEY (`chat_status_id`) REFERENCES `chat_statuses` (`id`);

--
-- Filtros para la tabla `ciudades`
--
ALTER TABLE `ciudades`
  ADD CONSTRAINT `ciudades_ibfk_1` FOREIGN KEY (`estado_id`) REFERENCES `estados` (`id`);

--
-- Filtros para la tabla `leads`
--
ALTER TABLE `leads`
  ADD CONSTRAINT `leads_ibfk_1` FOREIGN KEY (`ciudad_id`) REFERENCES `ciudades` (`id`),
  ADD CONSTRAINT `leads_ibfk_2` FOREIGN KEY (`intencion_de_compra_id`) REFERENCES `intenciones_de_compra_de_leads` (`id`);

--
-- Filtros para la tabla `leads_productos`
--
ALTER TABLE `leads_productos`
  ADD CONSTRAINT `leads_productos_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`),
  ADD CONSTRAINT `leads_productos_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`);

--
-- Filtros para la tabla `leads_vehiculos`
--
ALTER TABLE `leads_vehiculos`
  ADD CONSTRAINT `leads_vehiculos_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`),
  ADD CONSTRAINT `leads_vehiculos_ibfk_2` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`id`);

--
-- Filtros para la tabla `pre_ordenes`
--
ALTER TABLE `pre_ordenes`
  ADD CONSTRAINT `pre_ordenes_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`);

--
-- Filtros para la tabla `pre_ordenes_productos`
--
ALTER TABLE `pre_ordenes_productos`
  ADD CONSTRAINT `pre_ordenes_productos_ibfk_1` FOREIGN KEY (`pre_orden_id`) REFERENCES `pre_ordenes` (`id`),
  ADD CONSTRAINT `pre_ordenes_productos_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`);

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`marca_id`) REFERENCES `marcas` (`id`),
  ADD CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`moneda_id`) REFERENCES `monedas` (`id`);

--
-- Filtros para la tabla `productos_categorias`
--
ALTER TABLE `productos_categorias`
  ADD CONSTRAINT `productos_categorias_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  ADD CONSTRAINT `productos_categorias_ibfk_2` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`);

--
-- Filtros para la tabla `productos_ciudades`
--
ALTER TABLE `productos_ciudades`
  ADD CONSTRAINT `productos_ciudades_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  ADD CONSTRAINT `productos_ciudades_ibfk_2` FOREIGN KEY (`ciudad_id`) REFERENCES `ciudades` (`id`);

--
-- Filtros para la tabla `productos_vehiculos`
--
ALTER TABLE `productos_vehiculos`
  ADD CONSTRAINT `productos_vehiculos_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  ADD CONSTRAINT `productos_vehiculos_ibfk_2` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`id`);

--
-- Filtros para la tabla `vehiculos`
--
ALTER TABLE `vehiculos`
  ADD CONSTRAINT `vehiculos_ibfk_1` FOREIGN KEY (`marca_id`) REFERENCES `marcas` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
