import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QLineEdit, QMessageBox, QDateEdit, QComboBox, QFormLayout,
    QAbstractItemView, QDialog, QDialogButtonBox, QSpinBox,
    QDoubleSpinBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.venta import Venta, VentaItem
from models.producto import Producto


class VentaItemDialog(QDialog):
    def __init__(self, parent=None, producto=None, cantidad=1):
        super().__init__(parent)
        self.setWindowTitle("Agregar Producto")
        self.setMinimumWidth(400)
        
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = producto.precio_venta if producto else 0
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Producto
        self.producto_label = QLabel(self.producto.nombre if self.producto else "")
        form_layout.addRow("Producto:", self.producto_label)
        
        # Precio unitario
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setPrefix("$ ")
        self.precio_input.setDecimals(2)
        self.precio_input.setMinimum(0.01)
        self.precio_input.setMaximum(999999.99)
        self.precio_input.setValue(float(self.precio_unitario))
        self.precio_input.valueChanged.connect(self.actualizar_subtotal)
        form_layout.addRow("Precio unitario:", self.precio_input)
        
        # Cantidad
        self.cantidad_input = QSpinBox()
        self.cantidad_input.setMinimum(1)
        self.cantidad_input.setMaximum(self.producto.cantidad if self.producto else 9999)
        self.cantidad_input.setValue(self.cantidad)
        self.cantidad_input.valueChanged.connect(self.actualizar_subtotal)
        form_layout.addRow("Cantidad:", self.cantidad_input)
        
        # Subtotal
        self.subtotal_label = QLabel("$ 0.00")
        form_layout.addRow("Subtotal:", self.subtotal_label)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
        # Actualizar subtotal inicial
        self.actualizar_subtotal()
    
    def actualizar_subtotal(self):
        self.precio_unitario = self.precio_input.value()
        self.cantidad = self.cantidad_input.value()
        subtotal = self.precio_unitario * self.cantidad
        self.subtotal_label.setText(f"$ {subtotal:.2f}")
    
    def get_item_data(self):
        return {
            'producto': self.producto,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.precio_unitario * self.cantidad
        }


