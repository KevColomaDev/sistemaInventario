from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QLineEdit, QMessageBox, QDateEdit, QComboBox, QFormLayout,
    QAbstractItemView, QDialogButtonBox, QSpinBox, QDoubleSpinBox,
    QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QIcon, QFont

from src.models.venta import Venta, VentaItem
from src.models.producto import Producto
from .ventas_view import VentaItemDialog


class VentaDialog(QDialog):
    venta_guardada = pyqtSignal()
    
    def __init__(self, parent=None, venta_id=None):
        super().__init__(parent)
        self.venta_id = venta_id
        self.venta = Venta()
        self.read_only = False
        
        if venta_id is not None:
            self.venta = Venta.obtener_por_id(venta_id)
            if not self.venta:
                QMessageBox.critical(self, "Error", "No se pudo cargar la venta.")
                self.reject()
                return
        
        self.setWindowTitle("Nueva Venta" if venta_id is None else f"Venta {self.venta.codigo_venta}")
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
    
    def set_read_only(self):
        """Configura el diálogo como solo lectura"""
        self.read_only = True
        self.setWindowTitle(f"Detalles de Venta - {self.venta.codigo_venta}")
        self.btn_guardar.setVisible(False)
        self.btn_cancelar_venta.setVisible(False)
        self.btn_agregar_producto.setEnabled(False)
        self.btn_eliminar_producto.setEnabled(False)
        self.notas_input.setReadOnly(True)
    
    def setup_ui(self):
        """Configura la interfaz de usuario del diálogo"""
        layout = QVBoxLayout(self)
        
        # Información de la venta
        info_layout = QHBoxLayout()
        
        # Columna izquierda - Datos de la venta
        form_layout = QFormLayout()
        
        # Código de venta
        self.codigo_label = QLabel(self.venta.codigo_venta or "Se generará automáticamente")
        form_layout.addRow("Código:", self.codigo_label)
        
        # Fecha
        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setEnabled(not self.read_only)
        form_layout.addRow("Fecha:", self.fecha_input)
        
        # Estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItem("Completada", "completada")
        self.estado_combo.addItem("Cancelada", "cancelada")
        self.estado_combo.setCurrentIndex(0 if not self.venta.estado or self.venta.estado == 'completada' else 1)
        self.estado_combo.setEnabled(not self.read_only)
        form_layout.addRow("Estado:", self.estado_combo)
        
        info_layout.addLayout(form_layout)
        
        # Columna derecha - Total
        total_layout = QVBoxLayout()
        total_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        self.total_label = QLabel("$ 0.00")
        self.total_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        total_layout.addWidget(self.total_label)
        
        info_layout.addLayout(total_layout)
        
        layout.addLayout(info_layout)
        
        # Línea separadora
        separator = QLabel()
        separator.setFrameShape(QLabel.Shape.HLine)
        separator.setFrameShadow(QLabel.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        
        self.btn_agregar_producto = QPushButton("Agregar Producto")
        self.btn_agregar_producto.setIcon(QIcon(":/icons/plus.png"))
        self.btn_agregar_producto.clicked.connect(self.agregar_producto)
        
        self.btn_eliminar_producto = QPushButton("Eliminar Producto")
        self.btn_eliminar_producto.setIcon(QIcon(":/icons/trash-2.png"))
        self.btn_eliminar_producto.clicked.connect(self.eliminar_producto)
        
        btn_layout.addWidget(self.btn_agregar_producto)
        btn_layout.addWidget(self.btn_eliminar_producto)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Código", "Producto", "Precio Unit.", "Cantidad", "Subtotal"
        ])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_productos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_productos.itemSelectionChanged.connect(self.actualizar_botones)
        
        layout.addWidget(self.tabla_productos)
        
        # Notas
        self.notas_input = QTextEdit()
        self.notas_input.setPlaceholderText("Notas adicionales...")
        self.notas_input.setMaximumHeight(80)
        if self.venta.notas:
            self.notas_input.setText(self.venta.notas)
        
        layout.addWidget(QLabel("Notas:"))
        layout.addWidget(self.notas_input)
        
        # Botones de acción
        button_box = QDialogButtonBox()
        
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setIcon(QIcon(":/icons/save.png"))
        self.btn_guardar.clicked.connect(self.guardar_venta)
        
        self.btn_cancelar_venta = QPushButton("Cancelar Venta")
        self.btn_cancelar_venta.setIcon(QIcon(":/icons/trash-2.png"))
        self.btn_cancelar_venta.clicked.connect(self.cancelar_venta)
        self.btn_cancelar_venta.setVisible(False)
        
        button_box.addButton(self.btn_guardar, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton("Cerrar", QDialogButtonBox.ButtonRole.RejectRole)
        button_box.addButton(self.btn_cancelar_venta, QDialogButtonBox.ButtonRole.ActionRole)
        
        button_box.accepted.connect(self.guardar_venta)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        # Cargar datos si es una venta existente
        if self.venta_id is not None:
            self.cargar_datos_venta()
        
        # Actualizar total
        self.actualizar_total()
        self.actualizar_botones()
        
        # Establecer foco en el primer campo
        if not self.read_only:
            self.btn_agregar_producto.setFocus()
    
    def cargar_datos_venta(self):
        """Carga los datos de la venta en el formulario"""
        self.codigo_label.setText(self.venta.codigo_venta)
        self.fecha_input.setDate(QDate.fromString(str(self.venta.fecha_venta), "yyyy-MM-dd"))
        
        # Cargar productos en la tabla
        self.tabla_productos.setRowCount(0)
        
        for item in self.venta.items:
            # Obtener datos del producto
            producto = Producto.obtener_por_id(item.producto_id)
            if not producto:
                continue
            
            row = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(row)
            
            # Código
            codigo_item = QTableWidgetItem(producto.codigo)
            self.tabla_productos.setItem(row, 0, codigo_item)
            
            # Nombre
            nombre_item = QTableWidgetItem(producto.nombre)
            self.tabla_productos.setItem(row, 1, nombre_item)
            
            # Precio unitario
            precio_item = QTableWidgetItem(f"$ {item.precio_unitario:.2f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_productos.setItem(row, 2, precio_item)
            
            # Cantidad
            cantidad_item = QTableWidgetItem(str(item.cantidad))
            cantidad_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_productos.setItem(row, 3, cantidad_item)
            
            # Subtotal
            subtotal_item = QTableWidgetItem(f"$ {item.subtotal:.2f}")
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_productos.setItem(row, 4, subtotal_item)
        
        # Ajustar columnas
        self.tabla_productos.resizeColumnsToContents()
        
        # Mostrar botón de cancelar si la venta está completada
        if self.venta.estado == 'completada' and not self.read_only:
            self.btn_cancelar_venta.setVisible(True)
    
    def agregar_producto(self):
        """Abre el diálogo para agregar un producto a la venta"""
        from .seleccionar_producto_dialog import SeleccionarProductoDialog
        
        dialog = SeleccionarProductoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            producto = dialog.get_producto_seleccionado()
            if producto:
                # Verificar si el producto ya está en la venta
                for i in range(self.tabla_productos.rowCount()):
                    codigo = self.tabla_productos.item(i, 0).text()
                    if codigo == producto.codigo:
                        QMessageBox.information(
                            self,
                            "Producto existente",
                            f"El producto {producto.nombre} ya está en la venta. "
                            "Puede modificar la cantidad seleccionando el producto y usando el botón 'Agregar Producto'."
                        )
                        return
                
                # Abrir diálogo para cantidad y precio
                item_dialog = VentaItemDialog(self, producto)
                if item_dialog.exec() == QDialog.DialogCode.Accepted:
                    item_data = item_dialog.get_item_data()
                    self.agregar_producto_tabla(item_data)
                    self.actualizar_total()
    
    def agregar_producto_tabla(self, item_data):
        """Agrega un producto a la tabla de la venta"""
        producto = item_data['producto']
        
        row = self.tabla_productos.rowCount()
        self.tabla_productos.insertRow(row)
        
        # Código
        codigo_item = QTableWidgetItem(producto.codigo)
        self.tabla_productos.setItem(row, 0, codigo_item)
        
        # Nombre
        nombre_item = QTableWidgetItem(producto.nombre)
        self.tabla_productos.setItem(row, 1, nombre_item)
        
        # Precio unitario
        precio_item = QTableWidgetItem(f"$ {item_data['precio_unitario']:.2f}")
        precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos.setItem(row, 2, precio_item)
        
        # Cantidad
        cantidad_item = QTableWidgetItem(str(item_data['cantidad']))
        cantidad_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabla_productos.setItem(row, 3, cantidad_item)
        
        # Subtotal
        subtotal_item = QTableWidgetItem(f"$ {item_data['subtotal']:.2f}")
        subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_productos.setItem(row, 4, subtotal_item)
        
        # Ajustar columnas
        self.tabla_productos.resizeColumnsToContents()
    
    def eliminar_producto(self):
        """Elimina el producto seleccionado de la venta"""
        selected = self.tabla_productos.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Selección requerida", "Por favor, seleccione un producto para eliminar.")
            return
        
        row = selected[0].row()
        producto = self.tabla_productos.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el producto {producto} de la venta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.tabla_productos.removeRow(row)
            self.actualizar_total()
    
    def actualizar_total(self):
        """Actualiza el total de la venta"""
        total = 0.0
        
        for row in range(self.tabla_productos.rowCount()):
            subtotal_text = self.tabla_productos.item(row, 4).text().replace("$", "").strip()
            try:
                subtotal = float(subtotal_text)
                total += subtotal
            except ValueError:
                pass
        
        self.total_label.setText(f"$ {total:.2f}")
    
    def actualizar_botones(self):
        """Actualiza el estado de los botones según la selección"""
        selected = bool(self.tabla_productos.selectedItems())
        self.btn_eliminar_producto.setEnabled(selected and not self.read_only)
    
    def guardar_venta(self):
        """Guarda la venta en la base de datos"""
        # Validar que haya al menos un producto
        if self.tabla_productos.rowCount() == 0:
            QMessageBox.warning(self, "Venta vacía", "Debe agregar al menos un producto a la venta.")
            return
        
        # Crear o actualizar la venta
        self.venta.fecha_venta = self.fecha_input.date().toPyDate()
        self.venta.estado = self.estado_combo.currentData()
        self.venta.notas = self.notas_input.toPlainText()
        
        # Limpiar ítems existentes
        self.venta.items = []
        
        # Agregar ítems a la venta
        for row in range(self.tabla_productos.rowCount()):
            codigo = self.tabla_productos.item(row, 0).text()
            producto = Producto.obtener_por_codigo(codigo)
            
            if not producto:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se encontró el producto con código {codigo}."
                )
                return
            
            cantidad = int(self.tabla_productos.item(row, 3).text())
            precio_text = self.tabla_productos.item(row, 2).text().replace("$", "").strip()
            precio = float(precio_text)
            
            # Verificar stock si es una venta nueva
            if self.venta_id is None and producto.cantidad < cantidad:
                QMessageBox.warning(
                    self,
                    "Stock insuficiente",
                    f"No hay suficiente stock para el producto {producto.nombre}.\n"
                    f"Stock disponible: {producto.cantidad}"
                )
                return
            
            self.venta.agregar_item(producto.id, cantidad, precio)
        
        # Guardar la venta
        try:
            self.venta.guardar()
            QMessageBox.information(
                self,
                "Venta guardada",
                f"La venta {self.venta.codigo_venta} ha sido guardada correctamente."
            )
            self.venta_guardada.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al guardar",
                f"No se pudo guardar la venta. Error: {str(e)}"
            )
    
    def cancelar_venta(self):
        """Cancela la venta actual"""
        if self.venta.estado == 'cancelada':
            QMessageBox.information(
                self,
                "Venta ya cancelada",
                "Esta venta ya ha sido cancelada anteriormente."
            )
            return
        
        reply = QMessageBox.question(
            self, 
            "Confirmar cancelación",
            f"¿Está seguro de cancelar la venta {self.venta.codigo_venta}?\n"
            "Esta acción no se puede deshacer y devolverá el stock al inventario.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            motivo = "Cancelado desde el diálogo de edición"
            if Venta.cancelar_venta(self.venta.id, motivo):
                QMessageBox.information(
                    self,
                    "Venta cancelada",
                    f"La venta {self.venta.codigo_venta} ha sido cancelada."
                )
                self.venta_guardada.emit()
                self.reject()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No se pudo cancelar la venta."
                )
