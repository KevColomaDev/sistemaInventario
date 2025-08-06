import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QComboBox, QDateEdit, QTabWidget, QVBoxLayout,
    QFormLayout, QMessageBox, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QIcon, QFont

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.venta import Venta
from models.producto import Producto
from models.categoria import Categoria


class ReportesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setup_ui()
            self.cargar_datos_iniciales()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al inicializar reportes",
                f"Error al inicializar la vista de reportes: {str(e)}"
            )
    
    def setup_ui(self):
        """Configura la interfaz de usuario de la vista de reportes"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Pestañas para diferentes tipos de reportes
        self.tabs = QTabWidget()
        
        # Pestaña de ventas
        self.tab_ventas = QWidget()
        self.setup_ventas_tab()
        
        # Pestaña de inventario
        self.tab_inventario = QWidget()
        self.setup_inventario_tab()
        
        # Pestaña de categorías
        self.tab_categorias = QWidget()
        self.setup_categorias_tab()
        
        # Agregar pestañas
        self.tabs.addTab(self.tab_ventas, "Ventas")
        self.tabs.addTab(self.tab_inventario, "Inventario")
        self.tabs.addTab(self.tab_categorias, "Categorías")
        
        layout.addWidget(self.tabs)
        
        # Botón de exportar
        btn_exportar = QPushButton("Exportar a Excel")
        btn_exportar.setIcon(QIcon(":/icons/download.png"))
        btn_exportar.clicked.connect(self.exportar_a_excel)
        
        layout.addWidget(btn_exportar, alignment=Qt.AlignmentFlag.AlignRight)
    
    def setup_ventas_tab(self):
        """Configura la pestaña de reportes de ventas"""
        layout = QVBoxLayout(self.tab_ventas)
        
        # Filtros
        filtros_layout = QHBoxLayout()
        
        # Fecha desde
        form_fecha_desde = QFormLayout()
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        form_fecha_desde.addRow("Desde:", self.fecha_desde)
        
        # Fecha hasta
        form_fecha_hasta = QFormLayout()
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate())
        form_fecha_hasta.addRow("Hasta:", self.fecha_hasta)
        
        # Botón de filtrar
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.filtrar_ventas)
        
        filtros_layout.addLayout(form_fecha_desde)
        filtros_layout.addLayout(form_fecha_hasta)
        filtros_layout.addWidget(btn_filtrar)
        filtros_layout.addStretch()
        
        layout.addLayout(filtros_layout)
        
        # Tabla de ventas
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(5)
        self.tabla_ventas.setHorizontalHeaderLabels([
            "Código", "Fecha", "Total", "Estado", "Productos"
        ])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_ventas.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.tabla_ventas)
    
    def setup_inventario_tab(self):
        """Configura la pestaña de reportes de inventario"""
        layout = QVBoxLayout(self.tab_inventario)
        
        # Filtros
        filtros_layout = QHBoxLayout()
        
        # Categoría
        form_categoria = QFormLayout()
        self.combo_categoria = QComboBox()
        form_categoria.addRow("Categoría:", self.combo_categoria)
        
        # Estado de stock
        form_estado = QFormLayout()
        self.combo_estado = QComboBox()
        self.combo_estado.addItem("Todos", "")
        self.combo_estado.addItem("Stock bajo", "bajo")
        self.combo_estado.addItem("En stock", "en_stock")
        self.combo_estado.addItem("Sin stock", "sin_stock")
        form_estado.addRow("Estado:", self.combo_estado)
        
        # Botón de filtrar
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.filtrar_inventario)
        
        filtros_layout.addLayout(form_categoria)
        filtros_layout.addLayout(form_estado)
        filtros_layout.addWidget(btn_filtrar)
        filtros_layout.addStretch()
        
        layout.addLayout(filtros_layout)
        
        # Tabla de inventario
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(5)
        self.tabla_inventario.setHorizontalHeaderLabels([
            "Código", "Producto", "Categoría", "Precio", "Stock"
        ])
        self.tabla_inventario.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_inventario.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.tabla_inventario)
    
    def setup_categorias_tab(self):
        """Configura la pestaña de reportes por categoría"""
        layout = QVBoxLayout(self.tab_categorias)
        
        # Tabla de resumen por categoría
        self.tabla_categorias = QTableWidget()
        self.tabla_categorias.setColumnCount(4)
        self.tabla_categorias.setHorizontalHeaderLabels([
            "Categoría", "Productos", "Stock Total", "Valor Total"
        ])
        self.tabla_categorias.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_categorias.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.tabla_categorias)
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales para los reportes"""
        try:
            # Cargar categorías para el filtro
            self.cargar_categorias()
            
            # Cargar datos iniciales
            self.filtrar_ventas()
            self.filtrar_inventario()
            self.generar_reporte_categorias()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al cargar datos",
                f"No se pudieron cargar los datos iniciales: {str(e)}"
            )
    
    def cargar_categorias(self):
        """Carga las categorías en el combo box"""
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Todas las categorías", "")
        
        categorias = Categoria.obtener_todas()
        for categoria in categorias:
            self.combo_categoria.addItem(categoria.nombre, categoria.id)
    
    def filtrar_ventas(self):
        """Filtra las ventas según los criterios seleccionados"""
        fecha_desde = self.fecha_desde.date().toPyDate()
        fecha_hasta = self.fecha_hasta.date().toPyDate()
        
        ventas = Venta.obtener_todas(fecha_desde, fecha_hasta)
        
        self.tabla_ventas.setRowCount(0)
        
        for venta in ventas:
            row = self.tabla_ventas.rowCount()
            self.tabla_ventas.insertRow(row)
            
            # Código
            codigo_item = QTableWidgetItem(venta.codigo_venta)
            self.tabla_ventas.setItem(row, 0, codigo_item)
            
            # Fecha
            fecha_item = QTableWidgetItem(venta.fecha_venta.strftime("%Y-%m-%d %H:%M"))
            self.tabla_ventas.setItem(row, 1, fecha_item)
            
            # Total
            total_item = QTableWidgetItem(f"$ {venta.total:.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_ventas.setItem(row, 2, total_item)
            
            # Estado
            estado_item = QTableWidgetItem(venta.estado.capitalize())
            estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if venta.estado == 'cancelada':
                estado_item.setForeground(Qt.GlobalColor.red)
            self.tabla_ventas.setItem(row, 3, estado_item)
            
            # Productos
            productos = ", ".join([f"{item.cantidad}x {item.producto.nombre}" for item in venta.items])
            productos_item = QTableWidgetItem(productos)
            self.tabla_ventas.setItem(row, 4, productos_item)
    
    def filtrar_inventario(self):
        """Filtra los productos según los criterios seleccionados"""
        categoria_id = self.combo_categoria.currentData()
        estado = self.combo_estado.currentData()
        
        # Construir la consulta
        query = """
        SELECT p.*, c.nombre as categoria_nombre 
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE 1=1
        """
        
        params = []
        
        # Filtrar por categoría
        if categoria_id:
            query += " AND p.categoria_id = ?"
            params.append(categoria_id)
        
        # Filtrar por estado de stock
        if estado == "bajo":
            query += " AND p.cantidad > 0 AND p.cantidad <= p.stock_minimo"
        elif estado == "en_stock":
            query += " AND p.cantidad > 0"
        elif estado == "sin_stock":
            query += " AND p.cantidad <= 0"
        
        # Ordenar por nombre
        query += " ORDER BY p.nombre"
        
        # Ejecutar consulta
        productos = Producto.ejecutar_consulta(query, params) if params else Producto.ejecutar_consulta(query)
        
        # Mostrar resultados
        self.tabla_inventario.setRowCount(0)
        
        for producto_data in productos:
            row = self.tabla_inventario.rowCount()
            self.tabla_inventario.insertRow(row)
            
            # Código
            codigo_item = QTableWidgetItem(producto_data['codigo'])
            self.tabla_inventario.setItem(row, 0, codigo_item)
            
            # Nombre
            nombre_item = QTableWidgetItem(producto_data['nombre'])
            self.tabla_inventario.setItem(row, 1, nombre_item)
            
            # Categoría
            categoria_item = QTableWidgetItem(producto_data['categoria_nombre'] or "Sin categoría")
            self.tabla_inventario.setItem(row, 2, categoria_item)
            
            # Precio
            precio_item = QTableWidgetItem(f"$ {float(producto_data['precio_venta'] or 0):.2f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_inventario.setItem(row, 3, precio_item)
            
            # Stock
            stock = int(producto_data['cantidad'] or 0)
            stock_item = QTableWidgetItem(str(stock))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Resaltar si el stock es bajo
            stock_minimo = int(producto_data.get('stock_minimo', 0) or 0)
            if stock <= 0:
                stock_item.setForeground(Qt.GlobalColor.red)
            elif stock <= stock_minimo:
                stock_item.setForeground(Qt.GlobalColor.darkYellow)
            
            self.tabla_inventario.setItem(row, 4, stock_item)
    
    def generar_reporte_categorias(self):
        """Genera un resumen de productos por categoría"""
        query = """
        SELECT 
            c.nombre as categoria,
            COUNT(p.id) as cantidad_productos,
            COALESCE(SUM(p.cantidad), 0) as stock_total,
            COALESCE(SUM(p.cantidad * p.precio_venta), 0) as valor_total
        FROM categorias c
        LEFT JOIN productos p ON c.id = p.categoria_id
        GROUP BY c.id, c.nombre
        ORDER BY c.nombre
        """
        
        resultados = Categoria.ejecutar_consulta(query)
        
        self.tabla_categorias.setRowCount(0)
        
        for i, fila in enumerate(resultados):
            row = self.tabla_categorias.rowCount()
            self.tabla_categorias.insertRow(row)
            
            # Categoría
            categoria_item = QTableWidgetItem(fila['categoria'] or "Sin categoría")
            self.tabla_categorias.setItem(row, 0, categoria_item)
            
            # Cantidad de productos
            cantidad_item = QTableWidgetItem(str(fila['cantidad_productos']))
            cantidad_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_categorias.setItem(row, 1, cantidad_item)
            
            # Stock total
            stock_item = QTableWidgetItem(str(int(fila['stock_total'])))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_categorias.setItem(row, 2, stock_item)
            
            # Valor total
            valor_item = QTableWidgetItem(f"$ {float(fila['valor_total']):.2f}")
            valor_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_categorias.setItem(row, 3, valor_item)
    
    def exportar_a_excel(self):
        """Exporta el reporte actual a un archivo Excel"""
        # Obtener la pestaña actual
        current_tab = self.tabs.currentIndex()
        
        # Determinar qué tabla exportar según la pestaña actual
        if current_tab == 0:  # Ventas
            tabla = self.tabla_ventas
            nombre_archivo = "reporte_ventas"
        elif current_tab == 1:  # Inventario
            tabla = self.tabla_inventario
            nombre_archivo = "reporte_inventario"
        else:  # Categorías
            tabla = self.tabla_categorias
            nombre_archivo = "reporte_categorias"
        
        # Pedir al usuario dónde guardar el archivo
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar a Excel",
            f"{nombre_archivo}.xlsx",
            "Archivos de Excel (*.xlsx);;Todos los archivos (*)"
        )
        
        if not file_path:
            return  # Usuario canceló
        
        try:
            # Crear un DataFrame de pandas con los datos de la tabla
            import pandas as pd
            
            # Obtener encabezados
            headers = []
            for i in range(tabla.columnCount()):
                headers.append(tabla.horizontalHeaderItem(i).text())
            
            # Obtener datos
            data = []
            for row in range(tabla.rowCount()):
                row_data = []
                for col in range(tabla.columnCount()):
                    item = tabla.item(row, col)
                    if item is not None:
                        # Limpiar el texto (eliminar $ y otros formatos)
                        text = item.text().replace('$', '').strip()
                        # Intentar convertir a número si es posible
                        try:
                            if '.' in text:
                                row_data.append(float(text))
                            else:
                                row_data.append(int(text))
                        except ValueError:
                            row_data.append(text)
                    else:
                        row_data.append("")
                data.append(row_data)
            
            # Crear DataFrame y guardar en Excel
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            QMessageBox.information(
                self,
                "Exportación exitosa",
                f"El reporte se ha exportado correctamente a:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al exportar",
                f"No se pudo exportar el reporte. Error: {str(e)}"
            )
    
    def actualizar_reportes(self):
        """Actualiza todos los reportes"""
        self.filtrar_ventas()
        self.filtrar_inventario()
        self.generar_reporte_categorias()
