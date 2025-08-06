import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QDir
from PyQt6.QtGui import QIcon, QAction, QKeySequence

# Import the custom Sidebar component
from src.views.components.sidebar import Sidebar

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.views.categorias.categorias_view import CategoriasView
from src.views.productos.productos_view import ProductosView
# Temporalmente usando vistas simples para debug
from src.views.ventas.ventas_simple import VentasSimpleView
from src.views.reportes.reportes_simple import ReportesSimpleView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Inventario")
        self.setMinimumSize(1024, 768)
        
        # Configurar la interfaz
        self.setup_ui()
        
        # Conectar señales
        self.conectar_senales()
        
        # Mostrar la vista de inicio
        self.stacked_widget.setCurrentIndex(0)
    
    def setup_ui(self):
        """Configura la interfaz principal de la aplicación"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barra de menú
        self.setup_menu_bar()
        
        # Barra de herramientas
        self.setup_toolbar()
        
        # Contenido principal
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Barra lateral
        self.setup_sidebar(content_layout)
        
        # Área de contenido
        content_area = QWidget()
        content_area.setObjectName("contentArea")
        content_area_layout = QVBoxLayout(content_area)
        content_area_layout.setContentsMargins(16, 16, 16, 16)
        
        # Widget apilado para las vistas
        self.stacked_widget = QStackedWidget()
        
        # Vista de inicio
        inicio_widget = QWidget()
        inicio_layout = QVBoxLayout(inicio_widget)
        
        bienvenida_label = QLabel("Bienvenido al Sistema de Inventario")
        bienvenida_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bienvenida_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 50px 0;")
        
        inicio_layout.addStretch()
        inicio_layout.addWidget(bienvenida_label)
        inicio_layout.addStretch()
        
        # Agregar la vista de inicio al widget apilado
        print("Agregando vista de inicio...")  # Debug
        self.stacked_widget.addWidget(inicio_widget)  # Índice 0 - Inicio
        
        # Inicializar las vistas con un widget contenedor
        try:
            # Vista de Categorías
            print("Inicializando vista de categorías...")  # Debug
            categorias_container = QWidget()
            categorias_layout = QVBoxLayout(categorias_container)
            categorias_layout.setContentsMargins(0, 0, 0, 0)
            self.categorias_view = CategoriasView()
            categorias_layout.addWidget(self.categorias_view)
            self.stacked_widget.addWidget(categorias_container)  # Índice 1 - Categorías
            
            # Vista de Productos
            print("Inicializando vista de productos...")  # Debug
            productos_container = QWidget()
            productos_layout = QVBoxLayout(productos_container)
            productos_layout.setContentsMargins(0, 0, 0, 0)
            self.productos_view = ProductosView()
            productos_layout.addWidget(self.productos_view)
            self.stacked_widget.addWidget(productos_container)  # Índice 2 - Productos
            
            # Vista de Ventas (Simple para debug)
            print("Inicializando vista de ventas...")  # Debug
            ventas_container = QWidget()
            ventas_layout = QVBoxLayout(ventas_container)
            ventas_layout.setContentsMargins(0, 0, 0, 0)
            self.ventas_view = VentasSimpleView()
            ventas_layout.addWidget(self.ventas_view)
            self.stacked_widget.addWidget(ventas_container)  # Índice 3 - Ventas
            
            # Vista de Reportes (Simple para debug)
            print("Inicializando vista de reportes...")  # Debug
            reportes_container = QWidget()
            reportes_layout = QVBoxLayout(reportes_container)
            reportes_layout.setContentsMargins(0, 0, 0, 0)
            self.reportes_view = ReportesSimpleView()
            reportes_layout.addWidget(self.reportes_view)
            self.stacked_widget.addWidget(reportes_container)  # Índice 4 - Reportes
            
            print(f"Total de vistas en el stacked widget: {self.stacked_widget.count()}")  # Debug
            
        except Exception as e:
            import traceback
            error_msg = f"Se produjo un error al cargar las vistas: {str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(
                self,
                "Error al cargar las vistas",
                error_msg
            )
        
        content_area_layout.addWidget(self.stacked_widget)
        
        content_layout.addWidget(content_area, 1)
        
        main_layout.addWidget(content_widget, 1)
        
        # Barra de estado
        self.statusBar().showMessage("Listo")
        
        # Aplicar estilos
        self.setup_styles()
    
    def setup_menu_bar(self):
        """Configura la barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        archivo_menu = menubar.addMenu("&Archivo")
        
        salir_action = QAction("&Salir", self)
        salir_action.setShortcut(QKeySequence.StandardKey.Quit)
        salir_action.triggered.connect(self.close)
        archivo_menu.addAction(salir_action)
        
        # Menú Editar
        editar_menu = menubar.addMenu("&Editar")
        
        # Menú Ver
        ver_menu = menubar.addMenu("&Ver")
        ver_categorias = ver_menu.addAction("Categorías")
        ver_categorias.triggered.connect(lambda: self.cambiar_vista(1))
        ver_productos = ver_menu.addAction("Productos")
        ver_productos.triggered.connect(lambda: self.cambiar_vista(2))
        ver_ventas = ver_menu.addAction("Ventas")
        ver_ventas.triggered.connect(lambda: self.cambiar_vista(3))
        ver_reportes = ver_menu.addAction("Reportes")
        ver_reportes.triggered.connect(lambda: self.cambiar_vista(4))
        
        # Menú Ayuda
        ayuda_menu = menubar.addMenu("A&yuda")
        
        acerca_de = ayuda_menu.addAction("Acerca de")
        acerca_de.triggered.connect(self.mostrar_acerca_de)
    
    def setup_toolbar(self):
        """Configura la barra de herramientas"""
        toolbar = self.addToolBar("Herramientas")
        toolbar.setMovable(False)
        
        # Botón de inicio
        btn_inicio = QAction(QIcon(":/icons/home.png"), "Inicio", self)
        btn_inicio.triggered.connect(lambda: self.cambiar_vista(0))
        toolbar.addAction(btn_inicio)
        
        # Separador
        toolbar.addSeparator()
        
        # Botón de categorías
        btn_categorias = QAction(QIcon(":/icons/tag.png"), "Categorías", self)
        btn_categorias.triggered.connect(lambda: self.cambiar_vista(1))
        toolbar.addAction(btn_categorias)
        
        # Botón de productos
        btn_productos = QAction(QIcon(":/icons/package.png"), "Productos", self)
        btn_productos.triggered.connect(lambda: self.cambiar_vista(2))
        toolbar.addAction(btn_productos)
        
        # Botón de ventas
        btn_ventas = QAction(QIcon(":/icons/shopping-cart.png"), "Ventas", self)
        btn_ventas.triggered.connect(lambda: self.cambiar_vista(3))
        toolbar.addAction(btn_ventas)
        
        # Botón de reportes
        btn_reportes = QAction(QIcon(":/icons/bar-chart-2.png"), "Reportes", self)
        btn_reportes.triggered.connect(lambda: self.cambiar_vista(4))
        toolbar.addAction(btn_reportes)
    
    def setup_sidebar(self, parent_layout):
        """Configura la barra lateral"""
        print("MainWindow: Configurando sidebar...")  # Debug
        
        # Create the custom Sidebar component
        self.sidebar = Sidebar()
        self.sidebar.setObjectName("sidebar")
        
        # Connect sidebar buttons directly to view change methods
        print("MainWindow: Conectando botones directamente...")  # Debug
        self.sidebar.btn_inicio.clicked.connect(lambda: self.cambiar_vista(0))
        self.sidebar.btn_categorias.clicked.connect(lambda: self.cambiar_vista(1))
        self.sidebar.btn_productos.clicked.connect(lambda: self.cambiar_vista(2))
        self.sidebar.btn_ventas.clicked.connect(lambda: self.cambiar_vista(3))
        self.sidebar.btn_reportes.clicked.connect(lambda: self.cambiar_vista(4))
        self.sidebar.btn_configuracion.clicked.connect(lambda: self.cambiar_vista(0))
        print("MainWindow: Botones conectados directamente")  # Debug
        
        # Add the sidebar to the parent layout
        parent_layout.addWidget(self.sidebar)
        print("MainWindow: Sidebar agregado al layout")  # Debug
    
    def handle_view_change(self, view_name):
        """Handle view changes from the sidebar"""
        print(f"Cambiando a la vista: {view_name}")  # Debug
        
        # Map view names to their corresponding indices
        view_map = {
            'inicio': 0,
            'categorias': 1,
            'productos': 2,
            'ventas': 3,
            'reportes': 4,
            'configuracion': 0  # Default to home for now
        }
        
        # Change to the appropriate view
        view_index = view_map.get(view_name, 0)  # Default to home if view not found
        print(f"Índice de vista: {view_index}")  # Debug
        self.cambiar_vista(view_index)
    
    def setup_styles(self):
        """Configura los estilos de la aplicación"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            #sidebar {
                background-color: #2c3e50;
                border-right: 1px solid #1a252f;
            }
            
            #sidebar QPushButton {
                color: #ecf0f1;
                text-align: left;
                padding: 12px 16px;
                border: none;
                border-bottom: 1px solid #34495e;
                background: transparent;
            }
            
            #sidebar QPushButton:hover {
                background-color: #34495e;
            }
            
            #sidebar QPushButton:checked {
                background-color: #3498db;
                font-weight: bold;
            }
            
            #contentArea {
                background-color: #ffffff;
            }
            
            QToolBar {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 1px solid #dee2e6;
                padding: 4px;
                spacing: 4px;
            }
            
            QToolButton {
                padding: 6px 12px;
                border: 1px solid transparent;
                border-radius: 4px;
                background: transparent;
            }
            
            QToolButton:hover {
                background-color: #e9ecef;
            }
            
            QToolButton:pressed {
                background-color: #dee2e6;
            }
        """)
    
    def conectar_senales(self):
        """Conecta las señales de las vistas"""
        # Conectar señales de actualización de la vista de categorías
        categorias_view = self.stacked_widget.widget(1)
        if hasattr(categorias_view, 'categoria_guardada'):
            categorias_view.categoria_guardada.connect(self.actualizar_vistas)
        
        # Conectar señales de actualización de la vista de productos
        productos_view = self.stacked_widget.widget(2)
        if hasattr(productos_view, 'producto_guardado'):
            productos_view.producto_guardado.connect(self.actualizar_vistas)
        
        # Conectar señales de actualización de la vista de ventas
        ventas_view = self.stacked_widget.widget(3)
        if hasattr(ventas_view, 'venta_realizada'):
            ventas_view.venta_realizada.connect(self.actualizar_vistas)
    
    def cambiar_vista(self, index):
        """Cambia la vista actual"""
        print(f"Intentando cambiar a la vista con índice: {index}")  # Debug
        
        # Verificar que el índice sea válido
        if index < 0 or index >= self.stacked_widget.count():
            print(f"Índice de vista inválido: {index}")  # Debug
            index = 0  # Volver a la vista de inicio si el índice no es válido
        
        # Cambiar a la vista solicitada
        self.stacked_widget.setCurrentIndex(index)
        print(f"Vista actual: {self.stacked_widget.currentIndex()}")  # Debug
        
        # Actualizar el título de la ventana según la vista actual
        titulos = [
            "Inicio - Sistema de Inventario",
            "Categorías - Sistema de Inventario",
            "Productos - Sistema de Inventario",
            "Ventas - Sistema de Inventario",
            "Reportes - Sistema de Inventario"
        ]
        
        if 0 <= index < len(titulos):
            titulo = titulos[index]
            self.setWindowTitle(titulo)
            print(f"Título actualizado: {titulo}")  # Debug
        
        # Actualizar la barra de estado
        mensaje_estado = f"Vista actualizada: {titulos[index].split(' - ')[0]}"
        self.statusBar().showMessage(mensaje_estado)
        print(f"Mensaje de estado: {mensaje_estado}")  # Debug
    
    def actualizar_vistas(self):
        """Actualiza todas las vistas que necesitan refrescarse"""
        # Actualizar vista de categorías si es necesario
        categorias_view = self.stacked_widget.widget(1)
        if hasattr(categorias_view, 'cargar_categorias'):
            categorias_view.cargar_categorias()
        
        # Actualizar vista de productos
        productos_view = self.stacked_widget.widget(2)
        if hasattr(productos_view, 'cargar_productos'):
            productos_view.cargar_productos()
        
        # Actualizar vista de ventas
        ventas_view = self.stacked_widget.widget(3)
        if hasattr(ventas_view, 'cargar_ventas'):
            ventas_view.cargar_ventas()
        
        # Actualizar vista de reportes si es necesario
        reportes_view = self.stacked_widget.widget(4)
        if hasattr(reportes_view, 'actualizar_reportes'):
            reportes_view.actualizar_reportes()
    
    def mostrar_acerca_de(self):
        """Muestra el diálogo Acerca de"""
        QMessageBox.about(
            self,
            "Acerca de",
            "<h2>Sistema de Inventario</h2>"
            "<p>Versión 1.0.0</p>"
            "<p>Aplicación de gestión de inventario desarrollada con PyQt6.</p>"
            "<p>&copy; 2025 Todos los derechos reservados.</p>"
        )
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la aplicación"""
        reply = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Está seguro de que desea salir de la aplicación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
