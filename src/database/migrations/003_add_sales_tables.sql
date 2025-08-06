-- Tabla para ventas
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_venta TEXT NOT NULL UNIQUE,
    fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) NOT NULL,
    estado TEXT NOT NULL DEFAULT 'completada' CHECK(estado IN ('completada', 'cancelada')),
    notas TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para ítems de venta
CREATE TABLE IF NOT EXISTS venta_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Índices para mejorar el rendimiento de las consultas
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_venta);
CREATE INDEX IF NOT EXISTS idx_venta_items_venta_id ON venta_items(venta_id);
CREATE INDEX IF NOT EXISTS idx_venta_items_producto_id ON venta_items(producto_id);
