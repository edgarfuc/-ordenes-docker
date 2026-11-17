
-- ==========================================
-- BASE DE DATOS: OrdenesDB
-- PROYECTO: Ordenes de venta
-- ==========================================

CREATE DATABASE OrdenesDB;
GO

USE OrdenesDB;
GO

-- Tabla principal de ordenes
CREATE TABLE ordenes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL DEFAULT GETDATE(),
    estado VARCHAR(30) NOT NULL DEFAULT 'Pendiente',
    total DECIMAL(12,2) NOT NULL DEFAULT 0
);
GO

-- Tabla de detalles de cada orden
CREATE TABLE orden_detalle (
    id INT IDENTITY(1,1) PRIMARY KEY,
    orden_id INT NOT NULL,
    producto VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(12,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,

    CONSTRAINT FK_orden_detalle_ordenes
    FOREIGN KEY (orden_id)
    REFERENCES ordenes(id)
);
GO


-- ==========================================
-- INSERTAR 5 ORDENES DE PRUEBA
-- ==========================================

INSERT INTO ordenes (cliente, fecha, estado, total)
VALUES
('Juan Perez', '2026-11-15', 'Pendiente', 0),
('Maria Lopez', '2026-11-15', 'Pagada', 0),
('Carlos Rivera', '2026-11-16', 'Pendiente', 0),
('Ana Martinez', '2026-11-16', 'Pagada', 0),
('Pedro Sanchez', '2026-11-16', 'Anulada', 0);
GO

-- ==========================================
-- INSERTAR DETALLES DE LAS ORDENES
-- Cada orden tiene 2 productos
-- ==========================================

INSERT INTO orden_detalle
(orden_id, producto, cantidad, precio_unitario, subtotal)
VALUES
-- Orden 1
(1, 'Teclado', 2, 150.00, 300.00),
(1, 'Mouse', 1, 50.00, 50.00),

-- Orden 2
(2, 'Monitor', 3, 25.00, 75.00),
(2, 'Cable HDMI', 2, 40.00, 80.00),

-- Orden 3
(3, 'Laptop', 1, 500.00, 500.00),
(3, 'Memoria USB', 2, 75.00, 150.00),

-- Orden 4
(4, 'Audifonos', 4, 12.50, 50.00),
(4, 'Impresora', 1, 200.00, 200.00),

-- Orden 5
(5, 'Disco SSD', 2, 80.00, 160.00),
(5, 'Mousepad', 3, 15.00, 45.00);
GO

-- ==========================================
-- ACTUALIZAR TOTALES DE LAS ORDENES
-- ==========================================

UPDATE ordenes
SET total = (
    SELECT COALESCE(SUM(subtotal), 0)
    FROM orden_detalle
    WHERE orden_detalle.orden_id = ordenes.id
);
GO

