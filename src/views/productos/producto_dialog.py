from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox,
    QSpinBox, QPushButton, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from src.models.producto import Producto
from src.models.categoria import Categoria

class ProductoDialog(QDialog):
    producto_guardado = pyqtSignal()
    
    def __init__(self, producto_id=None, parent=None):
        super().__init__(parent)
        self.producto_id = producto_id
        self.setWindowTitle("Nuevo Producto" if producto_id is None else "Editar Producto")
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.cargar_categorias()
        
        if producto_id is not None:
            self.cargar_producto()
    
    def setup_ui(self):
        """Configura la interfaz de usuario del diálogo"""
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Código
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código único del producto")
        self.codigo_input.returnPressed.connect(self.guardar_producto)  # Enter key press
        form_layout.addRow("Código*:", self.codigo_input)
        
        # Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del producto")
        self.nombre_input.returnPressed.connect(self.guardar_producto)  # Enter key press
        form_layout.addRow("Nombre*:", self.nombre_input)
        
        # Categoría
        self.categoria_combo = QComboBox()
        form_layout.addRow("Categoría:", self.categoria_combo)
        
        # Configurar el botón de guardar como predeterminado
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        # Precio
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setPrefix("$ ")
        self.precio_input.setRange(0, 999999.99)
        self.precio_input.setDecimals(2)
        self.precio_input.setSingleStep(0.5)
        form_layout.addRow("Precio*:", self.precio_input)
        
        # Cantidad
        self.cantidad_input = QSpinBox()
        self.cantidad_input.setMinimum(0)
        self.cantidad_input.setMaximum(999999)
        form_layout.addRow("Cantidad inicial*:", self.cantidad_input)
        
        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción detallada del producto")
        self.descripcion_input.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.descripcion_input)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Configurar botón de guardar como predeterminado
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar_producto)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_guardar)
        button_layout.addWidget(self.btn_cancelar)
        
        layout.addLayout(button_layout)
        
        # Configurar el botón de guardar como predeterminado
        self.btn_guardar.setDefault(True)
        
        # Configurar estilos
        self.setup_styles()
    
    def setup_styles(self):
        """Configura los estilos del diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F0E5;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 6px 8px;
                border: 1px solid #DAC0A3;
                border-radius: 4px;
                background-color: white;
                color: #111;
            }
            
            QComboBox QAbstractItemView {
                background-color: white;
                color: #111;
                selection-background-color: #EADBC8;
                selection-color: #111;
            }
            
            QTextEdit {
                padding: 4px;
            }
            
            QPushButton {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }
            
            QPushButton#btn_guardar {
                background-color: #A8E6CF;
                color: #1B5E20;
            }
            
            QPushButton#btn_cancelar {
                background-color: #FFD3B6;
                color: #BF360C;
            }
            
            QPushButton:hover {
                opacity: 0.9;
            }
            
            QPushButton:pressed {
                opacity: 0.8;
            }
            
            QLabel {
                color: #4A4A4A;
                font-weight: 500;
            }
        """)
        
        # Aplicar estilos específicos a los botones
        self.btn_guardar.setObjectName("btn_guardar")
        self.btn_cancelar.setObjectName("btn_cancelar")
    
    def cargar_categorias(self):
        """Carga las categorías en el combobox"""
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Sin categoría", None)
        
        categorias = Categoria.obtener_todas()
        for categoria in categorias:
            self.categoria_combo.addItem(categoria.nombre, categoria.id)
    
    def cargar_producto(self):
        """Carga los datos del producto en el formulario"""
        if self.producto_id is None:
            return
            
        producto = Producto.obtener_por_id(self.producto_id)
        if not producto:
            QMessageBox.critical(self, "Error", "No se pudo cargar el producto.")
            self.reject()
            return
        
        self.setWindowTitle(f"Editar: {producto.nombre}")
        self.codigo_input.setText(producto.codigo)
        self.nombre_input.setText(producto.nombre)
        self.descripcion_input.setPlainText(producto.descripcion)
        self.precio_input.setValue(producto.precio)
        self.cantidad_input.setValue(producto.cantidad)
        
        # Seleccionar la categoría correcta
        index = self.categoria_combo.findData(producto.categoria_id)
        if index >= 0:
            self.categoria_combo.setCurrentIndex(index)
    
    def validar_formulario(self):
        """Valida los datos del formulario"""
        errores = []
        
        codigo = self.codigo_input.text().strip()
        nombre = self.nombre_input.text().strip()
        
        if not codigo:
            errores.append("El código es obligatorio")
        
        if not nombre:
            errores.append("El nombre es obligatorio")
        
        if self.precio_input.value() <= 0:
            errores.append("El precio debe ser mayor a cero")
        
        # Verificar si el código ya existe (solo para nuevo producto)
        if self.producto_id is None and codigo:
            # Verificar si ya existe un producto con el mismo código
            productos = Producto.buscar(codigo)
            if productos:
                errores.append("Ya existe un producto con este código")
        
        return errores
    
    def guardar_producto(self):
        """Guarda o actualiza el producto"""
        errores = self.validar_formulario()
        if errores:
            QMessageBox.warning(
                self,
                "Error de validación",
                "Por favor, corrija los siguientes errores:\n\n• " + "\n• ".join(errores)
            )
            return
        
        # Crear o actualizar el producto
        producto = Producto(
            id=self.producto_id,
            codigo=self.codigo_input.text().strip(),
            nombre=self.nombre_input.text().strip(),
            descripcion=self.descripcion_input.toPlainText().strip(),
            precio=self.precio_input.value(),
            cantidad=self.cantidad_input.value(),
            categoria_id=self.categoria_combo.currentData()
        )
        
        try:
            if self.producto_id is None:
                # Nuevo producto
                producto_id = producto.guardar()
                if producto_id:
                    QMessageBox.information(
                        self,
                        "Producto guardado",
                        f"El producto '{producto.nombre}' ha sido guardado correctamente."
                    )
                    self.producto_guardado.emit()
                    self.accept()
            else:
                # Actualizar producto existente
                if producto.actualizar() is not None:
                    QMessageBox.information(
                        self,
                        "Producto actualizado",
                        f"Los datos de '{producto.nombre}' han sido actualizados correctamente."
                    )
                    self.producto_guardado.emit()
                    self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar el producto: {str(e)}"
            )
