from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QLineEdit, QMessageBox, QAbstractItemView, QDialogButtonBox,
    QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from src.models.producto import Producto
from src.models.categoria import Categoria


class SeleccionarProductoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Producto")
        self.setMinimumSize(600, 400)
        
        self.producto_seleccionado = None
        self.setup_ui()
        self.cargar_categorias()
        self.cargar_productos()
    
    def setup_ui(self):
        """Configura la interfaz de usuario del diálogo"""
        layout = QVBoxLayout(self)
        
        # Barra de búsqueda y filtro por categoría
        search_layout = QHBoxLayout()

        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar productos...")
        self.buscar_input.textChanged.connect(self.filtrar_productos)

        self.categoria_combo = QComboBox()
        self.categoria_combo.addItem("Todas las categorías", None)
        self.categoria_combo.currentIndexChanged.connect(self.filtrar_productos)

        search_layout.addWidget(QLabel("Buscar:"))
        search_layout.addWidget(self.buscar_input)
        search_layout.addWidget(QLabel("Categoría:"))
        search_layout.addWidget(self.categoria_combo)
        
        layout.addLayout(search_layout)
        
        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Código", "Nombre", "Categoría", "Precio Venta", "Stock"
        ])
        header = self.tabla_productos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Código
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Nombre (ocupa ancho disponible)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Categoría
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Precio
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Stock
        header.setStretchLastSection(False)
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_productos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_productos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_productos.doubleClicked.connect(self.aceptar_seleccion)
        
        layout.addWidget(self.tabla_productos)
        
        # Botones
        button_box = QDialogButtonBox()
        
        self.btn_seleccionar = QPushButton("Seleccionar")
        self.btn_seleccionar.setIcon(QIcon(":/icons/check.png"))
        self.btn_seleccionar.clicked.connect(self.aceptar_seleccion)
        
        button_box.addButton("Cancelar", QDialogButtonBox.ButtonRole.RejectRole)
        button_box.addButton(self.btn_seleccionar, QDialogButtonBox.ButtonRole.AcceptRole)
        
        button_box.accepted.connect(self.aceptar_seleccion)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        # Establecer foco en la búsqueda
        self.buscar_input.setFocus()
    
    def cargar_productos(self, filtro=None):
        """Carga los productos en la tabla"""
        categoria_id = self.categoria_combo.currentData() if hasattr(self, 'categoria_combo') else None
        if filtro:
            productos = Producto.buscar(filtro, categoria_id)
        else:
            productos = Producto.obtener_todos(categoria_id)
        # Obtener solo productos con stock mayor a 0
        productos = [p for p in productos if getattr(p, 'cantidad', 0) > 0]
        
        self.tabla_productos.setRowCount(0)
        
        for producto in productos:
            self.agregar_producto_tabla(producto)
        
        # Ajuste de columnas manejado por header (sin forzar resize por contenido)
    
    def agregar_producto_tabla(self, producto):
        """Agrega un producto a la tabla"""
        if not producto or not hasattr(producto, 'id'):
            return
            
        row = self.tabla_productos.rowCount()
        self.tabla_productos.insertRow(row)
        
        # Código - Guardamos el ID del producto en UserRole para usarlo después
        codigo_item = QTableWidgetItem(producto.codigo)
        codigo_item.setData(Qt.ItemDataRole.UserRole, producto.id)  # Almacenar el ID
        self.tabla_productos.setItem(row, 0, codigo_item)
        
        # Nombre
        nombre_item = QTableWidgetItem(producto.nombre)
        self.tabla_productos.setItem(row, 1, nombre_item)
        
        # Categoría (usar atributo categoria_nombre del modelo Producto)
        categoria_nombre = getattr(producto, 'categoria_nombre', None) or "Sin categoría"
        categoria_item = QTableWidgetItem(categoria_nombre)
        self.tabla_productos.setItem(row, 2, categoria_item)
        
        # Precio de venta - Usar el atributo 'precio' en lugar de 'precio_venta'
        precio = float(getattr(producto, 'precio', 0.0))
        precio_item = QTableWidgetItem(f"$ {precio:.2f}")
        precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos.setItem(row, 3, precio_item)
        
        # Stock
        stock = int(getattr(producto, 'cantidad', 0))
        stock_item = QTableWidgetItem(str(stock))
        stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Resaltar si el stock es bajo
        if stock < 5:  # Ajusta este valor según lo que consideres "bajo stock"
            stock_item.setForeground(Qt.GlobalColor.red)
        
        self.tabla_productos.setItem(row, 4, stock_item)
    
    def filtrar_productos(self):
        """Filtra los productos según el texto de búsqueda"""
        filtro = self.buscar_input.text().strip()
        self.cargar_productos(filtro if filtro else None)

    def cargar_categorias(self):
        """Carga las categorías en el combo"""
        if not hasattr(self, 'categoria_combo'):
            return
        self.categoria_combo.blockSignals(True)
        current = self.categoria_combo.currentData()
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Todas las categorías", None)
        for cat in Categoria.obtener_todas():
            self.categoria_combo.addItem(cat.nombre, cat.id)
        # Restaurar selección si posible
        if current is not None:
            idx = self.categoria_combo.findData(current)
            if idx >= 0:
                self.categoria_combo.setCurrentIndex(idx)
        self.categoria_combo.blockSignals(False)
    
    def aceptar_seleccion(self):
        """Acepta la selección del producto"""
        selected = self.tabla_productos.selectedItems()
        if not selected:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Por favor, seleccione un producto para continuar."
            )
            return
        
        # Obtener el ID del producto seleccionado desde los datos de la tabla
        row = selected[0].row()
        producto_id = self.tabla_productos.item(row, 0).data(Qt.ItemDataRole.UserRole)  # Almacenamos el ID en UserRole
        
        if not producto_id:
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo identificar el producto seleccionado."
            )
            return
        
        # Obtener el producto completo de la base de datos usando el ID
        self.producto_seleccionado = Producto.obtener_por_id(producto_id)
        
        if not self.producto_seleccionado:
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo cargar la información del producto seleccionado."
            )
            return
            
        self.accept()
    
    def get_producto_seleccionado(self):
        """Devuelve el producto seleccionado"""
        return self.producto_seleccionado
