from datetime import datetime
from src.database import db

class Producto:
    def __init__(self, codigo, nombre, precio, cantidad=0, descripcion="", categoria_id=None, id=None):
        self.id = id
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = float(precio) if precio is not None else 0.0
        self.cantidad = int(cantidad) if cantidad is not None else 0
        self.categoria_id = categoria_id
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def guardar(self):
        """Guarda el producto en la base de datos"""
        query = """
        INSERT INTO productos (codigo, nombre, descripcion, precio, cantidad, categoria_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.id = db.execute_query(
            query,
            (self.codigo, self.nombre, self.descripcion, 
             self.precio, self.cantidad, self.categoria_id)
        )
        return self.id
    
    def actualizar(self):
        """Actualiza el producto en la base de datos"""
        if not self.id:
            return None
            
        query = """
        UPDATE productos
        SET codigo = ?, nombre = ?, descripcion = ?, 
            precio = ?, cantidad = ?, categoria_id = ?
        WHERE id = ?
        """
        db.execute_query(
            query,
            (self.codigo, self.nombre, self.descripcion, 
             self.precio, self.cantidad, self.categoria_id, self.id)
        )
        return self.id
    
    def actualizar_cantidad(self, nueva_cantidad, notas=""):
        """Actualiza la cantidad disponible y registra el movimiento"""
        if not self.id:
            return False
            
        diferencia = nueva_cantidad - self.cantidad
        tipo_movimiento = "entrada" if diferencia > 0 else "salida"
        
        # Actualizar la cantidad
        query = "UPDATE productos SET cantidad = ? WHERE id = ?"
        db.execute_query(query, (nueva_cantidad, self.id))
        
        # Registrar el movimiento
        self.registrar_movimiento(tipo_movimiento, abs(diferencia), notas)
        
        self.cantidad = nueva_cantidad
        return True
    
    def registrar_movimiento(self, tipo, cantidad, notas=""):
        """Registra un movimiento de inventario"""
        if not self.id:
            return None
            
        query = """
        INSERT INTO movimientos (producto_id, tipo, cantidad, notas)
        VALUES (?, ?, ?, ?)
        """
        return db.execute_query(query, (self.id, tipo, cantidad, notas))
    
    def eliminar(self):
        """Elimina el producto de la base de datos"""
        if not self.id:
            return False
            
        # Primero eliminamos los movimientos asociados
        db.execute_query("DELETE FROM movimientos WHERE producto_id = ?", (self.id,))
        
        # Luego eliminamos el producto
        db.execute_query("DELETE FROM productos WHERE id = ?", (self.id,))
        return True
    
    @classmethod
    def obtener_todos(cls, categoria_id=None):
        """Obtiene todos los productos, opcionalmente filtrados por categoría"""
        if categoria_id is not None:
            query = """
            SELECT p.*, c.nombre as categoria_nombre 
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.categoria_id = ?
            ORDER BY p.nombre
            """
            resultados = db.execute_query(query, (categoria_id,))
        else:
            query = """
            SELECT p.*, c.nombre as categoria_nombre 
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.nombre
            """
            resultados = db.execute_query(query)
            
        return [cls.crear_desde_fila(dict(row)) for row in resultados]
    
    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene un producto por su ID"""
        query = """
        SELECT p.*, c.nombre as categoria_nombre 
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.id = ?
        """
        resultado = db.execute_query(query, (id,))
        if resultado:
            return cls.crear_desde_fila(dict(resultado[0]))
        return None
    
    @classmethod
    def buscar(cls, termino, categoria_id=None):
        """Busca productos por nombre o código, opcionalmente filtrados por categoría"""
        termino_busqueda = f"%{termino}%"
        
        if categoria_id is not None:
            query = """
            SELECT p.*, c.nombre as categoria_nombre 
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE (p.nombre LIKE ? OR p.codigo LIKE ?) AND p.categoria_id = ?
            ORDER BY p.nombre
            """
            resultados = db.execute_query(query, (termino_busqueda, termino_busqueda, categoria_id))
        else:
            query = """
            SELECT p.*, c.nombre as categoria_nombre 
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.nombre LIKE ? OR p.codigo LIKE ?
            ORDER BY p.nombre
            """
            resultados = db.execute_query(query, (termino_busqueda, termino_busqueda))
            
        return [cls.crear_desde_fila(dict(row)) for row in resultados]
    
    @classmethod
    def crear_desde_fila(cls, fila):
        """Crea una instancia de Producto a partir de una fila de la base de datos"""
        producto = cls(
            id=fila.get('id'),
            codigo=fila.get('codigo', ''),
            nombre=fila.get('nombre', ''),
            descripcion=fila.get('descripcion', ''),
            precio=float(fila.get('precio', 0)),
            cantidad=int(fila.get('cantidad', 0)),
            categoria_id=fila.get('categoria_id')
        )
        producto.categoria_nombre = fila.get('categoria_nombre')
        return producto
    
    def to_dict(self):
        """Convierte el objeto a un diccionario"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'cantidad': self.cantidad,
            'categoria_id': self.categoria_id,
            'categoria_nombre': getattr(self, 'categoria_nombre', ''),
            'valor_total': self.precio * self.cantidad,
            'fecha_creacion': self.fecha_creacion
        }
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo}) - {self.cantidad} disponibles"
