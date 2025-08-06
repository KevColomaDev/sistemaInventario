from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
import random
import string

from src.database import db

@dataclass
class VentaItem:
    id: Optional[int] = None
    venta_id: Optional[int] = None
    producto_id: int = 0
    cantidad: int = 1
    precio_unitario: float = 0.0
    subtotal: float = 0.0
    created_at: Optional[datetime] = None
    
    def calcular_subtotal(self):
        self.subtotal = round(self.cantidad * self.precio_unitario, 2)
        return self.subtotal

@dataclass
class Venta:
    id: Optional[int] = None
    codigo_venta: str = ""
    fecha_venta: datetime = field(default_factory=datetime.now)
    total: float = 0.0
    estado: str = "completada"
    notas: str = ""
    items: List[VentaItem] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def generar_codigo_venta(cls):
        """Genera un código único para la venta"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"V-{timestamp}-{random_str}"
    
    def agregar_item(self, producto_id: int, cantidad: int, precio_unitario: float):
        """Agrega un ítem a la venta"""
        item = VentaItem(
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        item.calcular_subtotal()
        self.items.append(item)
        self.calcular_total()
    
    def eliminar_item(self, item_index: int):
        """Elimina un ítem de la venta por su índice"""
        if 0 <= item_index < len(self.items):
            del self.items[item_index]
            self.calcular_total()
    
    def calcular_total(self):
        """Calcula el total de la venta sumando los subtotales de los ítems"""
        self.total = round(sum(item.subtotal for item in self.items), 2)
        return self.total
    
    def guardar(self):
        """Guarda la venta en la base de datos"""
        if not self.codigo_venta:
            self.codigo_venta = self.generar_codigo_venta()
        
        self.calcular_total()
        now = datetime.now()
        
        if self.id is None:
            # Insertar nueva venta
            query = """
            INSERT INTO ventas (codigo_venta, fecha_venta, total, estado, notas, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            venta_id = db.execute_query(
                query,
                (
                    self.codigo_venta,
                    self.fecha_venta,
                    self.total,
                    self.estado,
                    self.notas,
                    now,
                    now
                )
            )
            self.id = venta_id
            
            # Insertar ítems
            for item in self.items:
                item_query = """
                INSERT INTO venta_items (venta_id, producto_id, cantidad, precio_unitario, subtotal, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                db.execute_query(
                    item_query,
                    (
                        self.id,
                        item.producto_id,
                        item.cantidad,
                        item.precio_unitario,
                        item.subtotal,
                        now
                    )
                )
                
                # Actualizar el stock del producto
                db.execute_query(
                    "UPDATE productos SET cantidad = cantidad - ? WHERE id = ?",
                    (item.cantidad, item.producto_id)
                )
        else:
            # Actualizar venta existente
            query = """
            UPDATE ventas 
            SET total = ?, estado = ?, notas = ?, updated_at = ?
            WHERE id = ?
            """
            db.execute_query(
                query,
                (self.total, self.estado, self.notas, now, self.id)
            )
            
            # Eliminar ítems antiguos
            db.execute_query("DELETE FROM venta_items WHERE venta_id = ?", (self.id,))
            
            # Insertar ítems actualizados
            for item in self.items:
                item_query = """
                INSERT INTO venta_items (venta_id, producto_id, cantidad, precio_unitario, subtotal, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                db.execute_query(
                    item_query,
                    (
                        self.id,
                        item.producto_id,
                        item.cantidad,
                        item.precio_unitario,
                        item.subtotal,
                        now
                    )
                )
        
        return self.id
    
    @classmethod
    def obtener_por_id(cls, venta_id: int):
        """Obtiene una venta por su ID"""
        venta_data = db.execute_query(
            "SELECT * FROM ventas WHERE id = ?",
            (venta_id,),
            fetch_one=True
        )
        
        if not venta_data:
            return None
            
        # Obtener ítems de la venta
        items_data = db.execute_query(
            "SELECT * FROM venta_items WHERE venta_id = ?",
            (venta_id,)
        )
        
        # Crear objeto Venta
        venta = cls(
            id=venta_data['id'],
            codigo_venta=venta_data['codigo_venta'],
            fecha_venta=venta_data['fecha_venta'],
            total=venta_data['total'],
            estado=venta_data['estado'],
            notas=venta_data['notas'],
            created_at=venta_data['created_at'],
            updated_at=venta_data['updated_at']
        )
        
        # Agregar ítems
        for item_data in items_data:
            item = VentaItem(
                id=item_data['id'],
                venta_id=item_data['venta_id'],
                producto_id=item_data['producto_id'],
                cantidad=item_data['cantidad'],
                precio_unitario=item_data['precio_unitario'],
                subtotal=item_data['subtotal'],
                created_at=item_data['created_at']
            )
            venta.items.append(item)
        
        return venta
    
    @classmethod
    def obtener_todas(cls, fecha_inicio=None, fecha_fin=None, estado=None):
        """Obtiene todas las ventas, opcionalmente filtradas por fecha y estado"""
        query = "SELECT * FROM ventas WHERE 1=1"
        params = []
        
        if fecha_inicio:
            query += " AND DATE(fecha_venta) >= ?"
            params.append(fecha_inicio.strftime("%Y-%m-%d"))
            
        if fecha_fin:
            query += " AND DATE(fecha_venta) <= ?"
            params.append(fecha_fin.strftime("%Y-%m-%d"))
            
        if estado:
            query += " AND estado = ?"
            params.append(estado)
            
        query += " ORDER BY fecha_venta DESC"
        
        ventas_data = db.execute_query(query, tuple(params))
        ventas = []
        
        for venta_data in ventas_data:
            venta = cls.obtener_por_id(venta_data['id'])
            if venta:
                ventas.append(venta)
                
        return ventas
    
    @classmethod
    def cancelar_venta(cls, venta_id: int, motivo: str = ""):
        """Cancela una venta y devuelve el stock a inventario"""
        # Obtener la venta
        venta = cls.obtener_por_id(venta_id)
        if not venta:
            return False
            
        # Devolver el stock de cada ítem
        for item in venta.items:
            db.execute_query(
                "UPDATE productos SET cantidad = cantidad + ? WHERE id = ?",
                (item.cantidad, item.producto_id)
            )
        
        # Actualizar estado de la venta
        notas = f"VENTA CANCELADA. {venta.notas or ''} {motro}".strip()
        db.execute_query(
            "UPDATE ventas SET estado = 'cancelada', notas = ?, updated_at = ? WHERE id = ?",
            (notas, datetime.now(), venta_id)
        )
        
        return True
