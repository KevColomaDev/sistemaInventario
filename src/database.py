import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path='inventario.db'):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.initialize_database()
    
    def connect(self):
        """Establece la conexión con la base de datos"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        # Asegurar que las claves foráneas estén activas
        try:
            self.cursor.execute('PRAGMA foreign_keys = ON;')
        except Exception:
            pass
    
    def close(self):
        """Cierra la conexión con la base de datos"""
        if self.connection:
            self.connection.close()
    
    def initialize_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        self.connect()
        
        # Crear tabla de categorías
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Crear tabla de productos
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 0,
            categoria_id INTEGER,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
        ''')
        
        # Crear tabla de movimientos de inventario
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,  -- 'entrada' o 'salida'
            cantidad INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notas TEXT,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
        ''')

        # Crear tabla de ventas
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_venta TEXT NOT NULL UNIQUE,
            fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL DEFAULT 0,
            estado TEXT NOT NULL DEFAULT 'completada',
            notas TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Crear tabla de ítems de venta
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS venta_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
        ''')

        # Índices útiles
        self.cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_venta);
        ''')
        
        self.connection.commit()
        self.close()
    
    def execute_query(self, query, params=()):
        """Ejecuta una consulta y devuelve los resultados"""
        self.connect()
        try:
            self.cursor.execute(query, params)
            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error en la consulta: {e}")
            return None
        finally:
            self.close()

# Instancia global de la base de datos
db = Database()
