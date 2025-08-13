import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QLineEdit, QMessageBox, QDateEdit, QComboBox, QFormLayout,
    QAbstractItemView, QDialog, QDialogButtonBox, QSpinBox,
    QDoubleSpinBox, QSizePolicy, QFrame
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
        self.precio_unitario = producto.precio if (producto and hasattr(producto, 'precio')) else 0.0
        
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
        
        
        tool_layout.addWidget(self.btn_nueva_venta)
        tool_layout.addStretch()
        tool_layout.addWidget(QLabel("Desde:"))
        tool_layout.addWidget(self.fecha_desde)
        tool_layout.addWidget(QLabel("Hasta:"))
        tool_layout.addWidget(self.fecha_hasta)
        tool_layout.addWidget(QLabel("Buscar:"))
        tool_layout.addWidget(self.buscar_input)
        
        layout.addLayout(tool_layout)
        
        # Tabla de ventas
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(5)
        self.tabla_ventas.setHorizontalHeaderLabels([
            "Código", "Fecha", "Productos", "Total", "Acciones"
        ])
        # Ajuste de columnas (similar a productos/categorías)
        header = self.tabla_ventas.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Código
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Productos (ocupa ancho disponible)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Total
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Acciones
        header.setStretchLastSection(False)
        self.tabla_ventas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_ventas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_ventas.verticalHeader().setVisible(False)
        
        layout.addWidget(self.tabla_ventas)

        # Resumen (pie de página)
        resumen_widget = QFrame()
        resumen_widget.setObjectName("resumenWidget")
        resumen_layout = QHBoxLayout(resumen_widget)

        self.lbl_total_ventas = QLabel("Total de ventas: 0")
        self.lbl_monto_total = QLabel("Monto total: $0.00")

        resumen_layout.addWidget(self.lbl_total_ventas)
        resumen_layout.addStretch()
        resumen_layout.addWidget(self.lbl_monto_total)

        layout.addWidget(resumen_widget)

        # Estilos
        self.setup_styles()
    
    def setup_styles(self):
        """Configura los estilos de la vista"""
        self.setStyleSheet("""
            /* Inputs y combos (paleta similar) */
            QLineEdit, QComboBox, QDateEdit {
                padding: 6px 8px;
                border: 1px solid #DAC0A3;
                border-radius: 4px;
                min-width: 200px;
                background-color: white;
                color: #000;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: #000;
                selection-background-color: #EADBC8;
                selection-color: #000;
            }

            /* Botones */
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

            /* Tabla */
            QTableWidget {
                background-color: white;
                border: 1px solid #DAC0A3;
                border-radius: 4px;
                gridline-color: #EADBC8;
                selection-background-color: #EADBC8;
            }
            QTableWidget::item { color: #000; }
            QLabel { color: #000; }

            QHeaderView::section {
                background-color: #EADBC8;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #000;
            }

            /* Botón de acción en tabla */
            QPushButton#btn_ver {
                color: white;
                background-color: #0078d7; /* como btn_editar */
                border: none;
                padding: 3px 8px;
                border-radius: 4px;
                margin: 1px;
            }
            QPushButton#btn_ver:hover {
                background-color: #106ebe;
            }
        """)
    
    def cargar_ventas(self):
        """Carga las ventas en la tabla"""
        self.tabla_ventas.setRowCount(0)
        
        fecha_desde = self.fecha_desde.date().toPyDate()
        fecha_hasta = self.fecha_hasta.date().toPyDate()
        ventas = Venta.obtener_todas(fecha_desde, fecha_hasta)
        
        for venta in ventas:
            self.agregar_venta_tabla(venta)
        # Actualizar resumen después de cargar
        self.actualizar_resumen()
    
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

        # Productos (lista corta "Nombre x Cant.")
        try:
            venta_completa = Venta.obtener_por_id(venta.id)
            resumen_items = []
            if venta_completa and getattr(venta_completa, 'items', None):
                for it in venta_completa.items:
                    prod = Producto.obtener_por_id(it.producto_id)
                    if prod:
                        resumen_items.append(f"{prod.nombre} x {it.cantidad}")
            # Limitar a 3 elementos y recortar
            max_items = 3
            mostrado = resumen_items[:max_items]
            extra = len(resumen_items) - len(mostrado)
            texto = ", ".join(mostrado)
            if extra > 0:
                texto = f"{texto} +{extra} más"
            productos_item = QTableWidgetItem(texto)
            productos_item.setToolTip("\n".join(resumen_items))
        except Exception:
            productos_item = QTableWidgetItem("")
        self.tabla_ventas.setItem(row, 2, productos_item)
        
        # Total
        total_item = QTableWidgetItem(f"$ {venta.total:.2f}")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_ventas.setItem(row, 3, total_item)
        
        # Acciones
        acciones_widget = QWidget()
        acciones_layout = QHBoxLayout(acciones_widget)
        acciones_layout.setContentsMargins(5, 2, 5, 2)
        acciones_layout.setSpacing(5)
        
        btn_ver = QPushButton("Ver")
        btn_ver.setObjectName("btn_ver")
        btn_ver.clicked.connect(lambda _, v=venta: self.ver_venta(v))
        
        acciones_layout.addWidget(btn_ver)
        
        
        acciones_layout.addStretch()
        self.tabla_ventas.setCellWidget(row, 4, acciones_widget)
    
    def nueva_venta(self):
        """Abre el diálogo para crear una nueva venta"""
        from .venta_dialog import VentaDialog
        dialog = VentaDialog(self)
        dialog.venta_guardada.connect(self.on_venta_guardada)
        dialog.exec()
    
    def on_venta_guardada(self, venta_id):
        """Maneja el evento de venta guardada"""
        self.cargar_ventas()  # Recargar la lista de ventas
        self.venta_realizada.emit()  # Notificar a otras partes de la aplicación
        
        # Mostrar mensaje de éxito
        QMessageBox.information(
            self,
            "Venta guardada",
            "La venta se ha guardado correctamente."
        )
    
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
        # Actualizar resumen considerando filas visibles
        self.actualizar_resumen()
    
    def filtrar_ventas(self):
        """Filtra las ventas por fecha y estado"""
        self.cargar_ventas()

    def actualizar_resumen(self):
        """Actualiza el resumen de ventas en el pie de página"""
        total_ventas_visibles = 0
        monto_total = 0.0

        for row in range(self.tabla_ventas.rowCount()):
            if self.tabla_ventas.isRowHidden(row):
                continue
            total_ventas_visibles += 1
            total_text = self.tabla_ventas.item(row, 3)
            if total_text:
                valor = total_text.text().replace('$', '').replace(',', '').strip()
                try:
                    monto_total += float(valor)
                except ValueError:
                    pass

        self.lbl_total_ventas.setText(f"Total de ventas: {total_ventas_visibles}")
        self.lbl_monto_total.setText(f"Monto total: ${monto_total:,.2f}")
