-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 13-07-2025 a las 21:57:02
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `libreria`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carritos`
--

CREATE TABLE `carritos` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carrito_detalles`
--

CREATE TABLE `carrito_detalles` (
  `id` int(11) NOT NULL,
  `carrito_id` int(11) NOT NULL,
  `libro_id` int(11) NOT NULL,
  `cantidad` int(11) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id`, `nombre`) VALUES
(1, 'Fantasía'),
(2, 'Ciencia Ficción'),
(3, 'Autobibliografia'),
(4, 'Drama'),
(5, 'Distopia'),
(6, 'mambo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `libros`
--

CREATE TABLE `libros` (
  `id` int(11) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `autor` varchar(255) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL DEFAULT 0,
  `imagen_url` varchar(2048) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `editorial` varchar(255) DEFAULT NULL,
  `fecha_publicacion` date DEFAULT NULL,
  `en_remate` tinyint(1) DEFAULT 0,
  `categoria_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `libros`
--

INSERT INTO `libros` (`id`, `titulo`, `autor`, `precio`, `stock`, `imagen_url`, `descripcion`, `editorial`, `fecha_publicacion`, `en_remate`, `categoria_id`) VALUES
(1, 'El Hobbit', 'J.R.R. Tolkien', 22.50, 10, 'https://images.cdn1.buscalibre.com/fit-in/360x360/c6/cc/c6cc0d544da7e4c54e0ae464d7ffcbcd.jpg', 'Una aventura épica que precede a El Señor de los Anillos.', 'Minotauro', '1937-09-21', 0, 1),
(2, 'Dune', 'Frank Herbert', 28.99, 15, 'https://cdn.swiatksiazki.pl/media/catalog/product/9/1/9199906615891.jpg?width=650&height=650&store=default&image-type=small_image', 'La saga de ciencia ficción definitiva sobre un planeta desértico.', 'Debolsillo', '1965-08-01', 1, 2),
(3, 'Mi lucha', 'Elmer Calizaya', 90.00, 3, 'https://preview.redd.it/aez34xbkf1p01.jpg?width=640&crop=smart&auto=webp&s=3471d04e177dff749e664667a8327274cd3c5b99', 'Libro Auto bibliografía sobre diplomacia', '.', '2025-07-13', 0, 3),
(4, 'mambo', 'mambo', 999.99, 1, 'https://preview.redd.it/nty78xetq2fe1.jpeg?width=360&format=pjpg&auto=webp&s=79d4cd6ebb408540f504a7f42d143fcad69bc108', 'mambo', 'mambo', '2025-07-13', 0, 6);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `total` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedido_detalles`
--

CREATE TABLE `pedido_detalles` (
  `id` int(11) NOT NULL,
  `pedido_id` int(11) NOT NULL,
  `libro_id` int(11) NOT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `precio_unitario` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id`, `nombre`) VALUES
(1, 'admin'),
(2, 'user');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `contraseña` varchar(255) NOT NULL,
  `rol_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre`, `correo`, `contraseña`, `rol_id`) VALUES
(1, 'admin', 'castillo.erixon@gmail.com', 'scrypt:32768:8:1$B1R6wxlb03TITv97$a2160c065ff6171f41c2bd1476cd6045a201d319d081a7474e5737a6199d04a48a80bf9170e2b2eaa24a4f57487ffc4331bc82a5f1515e319e5b5d3e62eea87c', 1),
(2, 'carlitos', 'correomentira@gmail.com', 'scrypt:32768:8:1$kiZVXilkaQAk5TKd$c0b48833e0279e2f9175a63a6f2fc64c823a289cac6d0446e04be3f5f8ab7312fa8f8409e8e23918ce7681ce71c6794386215712c7556368e3d92efbdd243958', 2);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `carritos`
--
ALTER TABLE `carritos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `carrito_detalles`
--
ALTER TABLE `carrito_detalles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `carrito_id` (`carrito_id`),
  ADD KEY `libro_id` (`libro_id`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `libros`
--
ALTER TABLE `libros`
  ADD PRIMARY KEY (`id`),
  ADD KEY `categoria_id` (`categoria_id`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `pedido_detalles`
--
ALTER TABLE `pedido_detalles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pedido_id` (`pedido_id`),
  ADD KEY `libro_id` (`libro_id`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `correo` (`correo`),
  ADD KEY `rol_id` (`rol_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `carritos`
--
ALTER TABLE `carritos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `carrito_detalles`
--
ALTER TABLE `carrito_detalles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `libros`
--
ALTER TABLE `libros`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pedido_detalles`
--
ALTER TABLE `pedido_detalles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `carritos`
--
ALTER TABLE `carritos`
  ADD CONSTRAINT `carritos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `carrito_detalles`
--
ALTER TABLE `carrito_detalles`
  ADD CONSTRAINT `carrito_detalles_ibfk_1` FOREIGN KEY (`carrito_id`) REFERENCES `carritos` (`id`),
  ADD CONSTRAINT `carrito_detalles_ibfk_2` FOREIGN KEY (`libro_id`) REFERENCES `libros` (`id`);

--
-- Filtros para la tabla `libros`
--
ALTER TABLE `libros`
  ADD CONSTRAINT `libros_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`);

--
-- Filtros para la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `pedido_detalles`
--
ALTER TABLE `pedido_detalles`
  ADD CONSTRAINT `pedido_detalles_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`),
  ADD CONSTRAINT `pedido_detalles_ibfk_2` FOREIGN KEY (`libro_id`) REFERENCES `libros` (`id`);

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
