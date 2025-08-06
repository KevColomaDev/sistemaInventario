from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy, QStyle
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon

from src.views.components.nav_button import NavButton

class Sidebar(QWidget):
    # Señales para cambiar de vista
    view_changed = pyqtSignal(str)  # 'inicio', 'productos', 'categorias', 'configuracion'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """Configura la interfaz de usuario de la barra lateral"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(8)
        
        # Logo y título
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setPixmap(QPixmap(":/icons/logo.png").scaled(120, 120, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation))
        
        self.title_label = QLabel("Sistema de Inventario")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("appTitle")
        
        # Línea separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("separator")
        
        # Botones de navegación con iconos del sistema como respaldo
        style = self.style()
        
        # Inicio
        home_icon = QIcon.fromTheme("go-home", style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.btn_inicio = NavButton("Inicio", "")
        self.btn_inicio.setIcon(home_icon)
        
        # Productos
        product_icon = QIcon.fromTheme("package-x-generic", style.standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.btn_productos = NavButton("Productos", "")
        self.btn_productos.setIcon(product_icon)
        
        # Categorías
        category_icon = QIcon.fromTheme("tag", style.standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        self.btn_categorias = NavButton("Categorías", "")
        self.btn_categorias.setIcon(category_icon)
        
        # Ventas
        sales_icon = QIcon.fromTheme("shopping-cart", style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.btn_ventas = NavButton("Ventas", "")
        self.btn_ventas.setIcon(sales_icon)
        
        
        # Configuración
        settings_icon = QIcon.fromTheme("preferences-system", style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.btn_configuracion = NavButton("Configuración", "")
        self.btn_configuracion.setIcon(settings_icon)
        
        # Conectar señales con los nombres de vista correctos
        self.btn_inicio.clicked.connect(lambda: self.emit_view_changed('inicio'))
        self.btn_productos.clicked.connect(lambda: self.emit_view_changed('productos'))
        self.btn_categorias.clicked.connect(lambda: self.emit_view_changed('categorias'))
        self.btn_ventas.clicked.connect(lambda: self.emit_view_changed('ventas'))
        self.btn_configuracion.clicked.connect(lambda: self.emit_view_changed('inicio'))  # Configuración va a inicio por ahora
        
        print("Sidebar: Señales de botones conectadas")  # Debug
        
        # Espaciador para empujar el botón de configuración hacia abajo
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Agregar widgets al layout
        layout.addWidget(self.logo_label)
        layout.addWidget(self.title_label)
        layout.addWidget(separator)
        layout.addWidget(self.btn_inicio)
        layout.addWidget(self.btn_productos)
        layout.addWidget(self.btn_categorias)
        layout.addWidget(self.btn_ventas)
        layout.addSpacing(16)
        layout.addWidget(separator)
        layout.addWidget(spacer)
        layout.addWidget(self.btn_configuracion)
        
        # Seleccionar la vista de inicio por defecto
        self.btn_inicio.setChecked(True)
    
    def setup_styles(self):
        """Configura los estilos de la barra lateral"""
        self.setStyleSheet("""
            QWidget {
                background-color: #EADBC8;
            }
            
            #appTitle {
                color: #4A4A4A;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 0;
                margin-bottom: 8px;
            }
            
            #separator {
                border: 1px solid #DAC0A3;
                margin: 8px 0;
            }
        """)
    
    def emit_view_changed(self, view_name):
        """Emite la señal cuando se cambia la vista"""
        print(f"Sidebar: Emitiendo señal para vista '{view_name}'")
        self.view_changed.emit(view_name)
        print(f"Sidebar: Señal emitida para vista '{view_name}'")
