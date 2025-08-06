from datetime import datetime
from src.database import db

class Categoria:
    def __init__(self, nombre, descripcion="", id=None, fecha_creacion=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def guardar(self):
        """Guarda la categoría en la base de datos"""
        query = """
        INSERT INTO categorias (nombre, descripcion)
        VALUES (?, ?)
        """
        self.id = db.execute_query(query, (self.nombre, self.descripcion))
        return self.id
    
    def actualizar(self):
        """Actualiza la categoría en la base de datos"""
        if not self.id:
            return None
            
        query = """
        UPDATE categorias
        SET nombre = ?, descripcion = ?
        WHERE id = ?
        """
        db.execute_query(query, (self.nombre, self.descripcion, self.id))
        return self.id
    
    def eliminar(self):
        """Elimina la categoría de la base de datos"""
        if not self.id:
            return False
            
        # Verificar si hay productos asociados a esta categoría
        query = "SELECT COUNT(*) as count FROM productos WHERE categoria_id = ?"
        resultado = db.execute_query(query, (self.id,))
        
        if resultado and resultado[0]['count'] > 0:
            raise ValueError("No se puede eliminar la categoría porque tiene productos asociados")
        
        query = "DELETE FROM categorias WHERE id = ?"
        db.execute_query(query, (self.id,))
        return True
    
    @classmethod
    def obtener_todas(cls):
        """Obtiene todas las categorías de la base de datos"""
        query = "SELECT * FROM categorias ORDER BY nombre"
        return [cls(**dict(row)) for row in db.execute_query(query)]
    
    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una categoría por su ID"""
        query = "SELECT * FROM categorias WHERE id = ?"
        resultado = db.execute_query(query, (id,))
        if resultado:
            return cls(**dict(resultado[0]))
        return None
    
    @classmethod
    def buscar_por_nombre(cls, nombre):
        """Busca categorías por nombre (búsqueda parcial)"""
        query = "SELECT * FROM categorias WHERE nombre LIKE ? ORDER BY nombre"
        return [cls(**dict(row)) for row in db.execute_query(query, (f"%{nombre}%",))]
    
    def to_dict(self):
        """Convierte el objeto a un diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion
        }
    
    def __str__(self):
        return self.nombre
