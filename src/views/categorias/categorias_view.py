from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from src.models.categoria import Categoria

class CategoriasView(QWidget):
    # Señales
    agregar_categoria = pyqtSignal()
    editar_categoria = pyqtSignal(int)  # ID de la categoría
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.cargar_categorias()
    
    def setup_ui(self):
        """Configura la interfaz de usuario de la vista de categorías"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Barra de búsqueda y acciones
        search_layout = QHBoxLayout()
        
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar categorías...")
        self.buscar_input.textChanged.connect(self.buscar_categorias)
        
        btn_agregar = QPushButton("Nueva Categoría")
        btn_agregar.setIcon(QIcon(":/icons/tag.png"))
        btn_agregar.clicked.connect(self.agregar_categoria)
        
        search_layout.addWidget(QLabel("Buscar:"))
        search_layout.addWidget(self.buscar_input)
        search_layout.addWidget(btn_agregar)
        
        # Tabla de categorías
        self.tabla_categorias = QTableWidget()
        self.tabla_categorias.setColumnCount(4)
        self.tabla_categorias.setHorizontalHeaderLabels([
            "Nombre", "Descripción", "Productos", "Acciones"
        ])
        
        # Estilo para la tabla
        self.tabla_categorias.setStyleSheet("""
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
        layout.addWidget(legend)
        
        # Ajustar el ancho de las columnas
        header = self.tabla_categorias.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Nombre
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Descripción
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Productos
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Acciones
        
        self.tabla_categorias.verticalHeader().setVisible(False)
        self.tabla_categorias.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Widget de resumen
        resumen_widget = QFrame()
        resumen_widget.setObjectName("resumenWidget")
        resumen_layout = QHBoxLayout(resumen_widget)
        
        self.lbl_total_categorias = QLabel("Total de categorías: 0")
        self.lbl_categorias_sin_productos = QLabel("Categorías sin productos: 0")
        
        resumen_layout.addWidget(self.lbl_total_categorias)
        resumen_layout.addStretch()
        resumen_layout.addWidget(self.lbl_categorias_sin_productos)
        
        # Agregar widgets al layout principal
        layout.addLayout(search_layout)
        layout.addWidget(self.tabla_categorias)
        layout.addWidget(resumen_widget)
        
        # Configurar estilos
        self.setup_styles()
    
    def setup_styles(self):
        """Configura los estilos de la vista de categorías"""
        self.setStyleSheet("""
            QLineEdit {
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
    
    def cargar_categorias(self, categorias=None):
        """Carga las categorías en la tabla"""
        if categorias is None:
            categorias = Categoria.obtener_todas()
        
        self.tabla_categorias.setRowCount(0)
        categorias_sin_productos = 0
        
        for categoria in categorias:
            # Obtener el número de productos en esta categoría
            from src.models.producto import Producto
            productos = Producto.obtener_todos(categoria.id)
            num_productos = len(productos)
            
            if num_productos == 0:
                categorias_sin_productos += 1
            
            row = self.tabla_categorias.rowCount()
            self.tabla_categorias.insertRow(row)
            
            # Nombre
            self.tabla_categorias.setItem(row, 0, QTableWidgetItem(categoria.nombre))
            
            # Descripción
            desc_item = QTableWidgetItem(categoria.descripcion or "")
            desc_item.setToolTip(categoria.descripcion or "")
            self.tabla_categorias.setItem(row, 1, desc_item)
            
            # Número de productos
            productos_item = QTableWidgetItem(str(num_productos))
            productos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_categorias.setItem(row, 2, productos_item)
            
            # Botones de acción
            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout(acciones_widget)
            acciones_layout.setContentsMargins(5, 2, 5, 2)
            acciones_layout.setSpacing(5)
            
            btn_editar = QPushButton()
            btn_editar.setObjectName("btn_editar")
            btn_editar.setIcon(QIcon(":/icons/edit.png"))
            btn_editar.setToolTip("Editar categoría")
            btn_editar.setFixedSize(28, 28)
            btn_editar.setStyleSheet("")
            btn_editar.clicked.connect(lambda _, c=categoria: self.editar_categoria.emit(c.id))
            
            btn_eliminar = QPushButton()
            btn_eliminar.setObjectName("btn_eliminar")
            btn_eliminar.setIcon(QIcon(":/icons/trash-2.png"))
            btn_eliminar.setToolTip("Eliminar categoría")
            btn_eliminar.setFixedSize(28, 28)
            btn_eliminar.setStyleSheet("")
            btn_eliminar.clicked.connect(lambda _, c=categoria: self.eliminar_categoria(c))
            
            # Deshabilitar botón de eliminar si la categoría tiene productos
            if num_productos > 0:
                btn_eliminar.setEnabled(False)
                btn_eliminar.setToolTip("No se puede eliminar una categoría con productos")
            
            acciones_layout.addWidget(btn_editar)
            acciones_layout.addWidget(btn_eliminar)
            acciones_layout.addStretch()
            
            self.tabla_categorias.setCellWidget(row, 3, acciones_widget)
        
        # Actualizar resumen
        self.actualizar_resumen(len(categorias), categorias_sin_productos)
    
    def buscar_categorias(self):
        """Busca categorías según el texto de búsqueda"""
        texto_busqueda = self.buscar_input.text().strip()
        
        if texto_busqueda:
            categorias = Categoria.buscar_por_nombre(texto_busqueda)
            self.cargar_categorias(categorias)
        else:
            self.cargar_categorias()
    
    def actualizar_resumen(self, total_categorias, categorias_sin_productos):
        """Actualiza el resumen de categorías"""
        self.lbl_total_categorias.setText(f"Total de categorías: {total_categorias}")
        self.lbl_categorias_sin_productos.setText(f"Categorías sin productos: {categorias_sin_productos}")
    
    def eliminar_categoria(self, categoria):
        """Muestra un diálogo de confirmación para eliminar una categoría"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar la categoría '{categoria.nombre}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                if categoria.eliminar():
                    QMessageBox.information(
                        self,
                        "Categoría eliminada",
                        f"La categoría '{categoria.nombre}' ha sido eliminada correctamente."
                    )
                    self.cargar_categorias()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error al eliminar",
                    f"No se pudo eliminar la categoría: {str(e)}"
                )