class VentasView(QWidget):
    venta_realizada = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setup_ui()
            self.cargar_ventas()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al inicializar ventas",
                f"Error al inicializar la vista de ventas: {str(e)}"
            )
            # Create an error widget if initialization fails
            error_widget = QWidget()
            layout = QVBoxLayout(error_widget)
            label = QLabel("No se pudo cargar el módulo de ventas. Por favor, verifica los datos e inténtalo de nuevo.")
            label.setWordWrap(True)
            layout.addWidget(label)
            self.setLayout(layout)
    
    def setup_ui(self):
        """Configura la interfaz de usuario de la vista de ventas"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Barra de herramientas
        tool_layout = QHBoxLayout()
        
        self.btn_nueva_venta = QPushButton("Nueva Venta")
        self.btn_nueva_venta.setIcon(QIcon(":/icons/plus.png"))
        self.btn_nueva_venta.clicked.connect(self.nueva_venta)
        
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar ventas...")
        self.buscar_input.textChanged.connect(self.buscar_ventas)
        
        # Filtros
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_desde.dateChanged.connect(self.filtrar_ventas)
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.dateChanged.connect(self.filtrar_ventas)
        
        self.estado_combo = QComboBox()
        self.estado_combo.addItem("Todas", "")
        self.estado_combo.addItem("Completadas", "completada")
        self.estado_combo.addItem("Canceladas", "cancelada")
        self.estado_combo.currentIndexChanged.connect(self.filtrar_ventas)
        
        tool_layout.addWidget(self.btn_nueva_venta)
        tool_layout.addStretch()
        tool_layout.addWidget(QLabel("Desde:"))
        tool_layout.addWidget(self.fecha_desde)
        tool_layout.addWidget(QLabel("Hasta:"))
        tool_layout.addWidget(self.fecha_hasta)
        tool_layout.addWidget(QLabel("Estado:"))
        tool_layout.addWidget(self.estado_combo)
        tool_layout.addWidget(QLabel("Buscar:"))
        tool_layout.addWidget(self.buscar_input)
        
        layout.addLayout(tool_layout)
        
        # Tabla de ventas
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(5)
        self.tabla_ventas.setHorizontalHeaderLabels([
            "Código", "Fecha", "Total", "Estado", "Acciones"
        ])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_ventas.horizontalHeader().setStretchLastSection(True)
        self.tabla_ventas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_ventas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.tabla_ventas)
        
        # Estilos
        self.setup_styles()
    
    def setup_styles(self):
        """Configura los estilos de la vista"""
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                gridline-color: #f0f0f0;
            }
            
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #333;
            }
            
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                border: 1px solid #d0d0d0;
                background-color: #f8f8f8;
            }
            
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            
            QPushButton#btn_ver {
                background-color: #4a90e2;
                color: white;
                border: none;
            }
            
            QPushButton#btn_cancelar {
                background-color: #e74c3c;
                color: white;
                border: none;
                margin-left: 5px;
            }
        """)
    
    def cargar_ventas(self):
        """Carga las ventas en la tabla"""
        self.tabla_ventas.setRowCount(0)
        
        fecha_desde = self.fecha_desde.date().toPyDate()
        fecha_hasta = self.fecha_hasta.date().toPyDate()
        estado = self.estado_combo.currentData()
        
        ventas = Venta.obtener_todas(fecha_desde, fecha_hasta, estado)
        
        for venta in ventas:
            self.agregar_venta_tabla(venta)
    
    def agregar_venta_tabla(self, venta):
        """Agrega una venta a la tabla"""
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
        
        # Acciones
        acciones_widget = QWidget()
        acciones_layout = QHBoxLayout(acciones_widget)
        acciones_layout.setContentsMargins(5, 2, 5, 2)
        acciones_layout.setSpacing(5)
        
        btn_ver = QPushButton("Ver")
        btn_ver.setObjectName("btn_ver")
        btn_ver.clicked.connect(lambda _, v=venta: self.ver_venta(v))
        
        acciones_layout.addWidget(btn_ver)
        
        if venta.estado == 'completada':
            btn_cancelar = QPushButton("Cancelar")
            btn_cancelar.setObjectName("btn_cancelar")
            btn_cancelar.clicked.connect(lambda _, v=venta: self.cancelar_venta(v))
            acciones_layout.addWidget(btn_cancelar)
        
        acciones_layout.addStretch()
        self.tabla_ventas.setCellWidget(row, 4, acciones_widget)
    
    def nueva_venta(self):
        """Abre el diálogo para crear una nueva venta"""
        from .venta_dialog import VentaDialog
        dialog = VentaDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_ventas()
            self.venta_realizada.emit()
    
    def ver_venta(self, venta):
        """Muestra los detalles de una venta"""
        from .venta_dialog import VentaDialog
        dialog = VentaDialog(self, venta.id)
        dialog.set_read_only()
        dialog.exec()
    
    def cancelar_venta(self, venta):
        """Cancela una venta"""
        reply = QMessageBox.question(
            self, 
            "Confirmar cancelación",
            f"¿Está seguro de cancelar la venta {venta.codigo_venta}?\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if Venta.cancelar_venta(venta.id, "Cancelado por el usuario"):
                QMessageBox.information(
                    self,
                    "Venta cancelada",
                    f"La venta {venta.codigo_venta} ha sido cancelada."
                )
                self.cargar_ventas()
                self.venta_realizada.emit()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No se pudo cancelar la venta."
                )
    
    def buscar_ventas(self):
        """Busca ventas por código"""
        texto = self.buscar_input.text().strip().lower()
        
        for row in range(self.tabla_ventas.rowCount()):
            codigo = self.tabla_ventas.item(row, 0).text().lower()
            if texto in codigo:
                self.tabla_ventas.setRowHidden(row, False)
            else:
                self.tabla_ventas.setRowHidden(row, True)
    
    def filtrar_ventas(self):
        """Filtra las ventas por fecha y estado"""
        self.cargar_ventas()
