from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class VentasSimpleView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("MÓDULO DE VENTAS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px;
        """)
        
        subtitle = QLabel("Vista de Ventas Funcionando Correctamente")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 18px;
            color: #34495e;
            margin: 10px;
        """)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
