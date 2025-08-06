from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

from src.models.producto import Producto
from src.models.categoria import Categoria

class ProductosView(QWidget):
    # Señales
    agregar_producto = pyqtSignal()
    editar_producto = pyqtSignal(int)  # ID del producto
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.cargar_categorias()
        self.cargar_productos()
    
    def setup_ui(self):
        """Configura la interfaz de usuario de la vista de productos"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Barra de búsqueda y filtros
        search_layout = QHBoxLayout()
        
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar productos...")
        self.buscar_input.textChanged.connect(self.buscar_productos)
        
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItem("Todas las categorías", None)
        self.categoria_combo.currentIndexChanged.connect(self.filtrar_por_categoria)
        
        btn_agregar = QPushButton("Nuevo Producto")
        btn_agregar.setIcon(QIcon(":/icons/plus.png"))
        btn_agregar.clicked.connect(self.agregar_producto)
        
        search_layout.addWidget(QLabel("Buscar:"))
        search_layout.addWidget(self.buscar_input)
        search_layout.addWidget(QLabel("Categoría:"))
        search_layout.addWidget(self.categoria_combo)
        search_layout.addWidget(btn_agregar)
        
        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(6)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Código", "Nombre", "Categoría", "Precio", "Cantidad", "Acciones"
        ])
        
        # Estilo para la tabla
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                color: black;
                gridline-color: #d0d0d0;
            }
            QTableWidget::item {
                color: black;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QLabel {
                color: black;
            }
            QHeaderView::section {
                color: black;
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
            QPushButton#btn_editar {
                color: white;
                background-color: #0078d7;
                border: none;
                padding: 3px 8px;
                border-radius: 4px;
                margin: 1px;
            }
            QPushButton#btn_editar:hover {
                background-color: #106ebe;
            }
            QPushButton#btn_eliminar {
                color: white;
                background-color: #dc3545;
                border: none;
                padding: 3px 8px;
                border-radius: 4px;
                margin: 1px;
            }
            QPushButton#btn_eliminar:hover {
                background-color: #c82333;
            }
        """)
        
        # Agregar leyenda de acciones
        legend = QLabel("<b>Leyenda:</b> <span style='color: #0078d7;'>Azul: Editar</span> | <span style='color: #dc3545;'>Rojo: Eliminar</span>")
        legend.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        search_layout.insertWidget(1, legend)  # Agregar la leyenda después del campo de búsqueda
        
        # Ajustar el ancho de las columnas
        header = self.tabla_productos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Código
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Categoría
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Precio
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Cantidad
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Acciones
        
        self.tabla_productos.verticalHeader().setVisible(False)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Widget de resumen
        resumen_widget = QFrame()
        resumen_widget.setObjectName("resumenWidget")
        resumen_layout = QHBoxLayout(resumen_widget)
        
        self.lbl_total_productos = QLabel("Total de productos: 0")
        self.lbl_productos_bajo_stock = QLabel("Productos con bajo stock: 0")
        self.lbl_valor_inventario = QLabel("Valor total del inventario: $0.00")
        
        resumen_layout.addWidget(self.lbl_total_productos)
        resumen_layout.addWidget(self.lbl_productos_bajo_stock)
        resumen_layout.addStretch()
        resumen_layout.addWidget(self.lbl_valor_inventario)
        
        # Agregar widgets al layout principal
        layout.addLayout(search_layout)
        layout.addWidget(self.tabla_productos)
        layout.addWidget(resumen_widget)
        
        # Configurar estilos
        self.setup_styles()
    
    def setup_styles(self):
        """Configura los estilos de la vista de productos"""
        self.setStyleSheet("""
            QLineEdit, QComboBox {
                padding: 6px 8px;
                border: 1px solid #DAC0A3;
                border-radius: 4px;
                min-width: 200px;
            }
            
            QPushButton {
                background-color: #DAC0A3;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                color: #4A4A4A;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #C8AE7D;
            }
            
            QPushButton:disabled {
                background-color: #EADBC8;
                color: #9E9E9E;
            }
            
            QTableWidget {
                background-color: white;
                border: 1px solid #DAC0A3;
                border-radius: 4px;
                gridline-color: #EADBC8;
                selection-background-color: #EADBC8;
            }
            
            QHeaderView::section {
                background-color: #EADBC8;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            
            #resumenWidget {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px 16px;
            }
            
            #resumenWidget QLabel {
                color: #4A4A4A;
                font-size: 13px;
            }
        """)
    
    def cargar_categorias(self):
        """Carga las categorías en el combobox"""
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Todas las categorías", None)
        
        categorias = Categoria.obtener_todas()
        for categoria in categorias:
            self.categoria_combo.addItem(categoria.nombre, categoria.id)
    
    def cargar_productos(self, productos=None):
        """Carga los productos en la tabla"""
        if productos is None:
            categoria_id = self.categoria_combo.currentData()
            productos = Producto.obtener_todos(categoria_id)
        
        self.tabla_productos.setRowCount(0)
        
        for producto in productos:
            row = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(row)
            
            # Agregar celdas con los datos del producto
            self.tabla_productos.setItem(row, 0, QTableWidgetItem(producto.codigo))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(producto.nombre))
            self.tabla_productos.setItem(row, 2, QTableWidgetItem(producto.categoria_nombre or "Sin categoría"))
            
            # Formatear precio con 2 decimales
            precio_item = QTableWidgetItem(f"${producto.precio:,.2f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_productos.setItem(row, 3, precio_item)
            
            # Resaltar en rojo si hay bajo stock (menos de 5 unidades)
            cantidad_item = QTableWidgetItem(str(producto.cantidad))
            cantidad_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if producto.cantidad < 5:
                cantidad_item.setForeground(Qt.GlobalColor.red)
            self.tabla_productos.setItem(row, 4, cantidad_item)
            
            # Botones de acción
            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout(acciones_widget)
            acciones_layout.setContentsMargins(5, 2, 5, 2)
            acciones_layout.setSpacing(5)
            
            btn_editar = QPushButton()
            btn_editar.setObjectName("btn_editar")
            btn_editar.setIcon(QIcon(":/icons/edit.png"))
            btn_editar.setToolTip("Editar producto")
            btn_editar.setFixedSize(28, 28)
            btn_editar.setStyleSheet("")
            btn_editar.clicked.connect(lambda _, p=producto: self.editar_producto.emit(p.id))
            
            btn_eliminar = QPushButton()
            btn_eliminar.setObjectName("btn_eliminar")
            btn_eliminar.setIcon(QIcon(":/icons/trash-2.png"))
            btn_eliminar.setToolTip("Eliminar producto")
            btn_eliminar.setFixedSize(28, 28)
            btn_eliminar.setStyleSheet("")
            btn_eliminar.clicked.connect(lambda _, p=producto: self.eliminar_producto(p))
            
            acciones_layout.addWidget(btn_editar)
            acciones_layout.addWidget(btn_eliminar)
            acciones_layout.addStretch()
            
            self.tabla_productos.setCellWidget(row, 5, acciones_widget)
        
        # Actualizar resumen
        self.actualizar_resumen()
    
    def buscar_productos(self):
        """Busca productos según el texto de búsqueda"""
        texto_busqueda = self.buscar_input.text().strip()
        categoria_id = self.categoria_combo.currentData()
        
        if texto_busqueda:
            productos = Producto.buscar(texto_busqueda, categoria_id)
            self.cargar_productos(productos)
        else:
            self.cargar_productos()
    
    def filtrar_por_categoria(self):
        """Filtra los productos por la categoría seleccionada"""
        self.cargar_productos()
    
    def actualizar_resumen(self):
        """Actualiza el resumen de productos"""
        total_productos = self.tabla_productos.rowCount()
        productos_bajo_stock = 0
        valor_total = 0.0
        
        for row in range(total_productos):
            cantidad = int(self.tabla_productos.item(row, 4).text())
            precio_text = self.tabla_productos.item(row, 3).text().replace('$', '').replace(',', '')
            precio = float(precio_text)
            
            if cantidad < 5:
                productos_bajo_stock += 1
            
            valor_total += cantidad * precio
        
        self.lbl_total_productos.setText(f"Total de productos: {total_productos}")
        self.lbl_productos_bajo_stock.setText(f"Productos con bajo stock: {productos_bajo_stock}")
        self.lbl_valor_inventario.setText(f"Valor total del inventario: ${valor_total:,.2f}")
    
    def eliminar_producto(self, producto):
        """Muestra un diálogo de confirmación para eliminar un producto"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar el producto '{producto.nombre}'?\n\n"
            f"Código: {producto.codigo}\n"
            f"Cantidad en inventario: {producto.cantidad}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                if producto.eliminar():
                    QMessageBox.information(
                        self,
                        "Producto eliminado",
                        f"El producto '{producto.nombre}' ha sido eliminado correctamente."
                    )
                    self.cargar_productos()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error al eliminar",
                    f"No se pudo eliminar el producto: {str(e)}"
                )
