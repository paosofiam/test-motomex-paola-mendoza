-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1:3306
-- Tiempo de generación: 03-06-2026 a las 05:54:00
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
('0018_pre_ordenes_productos');

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
(1, '2026-06-02 00:51:36', '2026-06-02 00:51:36', '2026-06-02 01:12:34', 1, '6771465876', 1, 'Conversacion iniciada desde Telegram'),
(2, '2026-06-02 01:27:11', '2026-06-02 01:27:11', '2026-06-02 02:09:52', 2, '6771465876', 1, 'Conversacion iniciada desde Telegram'),
(3, '2026-06-02 03:28:22', '2026-06-02 03:28:22', '2026-06-02 16:53:48', 2, '6771465876', 1, 'Conversacion iniciada desde Telegram'),
(4, '2026-06-02 03:28:22', '2026-06-02 03:28:22', '2026-06-02 21:04:21', 3, '6771465876', 1, 'Conversacion iniciada desde Telegram'),
(5, '2026-06-02 21:05:57', '2026-06-02 21:07:53', NULL, 6, '716082462', 1, 'Conversación retomada'),
(6, '2026-06-02 21:25:47', '2026-06-02 21:25:47', NULL, 7, '6771465876', 1, 'Conversacion iniciada desde Telegram'),
(7, '2026-06-02 21:25:47', '2026-06-02 21:25:47', NULL, 9, '6771465876', 1, 'Conversacion iniciada desde Telegram'),
(8, '2026-06-02 21:25:48', '2026-06-02 21:25:48', '2026-06-02 21:27:10', 8, '6771465876', 1, 'Conversacion iniciada desde Telegram'),
(9, '2026-06-02 21:25:48', '2026-06-02 21:25:48', NULL, 10, '6771465876', 1, 'Conversacion iniciada desde Telegram');

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

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estados`
--

CREATE TABLE `estados` (
  `id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `estado` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
(1, '2026-06-02 00:49:34', '2026-06-02 00:49:34', '2026-06-01 19:14:18', '6771465876', 'Paola Sofía', '+520000000000', NULL, NULL, NULL, 1),
(2, '2026-06-02 01:17:06', '2026-06-02 01:17:06', NULL, '6771465876', 'Paola Sofía', '+520000000000', NULL, NULL, NULL, 1),
(3, '2026-06-02 01:26:44', '2026-06-02 01:26:44', NULL, '6771465876', 'Paola Sofía', '+520000000000', NULL, NULL, NULL, 1),
(4, '2026-06-02 03:28:15', '2026-06-02 03:28:15', NULL, '6771465876', 'Paola Sofía', '+520000000000', NULL, NULL, NULL, 1),
(5, '2026-06-02 03:28:15', '2026-06-02 03:28:15', NULL, '6771465876', 'Paola Sofía', '+520000000000', NULL, NULL, NULL, 1),
(6, '2026-06-02 21:05:56', '2026-06-02 21:05:56', NULL, '716082462', 'Andree', '+520000000000', NULL, NULL, NULL, 1),
(7, '2026-06-02 21:25:46', '2026-06-02 21:25:46', NULL, '6771465876', 'Paola Sofía', '+520000000000', NULL, NULL, NULL, 1),
(8, '2026-06-02 21:25:47', '2026-06-02 21:25:47', NULL, '6771465876', 'Paola Sofía', '+520000000000', NULL, NULL, NULL, 1),
(9, '2026-06-02 21:25:47', '2026-06-02 21:25:47', NULL, '6771465876', 'Paola Sofía', '+520000000000', NULL, NULL, NULL, 1),
(10, '2026-06-02 21:25:47', '2026-06-02 21:25:47', NULL, '6771465876', 'Paola Sofía', '+520000000000', NULL, NULL, NULL, 1);

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `estados`
--
ALTER TABLE `estados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `intenciones_de_compra_de_leads`
--
ALTER TABLE `intenciones_de_compra_de_leads`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `leads`
--
ALTER TABLE `leads`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `monedas`
--
ALTER TABLE `monedas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `pre_ordenes`
--
ALTER TABLE `pre_ordenes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pre_ordenes_productos`
--
ALTER TABLE `pre_ordenes_productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos_categorias`
--
ALTER TABLE `productos_categorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos_ciudades`
--
ALTER TABLE `productos_ciudades`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos_vehiculos`
--
ALTER TABLE `productos_vehiculos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `vehiculos`
--
ALTER TABLE `vehiculos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

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
