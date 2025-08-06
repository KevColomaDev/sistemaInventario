import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QStatusBar, QLabel
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from src.views.components.sidebar import Sidebar
from src.views.productos.productos_view import ProductosView
from src.views.categorias.categorias_view import CategoriasView
from src.views.ventas.ventas_view import VentasView
from src.views.reportes.reportes_view import ReportesView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Inventario")
        self.setMinimumSize(1024, 720)
        
        # Configurar la ventana principal
        self.setup_ui()
        
        # Conectar señales
        self.setup_connections()
        
        # Establecer la vista de inicio
        self.sidebar.btn_inicio.setChecked(True)
        self.stacked_widget.setCurrentIndex(0)
    
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (horizontal)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barra lateral
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(220)
        
        # Área de contenido (stacked widget para cambiar entre vistas)
        self.stacked_widget = QStackedWidget()
        
        # Crear las vistas
        self.setup_views()
        
        # Agregar widgets al layout principal
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget, 1)  # El 1 hace que ocupe el espacio restante
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")
        
        # Configurar estilos
        self.setup_styles()
    
    def setup_views(self):
        """Configura las vistas de la aplicación"""
        # Vista de inicio
        self.inicio_widget = QWidget()
        self.setup_inicio_view()
        
        # Vista de productos
        self.productos_view = ProductosView()
        
        # Vista de categorías
        self.categorias_view = CategoriasView()
        
        # Vista de ventas
        self.ventas_view = VentasView()
        
        # Vista de reportes
        self.reportes_view = ReportesView()
        
        # Vista de configuración
        self.config_widget = QWidget()
        self.setup_config_view()
        
        # Agregar vistas al stacked widget
        self.stacked_widget.addWidget(self.inicio_widget)
        self.stacked_widget.addWidget(self.productos_view)
        self.stacked_widget.addWidget(self.categorias_view)
        self.stacked_widget.addWidget(self.ventas_view)
        self.stacked_widget.addWidget(self.reportes_view)
        self.stacked_widget.addWidget(self.config_widget)
    
    def setup_inicio_view(self):
        """Configura la vista de inicio"""
        layout = QHBoxLayout(self.inicio_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Contenido de ejemplo para la vista de inicio
        welcome_label = QLabel(
            "<h1>Bienvenido al Sistema de Inventario</h1>"
            "<p>Seleccione una opción del menú lateral para comenzar.</p>"
        )
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setWordWrap(True)
        
        layout.addWidget(welcome_label, 1)
    
    def setup_config_view(self):
        """Configura la vista de configuración (placeholder)"""
        layout = QHBoxLayout(self.config_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        
        label = QLabel("<h2>Configuración</h2><p>Configuración de la aplicación.</p>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, 1)
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        # Navegación
        self.sidebar.view_changed.connect(self.cambiar_vista)
        
        # Señales de productos
        self.productos_view.agregar_producto.connect(self.mostrar_dialogo_producto)
        self.productos_view.editar_producto.connect(self.mostrar_dialogo_editar_producto)
        
        # Señales de categorías
        self.categorias_view.agregar_categoria.connect(self.mostrar_dialogo_categoria)
        self.categorias_view.editar_categoria.connect(self.mostrar_dialogo_editar_categoria)
    
    def cambiar_vista(self, nombre_vista):
        """Cambia la vista actual según la selección del menú"""
        vistas = {
            'inicio': 0,
            'productos': 1,
            'categorias': 2,
            'ventas': 3,
            'reportes': 4,
            'configuracion': 0
        }
        
        if nombre_vista in vistas:
            self.stacked_widget.setCurrentIndex(vistas[nombre_vista])
    
    def mostrar_dialogo_producto(self):
        """Muestra el diálogo para agregar un nuevo producto"""
        from src.views.productos.producto_dialog import ProductoDialog
        
        try:
            dialogo = ProductoDialog(parent=self)
            dialogo.setWindowModality(Qt.WindowModality.ApplicationModal)
            dialogo.producto_guardado.connect(self.actualizar_vistas)
            dialogo.exec()
        except Exception as e:
            print(f"Error al mostrar el diálogo de producto: {str(e)}")
    
    def mostrar_dialogo_editar_producto(self, producto_id):
        """Muestra el diálogo para editar un producto existente"""
        from src.views.productos.producto_dialog import ProductoDialog
        
        try:
            dialogo = ProductoDialog(producto_id=producto_id, parent=self)
            dialogo.setWindowModality(Qt.WindowModality.ApplicationModal)
            dialogo.producto_guardado.connect(self.actualizar_vistas)
            dialogo.exec()
        except Exception as e:
            print(f"Error al mostrar el diálogo de edición de producto: {str(e)}")
    
    def mostrar_dialogo_categoria(self):
        """Muestra el diálogo para agregar una nueva categoría"""
        from src.views.categorias.categoria_dialog import CategoriaDialog
        
        try:
            dialogo = CategoriaDialog(parent=self)
            dialogo.setWindowModality(Qt.WindowModality.ApplicationModal)
            dialogo.categoria_guardada.connect(self.actualizar_vistas)
            dialogo.exec()
        except Exception as e:
            print(f"Error al mostrar el diálogo de categoría: {str(e)}")
    
    def mostrar_dialogo_editar_categoria(self, categoria_id):
        """Muestra el diálogo para editar una categoría existente"""
        from src.views.categorias.categoria_dialog import CategoriaDialog
        
        try:
            dialogo = CategoriaDialog(categoria_id=categoria_id, parent=self)
            dialogo.setWindowModality(Qt.WindowModality.ApplicationModal)
            dialogo.categoria_guardada.connect(self.actualizar_vistas)
            dialogo.exec()
        except Exception as e:
            print(f"Error al mostrar el diálogo de edición de categoría: {str(e)}")
    
    def actualizar_vistas(self):
        """Actualiza las vistas que muestran datos"""
        # Actualizar la vista de productos
        if hasattr(self, 'productos_view'):
            self.productos_view.cargar_productos()
        
        # Actualizar la vista de categorías
        if hasattr(self, 'categorias_view'):
            self.categorias_view.cargar_categorias()
    
    def setup_styles(self):
        """Configura los estilos de la ventana principal"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F0E5;
            }
            
            QLabel {
                color: #4A4A4A;
            }
            
            QStatusBar {
                background-color: #EADBC8;
                color: #4A4A4A;
                border-top: 1px solid #DAC0A3;
            }
        """)
